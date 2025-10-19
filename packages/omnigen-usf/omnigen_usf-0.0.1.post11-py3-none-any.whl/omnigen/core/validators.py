"""
Comprehensive validation for conversations and data structures.

Uses Pydantic for schema validation with comprehensive error handling.
Pydantic is REQUIRED for production use.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from omnigen.utils.logger import setup_logger

# Pydantic is REQUIRED for production - fail if not available
try:
    from pydantic import BaseModel, validator, Field
    from pydantic import ValidationError as PydanticValidationError
except ImportError as e:
    raise ImportError(
        "Pydantic is required for OmniGen. Install with: pip install pydantic>=2.0.0"
    ) from e

logger = setup_logger()


class Message(BaseModel):
    """Message schema with validation."""
    role: str = Field(..., description="Message role")
    content: Optional[str] = Field(None, description="Message content")
    tool_calls: Optional[list] = Field(None, description="Tool calls (for assistant messages)")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role is valid."""
        try:
            if v not in ['system', 'user', 'assistant', 'tool']:
                raise ValueError(f"Invalid role: {v}. Must be system, user, assistant, or tool")
            return v
        except Exception as e:
            logger.error(f"Role validation error: {e}")
            raise
    
    @validator('content')
    def validate_content(cls, v, values):
        """Validate content is not empty unless tool_calls exist."""
        try:
            # Get role and tool_calls from values
            role = values.get('role')
            
            # Content can be None or empty only for assistant messages with tool_calls
            if not v or not str(v).strip():
                # For assistant messages, check if tool_calls exist
                # Note: tool_calls will be validated separately
                if role == 'assistant':
                    # Will be validated in root_validator to check tool_calls
                    return v if v is not None else ""
                else:
                    # For user/system/tool roles, content is required
                    raise ValueError(f"Content cannot be empty for {role} messages")
            
            # Validate length if content exists
            if v and len(v) > 100000:  # 100K character limit
                raise ValueError(f"Content too long: {len(v)} chars (max 100000)")
            
            return v.strip() if v else ""
        except Exception as e:
            logger.error(f"Content validation error: {e}")
            raise
    
    @validator('tool_calls')
    def validate_tool_calls(cls, v, values):
        """Validate tool_calls if present."""
        try:
            if v is not None:
                role = values.get('role')
                # Only assistant messages can have tool_calls
                if role != 'assistant':
                    raise ValueError(f"Only assistant messages can have tool_calls, not {role}")
                
                # Validate it's a list
                if not isinstance(v, list):
                    raise ValueError("tool_calls must be a list")
                
                # Validate not empty if present
                if len(v) == 0:
                    raise ValueError("tool_calls cannot be an empty list")
            
            return v
        except Exception as e:
            logger.error(f"Tool calls validation error: {e}")
            raise
    
    class Config:
        """Pydantic config."""
        validate_assignment = True
        
    def __init__(self, **data):
        """Custom init to validate content/tool_calls relationship."""
        super().__init__(**data)
        
        # Final validation: assistant messages must have either content or tool_calls
        if self.role == 'assistant':
            has_content = self.content and str(self.content).strip()
            has_tool_calls = self.tool_calls and len(self.tool_calls) > 0
            
            if not has_content and not has_tool_calls:
                raise ValueError(
                    "Assistant messages must have either non-empty content or tool_calls"
                )


class Conversation(BaseModel):
    """Conversation schema with validation."""
    conversations: List[Message] = Field(..., description="List of conversation messages")
    
    @validator('conversations')
    def validate_conversations(cls, v):
        """Validate conversation structure."""
        try:
            if not v:
                raise ValueError("Conversations list cannot be empty")
            
            # First non-system message must be from user
            first_non_system = next((m for m in v if m.role != 'system'), None)
            if not first_non_system:
                raise ValueError("No non-system messages found")
            if first_non_system.role != 'user':
                raise ValueError("First non-system message must be from user")
            
            return v
        except Exception as e:
            logger.error(f"Conversation validation error: {e}")
            raise


