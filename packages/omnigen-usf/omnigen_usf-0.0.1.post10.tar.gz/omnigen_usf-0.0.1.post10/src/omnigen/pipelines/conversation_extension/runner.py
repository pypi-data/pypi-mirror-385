"""Production-grade runner with streaming, monitoring, and error handling."""

import time
import signal
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from tqdm import tqdm
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfig
from omnigen.pipelines.conversation_extension.checkpoint import CheckpointManager
from omnigen.pipelines.conversation_extension.streaming_loader import StreamingConversationLoader
from omnigen.pipelines.conversation_extension.generator import ConversationGenerator
from omnigen.core.error_handler import ErrorHandler
from omnigen.storage.incremental_saver import IncrementalSaver
from omnigen.utils.rate_limiter import RateLimiter
from omnigen.utils.logger import setup_logger

# Optional MongoDB monitoring
try:
    from omnigen.monitoring.mongodb_monitor import MongoDBMonitor
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoDBMonitor = None

logger = setup_logger()


class Runner:
    """
    Production-grade pipeline runner.
    
    Features:
    - Streaming data loading (constant memory)
    - Real-time MongoDB monitoring (optional)
    - Fail-fast error handling
    - Incremental saving (zero data loss)
    - Checkpoint/resume support
    - Parallel execution with retry logic
    """
    
    def __init__(self, config: ConversationExtensionConfig):
        """
        Initialize production runner.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.workspace_id = config.get('workspace_id', 'default')
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter()
        
        # Initialize checkpoint manager
        checkpoint_config = config.get('checkpoint', {})
        checkpoint_enabled = checkpoint_config.get('enabled', True)
        
        if checkpoint_enabled:
            checkpoint_file = checkpoint_config.get(
                'checkpoint_file',
                f'workspaces/{self.workspace_id}/checkpoint.json'
            )
            self.checkpoint_manager = CheckpointManager(checkpoint_file, config.to_dict())
            self.checkpoint_data = self.checkpoint_manager.load_or_create()
        else:
            self.checkpoint_manager = None
            self.checkpoint_data = None
        
        # Initialize MongoDB monitor (optional)
        self.monitor = None
        monitoring_config = config.get('monitoring', {})
        if monitoring_config.get('enabled', False) and MONGODB_AVAILABLE:
            try:
                mongodb_uri = monitoring_config.get('mongodb_uri')
                if mongodb_uri:
                    job_id = f"job_{uuid.uuid4().hex[:12]}"
                    user_id = monitoring_config.get('user_id', 'default')
                    session_id = monitoring_config.get('session_id', self.workspace_id)
                    
                    self.monitor = MongoDBMonitor(
                        connection_string=mongodb_uri,
                        job_id=job_id,
                        workspace_id=self.workspace_id,
                        user_id=user_id,
                        session_id=session_id,
                        config=config.to_dict()
                    )
                    logger.info(f"MongoDB monitoring enabled for job {job_id}")
                else:
                    logger.warning("MongoDB monitoring enabled but no URI provided")
            except Exception as e:
                logger.error(f"Failed to initialize MongoDB monitor: {e}")
                self.monitor = None
        elif monitoring_config.get('enabled', False) and not MONGODB_AVAILABLE:
            logger.warning("MongoDB monitoring requested but pymongo not installed")
        
        # Initialize error handler
        self.error_handler = ErrorHandler(monitor=self.monitor)
        
        # Initialize incremental saver
        storage_config = config.get('storage', {})
        output_file = storage_config.get('output_file', f'workspaces/{self.workspace_id}/output.jsonl')
        partial_file = storage_config.get('partial_file', f'workspaces/{self.workspace_id}/partial.jsonl')
        failed_file = storage_config.get('failed_file', f'workspaces/{self.workspace_id}/failed.jsonl')
        
        self.incremental_saver = IncrementalSaver(
            output_file=output_file,
            partial_file=partial_file,
            failed_file=failed_file,
            use_file_locking=True
        )
        
        # Initialize streaming data loader
        self.data_loader = StreamingConversationLoader(config, self.checkpoint_manager)
        
        # Initialize generator with production components
        self.generator = ConversationGenerator(
            config=config,
            rate_limiter=self.rate_limiter,
            error_handler=self.error_handler,
            incremental_saver=self.incremental_saver
        )
        
        # Track for graceful shutdown
        self.shutdown_requested = False
        self._setup_signal_handlers()
        
        logger.info(f"Production runner initialized for workspace: {self.workspace_id}")
    
    def _setup_signal_handlers(self):
        """Setup handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.warning("\n⚠️  Shutdown signal received. Saving checkpoint...")
            self.shutdown_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self):
        """Run the pipeline with full production features."""
        try:
            # Start monitoring
            if self.monitor:
                self.monitor.start_job()
            
            num_convs_requested = self.config.get('generation.num_conversations')
            num_workers = self.config.get('generation.parallel_workers', 10)
            total_lines = self.data_loader.total_lines
            
            # Check if resuming
            is_resuming = False
            if self.checkpoint_manager:
                progress = self.checkpoint_manager.get_progress_summary()
                if progress['total_processed'] > 0:
                    is_resuming = True
            
            # Handle "process all" mode: 0, None, or not specified
            if num_convs_requested in (0, None):
                num_convs = total_lines
                process_all_mode = True
            else:
                # Calculate effective count (min of requested and available)
                num_convs = min(num_convs_requested, total_lines)
                process_all_mode = False
                
                # Warn if limiting to prevent duplicates
                if num_convs_requested > total_lines:
                    logger.warning(
                        f"⚠️  Requested {num_convs_requested} conversations but only "
                        f"{total_lines} available. Limiting to {num_convs}."
                    )
            
            # Display header
            logger.info("="*60)
            if is_resuming:
                logger.info("RESUMING FROM CHECKPOINT")
                logger.info("="*60)
                progress = self.checkpoint_manager.get_progress_summary()
                logger.info(f"Previous Run: {self.checkpoint_data.get('started_at', 'Unknown')}")
                logger.info(f"Already Processed: {progress['total_processed']} "
                          f"(✓{progress['completed']} ⚠{progress['partial']} ✗{progress['failed']} ~{progress['skipped']})")
                remaining = num_convs - progress['total_processed']
                logger.info(f"Remaining: {remaining}")
            else:
                logger.info("PRODUCTION CONVERSATION EXTENSION PIPELINE")
                logger.info("="*60)
                logger.info(f"Total conversations in file: {total_lines}")
                if process_all_mode:
                    logger.info(f"Mode: Process ALL conversations")
                else:
                    logger.info(f"Requested: {num_convs_requested}")
                logger.info(f"Generating: {num_convs}")
            
            logger.info(f"Parallel workers: {num_workers}")
            logger.info(f"MongoDB monitoring: {'Enabled' if self.monitor else 'Disabled'}")
            logger.info(f"Error handling: Enabled (fail-fast)")
            logger.info(f"Streaming mode: Enabled (constant memory)")
            logger.info("="*60)
            
            self._generate_parallel(num_convs, num_workers)
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️  Interrupted. Progress saved in checkpoint.")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            # Finalize monitoring
            if self.monitor:
                try:
                    self.monitor.complete_job()
                    self.monitor.close()
                except Exception as e:
                    logger.error(f"Error finalizing monitor: {e}")
            
            # Finalize storage
            try:
                self.incremental_saver.finalize()
            except Exception as e:
                logger.error(f"Error finalizing storage: {e}")
    
    def _generate_parallel(self, num_conversations: int, num_workers: int):
        """Generate conversations in parallel with production features."""
        complete = 0
        partial = 0
        failed = 0
        skipped = 0
        start_time = time.time()
        
        # Token tracking aggregation (for console display only)
        total_input_tokens = 0
        total_output_tokens = 0
        
        # Get initial progress if resuming
        if self.checkpoint_manager:
            progress = self.checkpoint_manager.get_progress_summary()
            complete = progress['completed']
            partial = progress['partial']
            failed = progress['failed']
            skipped = progress['skipped']
        
        # Get already processed positions
        skip_positions = set()
        if self.checkpoint_manager:
            skip_positions = self.checkpoint_manager.get_processed_positions()
            logger.info(f"Skipping {len(skip_positions)} already processed positions")
        
        pbar = tqdm(
            total=num_conversations,
            desc="Generating",
            unit=" conv",
            colour='cyan',
            ncols=140,
            initial=complete + partial + failed + skipped
        )
        
        with ThreadPoolExecutor(max_workers=num_workers, thread_name_prefix="Worker") as executor:
            futures = {}
            submitted = 0
            
            # Submit conversations using streaming loader
            try:
                for base_conv in self.data_loader.stream_conversations(skip_positions=skip_positions):
                    if self.shutdown_requested:
                        logger.warning("Shutdown requested, stopping submission")
                        break
                    
                    if submitted >= num_conversations:
                        break
                    
                    try:
                        position = base_conv.get('_position', -1)
                        content_hash = base_conv.get('_content_hash', '')
                        
                        # Submit to thread pool
                        future = executor.submit(
                            self._process_conversation_with_retry,
                            base_conv,
                            submitted,
                            None  # No partial resume for now
                        )
                        futures[future] = (submitted, position, content_hash)
                        submitted += 1
                        
                    except Exception as e:
                        logger.error(f"Error submitting conversation: {e}")
                        
            except Exception as e:
                logger.error(f"Error streaming conversations: {e}")
            
            # Process results
            batch_count = 0
            auto_save_freq = self.config.get('checkpoint.auto_save_frequency', 10)
            
            for future in as_completed(futures):
                if self.shutdown_requested:
                    logger.warning("Shutdown requested, waiting for running tasks...")
                
                conv_id, position, content_hash = futures[future]
                
                try:
                    result = future.result()
                    
                    # Skip if marked as skipped
                    if result.get('skipped'):
                        skipped += 1
                        pbar.update(1)
                        continue
                    
                    # Determine status
                    status = 'failed'
                    if result.get('success'):
                        complete += 1
                        status = 'completed'
                    elif result.get('is_partial'):
                        partial += 1
                        status = 'partial'
                    else:
                        failed += 1
                        status = 'failed'
                    
                    # Aggregate token usage (for console display)
                    if 'tokens' in result:
                        tokens = result['tokens']
                        total_input_tokens += tokens.get('input_tokens', 0)
                        total_output_tokens += tokens.get('output_tokens', 0)
                    
                    # Save to incremental saver
                    self.incremental_saver.save_conversation(result, status=status)
                    
                    # Record to monitoring
                    if self.monitor:
                        try:
                            processing_time = result.get('processing_time_ms', 0)
                            tokens_total = result.get('tokens', {}).get('total_tokens', 0)
                            self.monitor.record_conversation(
                                conversation_id=conv_id,
                                position=position,
                                content_hash=content_hash,
                                status=status,
                                conversations=result.get('conversations', []),
                                processing_time_ms=processing_time,
                                tokens=tokens_total,
                                cost=0.0,  # Cost calculation optional, done by user
                                error=result.get('error')
                            )
                        except Exception as e:
                            logger.warning(f"Failed to record to monitor: {e}")
                    
                    # Save to checkpoint
                    if self.checkpoint_manager:
                        self.checkpoint_manager.add_processed(
                            position,
                            content_hash,
                            status,
                            result,
                            save_checkpoint=False  # Batch save
                        )
                        batch_count += 1
                        
                        # Auto-save checkpoint every N conversations
                        if batch_count >= auto_save_freq:
                            self.checkpoint_manager._save_checkpoint()
                            batch_count = 0
                    
                    # Update progress
                    rpm = self.rate_limiter.get_rpm()
                    pbar.update(1)
                    pbar.set_postfix_str(
                        f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} | RPM:{rpm}"
                    )
                    
                    # Update monitoring
                    if self.monitor:
                        try:
                            total_processed = complete + partial + failed + skipped
                            self.monitor.update_progress(position, total_processed)
                        except Exception as e:
                            logger.warning(f"Failed to update monitoring progress: {e}")
                    
                except Exception as e:
                    logger.error(f"Error processing conv {conv_id}: {e}")
                    failed += 1
                    
                    # Save failed to checkpoint
                    if self.checkpoint_manager:
                        self.checkpoint_manager.add_processed(
                            position,
                            content_hash,
                            'failed',
                            {'id': conv_id, 'error': str(e), 'conversations': []},
                            save_checkpoint=False
                        )
                    
                    pbar.update(1)
            
            # Final checkpoint save
            if self.checkpoint_manager:
                self.checkpoint_manager._save_checkpoint()
                logger.info("✓ Final checkpoint saved")
        
        pbar.close()
        
        # Summary
        total_time = time.time() - start_time
        total = complete + partial + failed
        
        print("\n" + "="*60)
        print("GENERATION COMPLETE")
        print("="*60)
        print(f"✓ Complete: {complete:>5}")
        print(f"⚠ Partial:  {partial:>5}")
        print(f"✗ Failed:   {failed:>5}")
        print(f"~ Skipped:  {skipped:>5}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"💾 Saved:   {complete + partial:>5}  ({(complete+partial)/total*100:.1f}% of processed)" if total > 0 else "💾 Saved:   0")
        print(f"⏱  Time:    {total_time/60:>5.1f} min")
        if total > 0:
            print(f"⚡ Speed:   {total/total_time:>5.2f} conv/s")
        print("="*60)
        
        if self.checkpoint_manager:
            print(f"\n📊 Checkpoint: {self.checkpoint_manager.checkpoint_path}")
        
        # Print storage stats
        try:
            stats = self.incremental_saver.get_stats()
            print(f"\n💾 Storage Stats:")
            print(f"   Output: {stats.get('output_count', 0)} conversations")
            print(f"   Partial: {stats.get('partial_count', 0)} conversations")
            print(f"   Failed: {stats.get('failed_count', 0)} conversations")
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
        
        # Print token usage stats
        if total_input_tokens > 0 or total_output_tokens > 0:
            total_tokens = total_input_tokens + total_output_tokens
            print(f"\n💰 Token Usage:")
            print(f"   Input Tokens:  {total_input_tokens:>12,}")
            print(f"   Output Tokens: {total_output_tokens:>12,}")
            print(f"   Total Tokens:  {total_tokens:>12,}")
            
            if complete > 0:
                avg_input = total_input_tokens / complete
                avg_output = total_output_tokens / complete
                avg_total = total_tokens / complete
                print(f"\n   Per Conversation:")
                print(f"   Avg Input:     {avg_input:>12,.0f}")
                print(f"   Avg Output:    {avg_output:>12,.0f}")
                print(f"   Avg Total:     {avg_total:>12,.0f}")
            
            # Optional: Show cost calculation example (if pricing configured)
            token_pricing = self.config.get('generation.token_pricing', {})
            input_price = token_pricing.get('input_cost_per_million', 0)
            output_price = token_pricing.get('output_cost_per_million', 0)
            
            if input_price > 0 or output_price > 0:
                input_cost = (total_input_tokens / 1_000_000) * input_price
                output_cost = (total_output_tokens / 1_000_000) * output_price
                total_cost = input_cost + output_cost
                
                print(f"\n   Cost (if ${input_price}/1M input, ${output_price}/1M output):")
                print(f"   Input Cost:    ${input_cost:>11.6f}")
                print(f"   Output Cost:   ${output_cost:>11.6f}")
                print(f"   Total Cost:    ${total_cost:>11.6f}")
        
        # Print error stats
        try:
            error_stats = self.error_handler.get_error_stats()
            if any(error_stats.values()):
                print(f"\n⚠️  Error Stats:")
                for error_type, count in error_stats.items():
                    if count > 0:
                        print(f"   {error_type}: {count}")
        except Exception as e:
            logger.error(f"Error getting error stats: {e}")
    
    def _process_conversation_with_retry(
        self,
        base_conv: dict,
        conv_id: int,
        partial_state: Optional[dict] = None
    ) -> dict:
        """
        Process a single conversation with retry logic.
        
        Args:
            base_conv: Base conversation data
            conv_id: Conversation ID
            partial_state: Optional partial state for resume
            
        Returns:
            Conversation result dict
        """
        max_retries = self.config.get('error_handling.max_retries', 3)
        
        start_time = time.time()
        
        for attempt in range(1, max_retries + 1):
            try:
                # Generate conversation
                result = self.generator.generate_conversation(
                    base_conv=base_conv,
                    conv_id=conv_id,
                    partial_state=partial_state
                )
                
                # Add processing time
                result['processing_time_ms'] = (time.time() - start_time) * 1000
                
                return result
                
            except Exception as e:
                # Handle error
                error_response = self.error_handler.handle_error(
                    exception=e,
                    conversation_data=base_conv,
                    attempt=attempt,
                    max_retries=max_retries,
                    context={'conversation_id': conv_id}
                )
                
                if error_response['action'] == 'abort_job':
                    # Critical error - abort entire job
                    logger.critical(f"Aborting job due to critical error: {e}")
                    raise e
                    
                elif error_response['action'] == 'skip':
                    # Non-retryable error - skip this conversation
                    logger.warning(f"Skipping conversation {conv_id}: {e}")
                    return {
                        'id': conv_id,
                        'error': str(e),
                        'conversations': [],
                        'success': False,
                        'skipped': False,
                        'generated_at': time.time(),
                        '_position': base_conv.get('_position', -1),
                        '_content_hash': base_conv.get('_content_hash', ''),
                        'processing_time_ms': (time.time() - start_time) * 1000
                    }
                    
                elif error_response['action'] == 'retry':
                    # Transient error - retry after wait
                    wait_time = error_response.get('wait_time', 5.0)
                    if attempt < max_retries:
                        logger.info(f"Retrying conversation {conv_id} in {wait_time:.1f}s (attempt {attempt}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Max retries exceeded
                        logger.error(f"Max retries exceeded for conversation {conv_id}")
                        return {
                            'id': conv_id,
                            'error': f"Max retries exceeded: {e}",
                            'conversations': [],
                            'success': False,
                            'skipped': False,
                            'generated_at': time.time(),
                            '_position': base_conv.get('_position', -1),
                            '_content_hash': base_conv.get('_content_hash', ''),
                            'processing_time_ms': (time.time() - start_time) * 1000
                        }
        
        # Should not reach here
        return {
            'id': conv_id,
            'error': 'Unknown error in retry logic',
            'conversations': [],
            'success': False,
            'skipped': False,
            'generated_at': time.time(),
            '_position': base_conv.get('_position', -1),
            '_content_hash': base_conv.get('_content_hash', ''),
            'processing_time_ms': (time.time() - start_time) * 1000
        }