"""Conversation generator with production-grade error handling and validation."""

import random
import re
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfig
from omnigen.pipelines.conversation_extension.prompts import get_default_prompts
from omnigen.core.provider_helper import ProviderHelper
from omnigen.core.error_handler import ErrorHandler
from omnigen.core.validators import ConversationValidator
from omnigen.storage.incremental_saver import IncrementalSaver
from omnigen.utils.datetime_gen import DateTimeGenerator
from omnigen.utils.rate_limiter import RateLimiter
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class ConversationGenerator:
    """
    Production-grade conversation generator with comprehensive error handling.
    
    Features:
    - Fail-fast error handling with ErrorHandler
    - Quality validation with ConversationValidator
    - Incremental saving with IncrementalSaver
    - Automatic retry on transient errors
    - Partial progress preservation
    """
    
    def __init__(
        self,
        config: ConversationExtensionConfig,
        rate_limiter: RateLimiter,
        error_handler: Optional[ErrorHandler] = None,
        incremental_saver: Optional[IncrementalSaver] = None
    ):
        """
        Initialize generator with production components.
        
        Args:
            config: Pipeline configuration
            rate_limiter: Rate limiter for API calls
            error_handler: Optional error handler (created if not provided)
            incremental_saver: Optional incremental saver for partial progress
        """
        self.config = config
        self.rate_limiter = rate_limiter
        self.error_handler = error_handler
        self.incremental_saver = incremental_saver
        self.workspace_id = config.get('workspace_id', 'default')
        
        # Token tracking
        self.track_tokens = config.get('generation.track_tokens', True)
        
        # Get provider configs for each role (defaults already applied in config)
        self.user_config = config.get_provider_config('user_followup')
        self.assistant_config = config.get_provider_config('assistant_response')
        
        # Get providers using ProviderHelper (defaults already applied, use_defaults=False)
        self.user_provider = ProviderHelper.get_provider(
            role='user_followup',
            config=self.user_config,
            use_defaults=False  # Defaults already applied in config
        )
        
        self.assistant_provider = ProviderHelper.get_provider(
            role='assistant_response',
            config=self.assistant_config,
            use_defaults=False  # Defaults already applied in config
        )
        
        self.datetime_gen = DateTimeGenerator(config)
        
        # Load default prompts and merge with custom prompts
        self.prompts = get_default_prompts()
        custom_prompts = config.get('prompts', {})
        if custom_prompts:
            self.prompts.update(custom_prompts)
        
        self.system_config = config.get('system_messages', {})
        self.generation_system_config = config.get('generation_system_messages', {})
        
        # Error handling config
        self.max_retries = config.get('error_handling.max_retries', 3)
        self.save_partial_on_error = config.get('error_handling.save_partial_on_error', True)
        
        logger.info(f"Initialized production generator for workspace: {self.workspace_id}")
    
    def generate_conversation(
        self,
        base_conv: Dict,
        conv_id: int,
        partial_state: Dict = None
    ) -> Dict:
        """
        Generate conversation with production error handling and validation.
        
        Args:
            base_conv: Dict with 'conversations', 'last_role', 'is_valid', '_position', '_content_hash'
            conv_id: Conversation ID
            partial_state: Optional partial conversation state to resume from
            
        Returns:
            Dict with generated conversation and metadata
        """
        extension_mode = self.config.get('generation.extension_mode', 'legacy')
        skip_invalid = self.config.get('generation.skip_invalid', True)
        
        # Check if valid
        if not base_conv.get('is_valid', False):
            if skip_invalid:
                return {
                    'id': conv_id,
                    'error': 'Invalid conversation format',
                    'conversations': [],
                    'success': False,
                    'skipped': True,
                    'generated_at': datetime.utcnow().isoformat(),
                    '_position': base_conv.get('_position', -1),
                    '_content_hash': base_conv.get('_content_hash', '')
                }
        
        conversation_datetime = self.datetime_gen.generate()
        
        # Use smart or legacy mode
        if extension_mode == 'smart':
            return self._generate_smart(base_conv, conv_id, conversation_datetime, partial_state)
        else:
            # Legacy mode: extract first user message
            base_question = ''
            if base_conv.get('conversations'):
                first_user = next((m for m in base_conv['conversations'] if m.get('role') == 'user'), None)
                if first_user:
                    base_question = first_user.get('content', '')
            
            return self._generate_legacy(base_question, conv_id, conversation_datetime, partial_state)
    
    def _generate_smart(
        self,
        base_conv: Dict,
        conv_id: int,
        conversation_datetime: str,
        partial_state: Dict = None
    ) -> Dict:
        """Generate conversation using smart extension mode with error handling."""
        conversation = []
        target_turns = 0
        
        # Token tracking
        token_usage_per_call = []
        total_input_tokens = 0
        total_output_tokens = 0
        
        try:
            # Resume from partial state if available
            if partial_state:
                conversation = partial_state.get('conversation', []).copy()
                turns_completed = partial_state.get('turns_completed', 0)
                last_role = partial_state.get('last_role', 'assistant')
            else:
                conversation = base_conv['conversations'].copy()
                last_role = base_conv.get('last_role', 'other')
                turns_completed = sum(1 for m in conversation if m.get('role') == 'user')
            
            # Handle based on last role
            if last_role == 'user':
                # Add 1 assistant response
                assistant_msg, usage = self._generate_response(conversation, conversation_datetime)
                conversation.append({'role': 'assistant', 'content': assistant_msg})
                if usage:
                    token_usage_per_call.append({'type': 'assistant_response', **usage})
                    total_input_tokens += usage.get('input_tokens', 0)
                    total_output_tokens += usage.get('output_tokens', 0)
            
            elif last_role == 'assistant':
                # Add user followup
                user_msg, usage = self._generate_followup(conversation)
                conversation.append({'role': 'user', 'content': user_msg})
                if usage:
                    token_usage_per_call.append({'type': 'user_followup', **usage})
                    total_input_tokens += usage.get('input_tokens', 0)
                    total_output_tokens += usage.get('output_tokens', 0)
                
                # Add assistant response
                assistant_msg, usage = self._generate_response(conversation, conversation_datetime)
                conversation.append({'role': 'assistant', 'content': assistant_msg})
                if usage:
                    token_usage_per_call.append({'type': 'assistant_response', **usage})
                    total_input_tokens += usage.get('input_tokens', 0)
                    total_output_tokens += usage.get('output_tokens', 0)
            
            # Calculate additional turns to generate
            turn_range = self.config.get('generation.turn_range', {'min': 3, 'max': 8})
            turn_calculation = self.config.get('generation.turn_calculation', 'additional')
            
            current_turns = sum(1 for m in conversation if m.get('role') == 'user')
            
            # If resuming, we've already started - continue to target
            if partial_state:
                target_turns = partial_state.get('target_turns', turn_range['max'])
                additional_turns = max(0, target_turns - current_turns)
            else:
                # Calculate target for new generation
                if turn_calculation == 'total':
                    # Total mode: total turns should be within range (but never remove existing)
                    if current_turns < turn_range['min']:
                        target_turns = turn_range['min']
                    elif current_turns >= turn_range['max']:
                        target_turns = current_turns  # Keep as is, don't remove
                    else:
                        target_turns = random.randint(current_turns, turn_range['max'])
                    additional_turns = target_turns - current_turns
                else:
                    # Additional mode (default): add NEW turns on top of existing
                    additional_turns = random.randint(turn_range['min'], turn_range['max'])
                    target_turns = current_turns + additional_turns
            
            # Generate additional turns with error handling
            for turn_idx in range(additional_turns):
                try:
                    # User followup
                    user_msg, usage = self._generate_followup(conversation)
                    conversation.append({'role': 'user', 'content': user_msg})
                    if usage:
                        token_usage_per_call.append({'type': 'user_followup', **usage})
                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                    
                    # Assistant response
                    assistant_msg, usage = self._generate_response(conversation, conversation_datetime)
                    conversation.append({'role': 'assistant', 'content': assistant_msg})
                    if usage:
                        token_usage_per_call.append({'type': 'assistant_response', **usage})
                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                    
                except Exception as turn_error:
                    # Handle error during turn generation
                    if self.error_handler:
                        error_response = self.error_handler.handle_error(
                            turn_error,
                            base_conv,
                            attempt=1,
                            context={'turn': turn_idx, 'conversation_id': conv_id}
                        )
                        
                        if error_response['action'] == 'abort_job':
                            raise turn_error
                        elif error_response['action'] == 'skip':
                            # Save partial progress if enabled
                            if self.save_partial_on_error and self.incremental_saver:
                                self._save_partial_progress(conv_id, conversation, target_turns, str(turn_error))
                            break
                        elif error_response['action'] == 'retry':
                            # Wait and retry will be handled by runner
                            raise turn_error
                    else:
                        raise turn_error
            
            # Apply system messages
            final_conversation = self._apply_system_messages(conversation, conversation_datetime)
            
            # Validate output quality
            is_valid, validation_error = ConversationValidator.validate_output_quality(final_conversation)
            if not is_valid:
                logger.warning(f"Conversation {conv_id} quality validation failed: {validation_error}")
                # Continue anyway - don't fail on quality issues
            
            result = {
                'id': conv_id,
                'conversations': final_conversation,
                'num_turns': sum(1 for m in final_conversation if m.get('role') == 'user'),
                'num_messages': len(final_conversation),
                'ends_with': final_conversation[-1]['role'] if final_conversation else 'none',
                'success': True,
                'is_complete': True,
                'generated_at': datetime.utcnow().isoformat(),
                '_position': base_conv.get('_position', -1),
                '_content_hash': base_conv.get('_content_hash', ''),
                '_target_turns': target_turns,
                'validation_passed': is_valid
            }
            
            # Add token tracking data if available (NO COST in output file)
            if token_usage_per_call:
                total_tokens = total_input_tokens + total_output_tokens
                result['tokens'] = {
                    'input_tokens': total_input_tokens,
                    'output_tokens': total_output_tokens,
                    'total_tokens': total_tokens,
                    'per_generation': token_usage_per_call
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Conversation {conv_id} failed: {e}")
            
            # Save partial progress if enabled
            if self.save_partial_on_error and self.incremental_saver and conversation:
                self._save_partial_progress(conv_id, conversation, target_turns, str(e))
            
            return {
                'id': conv_id,
                'error': str(e),
                'conversations': conversation if conversation else base_conv.get('conversations', []),
                'success': False,
                'is_partial': True,
                'generated_at': datetime.utcnow().isoformat(),
                '_position': base_conv.get('_position', -1),
                '_content_hash': base_conv.get('_content_hash', ''),
                'num_turns': sum(1 for m in conversation if m.get('role') == 'user') if conversation else 0
            }
    
    def _generate_legacy(
        self,
        base_question: str,
        conv_id: int,
        conversation_datetime: str,
        partial_state: Dict = None
    ) -> Dict:
        """Generate conversation using legacy mode with error handling."""
        turn_range = self.config.get('generation.turn_range', {'min': 3, 'max': 8})
        conversation = []
        
        # Token tracking
        token_usage_per_call = []
        total_input_tokens = 0
        total_output_tokens = 0
        
        # Resume from partial state if available
        if partial_state:
            conversation = partial_state.get('conversation', []).copy()
            turns_completed = partial_state.get('turns_completed', 0)
            num_turns = partial_state.get('target_turns', turn_range['max'])
        else:
            conversation = []
            turns_completed = 0
            num_turns = random.randint(turn_range['min'], turn_range['max'])
        
        try:
            for turn in range(turns_completed, num_turns):
                try:
                    # User message
                    if turn == 0:
                        user_msg = base_question
                        conversation.append({'role': 'user', 'content': user_msg})
                    else:
                        user_msg, usage = self._generate_followup(conversation)
                        conversation.append({'role': 'user', 'content': user_msg})
                        if usage:
                            token_usage_per_call.append({'type': 'user_followup', **usage})
                            total_input_tokens += usage.get('input_tokens', 0)
                            total_output_tokens += usage.get('output_tokens', 0)
                    
                    # Assistant message
                    assistant_msg, usage = self._generate_response(conversation, conversation_datetime)
                    conversation.append({'role': 'assistant', 'content': assistant_msg})
                    if usage:
                        token_usage_per_call.append({'type': 'assistant_response', **usage})
                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                    
                except Exception as turn_error:
                    # Handle error during turn generation
                    if self.error_handler:
                        error_response = self.error_handler.handle_error(
                            turn_error,
                            {'_position': -1},
                            attempt=1,
                            context={'turn': turn, 'conversation_id': conv_id}
                        )
                        
                        if error_response['action'] == 'abort_job':
                            raise turn_error
                        elif error_response['action'] == 'skip':
                            # Save partial progress if enabled
                            if self.save_partial_on_error and self.incremental_saver:
                                self._save_partial_progress(conv_id, conversation, num_turns, str(turn_error))
                            break
                    else:
                        raise turn_error
            
            # Apply system messages
            final_conversation = self._apply_system_messages(conversation, conversation_datetime)
            
            # Validate output quality
            is_valid, validation_error = ConversationValidator.validate_output_quality(final_conversation)
            if not is_valid:
                logger.warning(f"Conversation {conv_id} quality validation failed: {validation_error}")
            
            result = {
                'id': conv_id,
                'conversations': final_conversation,
                'num_turns': num_turns,
                'num_messages': len(final_conversation),
                'ends_with': final_conversation[-1]['role'] if final_conversation else 'none',
                'success': True,
                'is_complete': True,
                'generated_at': datetime.utcnow().isoformat(),
                '_target_turns': num_turns,
                'validation_passed': is_valid
            }
            
            # Add token tracking data if available (NO COST in output file)
            if token_usage_per_call:
                total_tokens = total_input_tokens + total_output_tokens
                result['tokens'] = {
                    'input_tokens': total_input_tokens,
                    'output_tokens': total_output_tokens,
                    'total_tokens': total_tokens,
                    'per_generation': token_usage_per_call
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Conversation {conv_id} failed: {e}")
            
            # Save partial progress if enabled
            if self.save_partial_on_error and self.incremental_saver and conversation:
                self._save_partial_progress(conv_id, conversation, num_turns, str(e))
            
            return {
                'id': conv_id,
                'error': str(e),
                'conversations': conversation,
                'success': False,
                'is_partial': True,
                'generated_at': datetime.utcnow().isoformat(),
                'num_turns': sum(1 for m in conversation if m.get('role') == 'user') if conversation else 0
            }
    
    def _save_partial_progress(
        self,
        conv_id: int,
        conversation: List[Dict],
        target_turns: int,
        error: str
    ):
        """Save partial progress using IncrementalSaver."""
        try:
            if self.incremental_saver:
                turns_completed = sum(1 for m in conversation if m.get('role') == 'user')
                self.incremental_saver.save_partial_progress(
                    conversation_id=conv_id,
                    partial_conversation=conversation,
                    turns_completed=turns_completed,
                    target_turns=target_turns,
                    error=error
                )
                logger.info(f"Saved partial progress for conversation {conv_id}: {turns_completed}/{target_turns} turns")
        except Exception as e:
            logger.error(f"Failed to save partial progress: {e}")
    
    def _generate_followup(self, conversation: List[Dict], track_tokens: bool = True) -> tuple:
        """
        Generate follow-up question using user_followup provider.
        
        Returns:
            tuple: (generated_text, usage_dict) if track_tokens else (generated_text, {})
        """
        history = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in conversation])
        prompt = self.prompts['followup_question'].format(history=history)
        
        messages = [
            {"role": "system", "content": "You are generating natural follow-up questions."},
            {"role": "user", "content": prompt}
        ]
        
        # Enforce rate limiting BEFORE API call
        self.rate_limiter.acquire(timeout=120)
        
        # Call with token tracking if enabled
        if track_tokens and self.track_tokens:
            response, usage = self.user_provider.chat_completion(
                messages,
                temperature=self.user_config.get('temperature', 0.7),
                max_tokens=self.user_config.get('max_tokens', 2048),
                return_usage=True
            )
        else:
            response = self.user_provider.chat_completion(
                messages,
                temperature=self.user_config.get('temperature', 0.7),
                max_tokens=self.user_config.get('max_tokens', 2048)
            )
            usage = {}
        
        # Record successful request for tracking
        self.rate_limiter.record_request()
        
        result = self._extract_from_tags(response, 'user')
        
        # Validate generated content is not empty
        if not result or not result.strip():
            raise ValueError("LLM generated empty user followup question")
        
        return result, usage
    
    def _generate_response(self, conversation: List[Dict], datetime_str: str, track_tokens: bool = True) -> tuple:
        """
        Generate assistant response using assistant_response provider.
        
        Returns:
            tuple: (generated_text, usage_dict) if track_tokens else (generated_text, {})
        """
        # Apply dataset system messages (these WILL be saved)
        conversation_with_system = self._apply_system_messages(conversation, datetime_str)
        
        # Apply generation-only system message (NOT saved to dataset)
        messages_for_generation = self._apply_generation_system_message(
            conversation_with_system,
            datetime_str
        )
        
        # Enforce rate limiting BEFORE API call
        self.rate_limiter.acquire(timeout=120)
        
        # Call with token tracking if enabled
        if track_tokens and self.track_tokens:
            response, usage = self.assistant_provider.chat_completion(
                messages_for_generation,  # Use messages with generation guidance
                temperature=self.assistant_config.get('temperature', 0.7),
                max_tokens=self.assistant_config.get('max_tokens', 8192),
                return_usage=True
            )
        else:
            response = self.assistant_provider.chat_completion(
                messages_for_generation,  # Use messages with generation guidance
                temperature=self.assistant_config.get('temperature', 0.7),
                max_tokens=self.assistant_config.get('max_tokens', 8192)
            )
            usage = {}
        
        # Record successful request for tracking
        self.rate_limiter.record_request()
        
        result = response.strip() if response else ""
        
        # Validate generated content is not empty
        if not result:
            raise ValueError("LLM generated empty assistant response")
        
        return result, usage
    
    def _apply_system_messages(self, conversation: List[Dict], datetime_str: str) -> List[Dict]:
        """
        Apply system message configuration with MERGING.
        
        System messages are merged into a single message in this order:
        1. prepend_always content (if enabled)
        2. existing system message content (if exists)
        3. append_always content (if enabled)
        
        add_if_missing: Only used if NO existing system message exists
        
        Result: Single system message at position 0 (if any system content exists)
        """
        timezone_str = self.datetime_gen.timezone_str if self.datetime_gen.enabled else 'UTC'
        
        # Extract existing system messages and other messages
        system_messages = [msg for msg in conversation if msg.get('role') == 'system']
        other_messages = [msg for msg in conversation if msg.get('role') != 'system']
        
        # Build merged system content parts
        merged_content_parts = []
        
        # 1. Prepend always (if enabled)
        prepend_always = self.system_config.get('prepend_always', {})
        if prepend_always.get('enabled', False):
            content = prepend_always.get('content', '').strip()
            if content:
                content = content.replace('{current_datetime}', datetime_str or '')
                content = content.replace('{timezone}', timezone_str)
                merged_content_parts.append(content)
        
        # 2. Existing system message(s) OR add_if_missing
        if system_messages:
            # Merge all existing system messages
            for msg in system_messages:
                if msg.get('content'):
                    merged_content_parts.append(msg['content'].strip())
        else:
            # No existing system message - use add_if_missing if enabled
            add_if_missing = self.system_config.get('add_if_missing', {})
            if add_if_missing.get('enabled', False):
                content = add_if_missing.get('content', '').strip()
                if content:
                    content = content.replace('{current_datetime}', datetime_str or '')
                    content = content.replace('{timezone}', timezone_str)
                    merged_content_parts.append(content)
        
        # 3. Append always (if enabled)
        append_always = self.system_config.get('append_always', {})
        if append_always.get('enabled', False):
            content = append_always.get('content', '').strip()
            if content:
                content = content.replace('{current_datetime}', datetime_str or '')
                content = content.replace('{timezone}', timezone_str)
                merged_content_parts.append(content)
        
        # Create final conversation
        result = []
        
        # Add merged system message if we have any content
        if merged_content_parts:
            merged_system_content = ' '.join(merged_content_parts)
            result.append({'role': 'system', 'content': merged_system_content})
        
        # Add all other messages
        result.extend(other_messages)
        
        return result
    
    def _apply_generation_system_message(
        self,
        conversation: List[Dict],
        datetime_str: str
    ) -> List[Dict]:
        """
        Apply generation-only system message for assistant response.
        
        This system message is ONLY used during generation and is NOT saved
        to the dataset. It provides guidance to the LLM without polluting
        the final conversation data.
        
        Args:
            conversation: Conversation with dataset system messages already applied
            datetime_str: Current datetime string for template variables
            
        Returns:
            Conversation with generation-only system message prepended
        """
        assistant_config = self.generation_system_config.get('assistant_response', {})
        
        # If not enabled, return conversation as-is
        if not assistant_config.get('enabled', False):
            return conversation
        
        content = assistant_config.get('content', '').strip()
        if not content:
            return conversation
        
        # Apply template variables
        timezone_str = self.datetime_gen.timezone_str if self.datetime_gen.enabled else 'UTC'
        content = content.replace('{current_datetime}', datetime_str or '')
        content = content.replace('{timezone}', timezone_str)
        
        # Prepend generation-only system message
        # This creates a NEW list, doesn't modify the original
        messages_for_generation = [
            {'role': 'system', 'content': content}
        ]
        messages_for_generation.extend(conversation)
        
        return messages_for_generation
    
    def _extract_from_tags(self, text: str, tag: str) -> str:
        """Extract content from XML tags."""
        pattern = f'<{tag}>(.*?)</{tag}>'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()