class ConversationValidator:
    """
    Comprehensive conversation validator.
    
    Validates:
    - JSON structure
    - Message format
    - Content quality
    - Conversation flow
    - Comprehensive error handling
    """
    
    @staticmethod
    def validate_jsonl_line(line: str, line_num: int) -> Optional[Dict]:
        """
        Validate a single JSONL line with comprehensive error handling.
        
        Args:
            line: JSONL line
            line_num: Line number for error reporting
            
        Returns:
            Parsed conversation dict or None if invalid
        """
        try:
            # Parse JSON
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"Line {line_num}: Invalid JSON - {e}")
                return None
            
            # Validate structure
            try:
                if not isinstance(data, dict):
                    logger.warning(f"Line {line_num}: Data must be a JSON object")
                    return None
                
                if 'conversations' not in data:
                    logger.warning(f"Line {line_num}: Missing 'conversations' field")
                    return None
            except Exception as e:
                logger.error(f"Line {line_num}: Structure validation error - {e}")
                return None
            
            # Validate using Pydantic (required)
            try:
                conversation = Conversation(**data)
                return data
            except PydanticValidationError as e:
                logger.warning(f"Line {line_num}: Pydantic validation failed - {e}")
                return None
            except Exception as e:
                logger.error(f"Line {line_num}: Validation error - {e}")
                return None
                    
        except Exception as e:
            logger.error(f"Line {line_num}: Unexpected validation error - {e}", exc_info=True)
            return None
    
    @staticmethod
    def validate_output_quality(conversation: List[Dict]) -> Tuple[bool, Optional[str]]:
        """
        Validate generated conversation quality.
        
        Args:
            conversation: List of conversation messages
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            if not conversation:
                return False, "Empty conversation"
            
            # Check each message for empty content (unless it has tool_calls)
            try:
                for i, msg in enumerate(conversation):
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    tool_calls = msg.get('tool_calls')
                    
                    # For assistant messages, either content or tool_calls must exist
                    if role == 'assistant':
                        has_content = content and str(content).strip()
                        has_tool_calls = tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0
                        
                        if not has_content and not has_tool_calls:
                            return False, f"Message {i} (assistant): empty content without tool_calls"
                    else:
                        # For user/system/tool messages, content is required
                        if not content or not str(content).strip():
                            return False, f"Message {i} ({role}): empty content"
            except Exception as e:
                logger.warning(f"Error checking empty content: {e}")
            
            # Check for repetition
            try:
                contents = [m.get('content', '') for m in conversation if m.get('content')]
                if len(contents) > 0 and len(contents) != len(set(contents)):
                    return False, "Repeated messages detected"
            except Exception as e:
                logger.warning(f"Error checking repetition: {e}")
            
            # Check for very short responses (but allow if tool_calls exist)
            try:
                for i, msg in enumerate(conversation):
                    content = msg.get('content', '')
                    tool_calls = msg.get('tool_calls')
                    
                    # Skip length check if message has tool_calls
                    if tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0:
                        continue
                    
                    if content and len(content.strip()) < 5:
                        return False, f"Message {i} too short (less than 5 chars)"
            except Exception as e:
                logger.warning(f"Error checking message length: {e}")
            
            # Check for proper alternation (user/assistant)
            try:
                last_role = None
                for msg in conversation:
                    role = msg.get('role')
                    if role == last_role and role != 'system':
                        return False, "Messages not properly alternating"
                    last_role = role
            except Exception as e:
                logger.warning(f"Error checking alternation: {e}")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error in validate_output_quality: {e}", exc_info=True)
            # On error, assume valid (don't block generation)
            return True, None
    
    @staticmethod
    def validate_conversation_structure(conversations: List[Dict]) -> Tuple[bool, Optional[str]]:
        """
        Validate basic conversation structure.
        
        Args:
            conversations: List of conversation messages
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            if not conversations:
                return False, "Empty conversations list"
            
            # Check each message has role and content
            try:
                for i, msg in enumerate(conversations):
                    if not isinstance(msg, dict):
                        return False, f"Message {i} is not a dict"
                    if 'role' not in msg:
                        return False, f"Message {i} missing role"
                    if 'content' not in msg:
                        return False, f"Message {i} missing content"
            except Exception as e:
                logger.error(f"Error validating message structure: {e}")
                return False, f"Structure validation error: {e}"
            
            # Check first non-system is user
            try:
                first_non_system = next((m for m in conversations if m.get('role') != 'system'), None)
                if not first_non_system:
                    return False, "No non-system messages found"
                if first_non_system.get('role') != 'user':
                    return False, "First non-system message must be from user"
            except Exception as e:
                logger.error(f"Error checking first message: {e}")
                return False, f"First message validation error: {e}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error in validate_conversation_structure: {e}", exc_info=True)
            return False, f"Unexpected validation error: {e}"