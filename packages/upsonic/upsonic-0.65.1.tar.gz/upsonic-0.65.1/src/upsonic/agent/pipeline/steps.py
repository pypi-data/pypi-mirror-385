"""
Concrete Step Implementations

This module contains all the concrete step implementations for the agent pipeline.
Each step handles a specific part of the agent execution flow. All steps must execute;
there is no skipping. If any error occurs, it's raised immediately to the user.
"""

import asyncio
import time
from typing import Any, Optional, AsyncIterator
from .step import Step, StepResult, StepStatus
from .context import StepContext


class InitializationStep(Step):
    """Initialize agent state for execution."""
    
    @property
    def name(self) -> str:
        return "initialization"
    
    @property
    def description(self) -> str:
        return "Initialize agent for execution"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Initialize agent state."""
        from upsonic.utils.printing import agent_started

        # Start task timing
        context.task.task_start(context.agent)

        agent_started(context.agent.get_agent_id())

        context.agent.tool_call_count = 0
        context.agent._tool_call_count = 0
        context.agent.current_task = context.task

        # Initialize appropriate result container based on mode
        if context.is_streaming:
            context.agent._stream_run_result.start_new_run()
        else:
            context.agent._run_result.start_new_run()

        return StepResult(
            status=StepStatus.SUCCESS,
            message="Agent initialized",
            execution_time=0.0
        )


class CacheCheckStep(Step):
    """Check if there's a cached response for the task."""
    
    @property
    def name(self) -> str:
        return "cache_check"
    
    @property
    def description(self) -> str:
        return "Check for cached responses"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Check cache for existing response."""
        if not context.task.enable_cache or context.task.is_paused:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Caching not enabled or task paused",
                execution_time=0.0
            )
        
        # Set cache manager
        context.task.set_cache_manager(context.agent._cache_manager)
        
        if context.agent.debug:
            from upsonic.utils.printing import cache_configuration
            embedding_provider_name = None
            if context.task.cache_embedding_provider:
                embedding_provider_name = getattr(
                    context.task.cache_embedding_provider, 'model_name', 'Unknown'
                )
            
            cache_configuration(
                enable_cache=context.task.enable_cache,
                cache_method=context.task.cache_method,
                cache_threshold=context.task.cache_threshold if context.task.cache_method == "vector_search" else None,
                cache_duration_minutes=context.task.cache_duration_minutes,
                embedding_provider=embedding_provider_name
            )
        
        input_text = context.task._original_input or context.task.description
        cached_response = await context.task.get_cached_response(input_text, context.model)
        
        if cached_response is not None:
            similarity = None
            if hasattr(context.task, '_last_cache_entry') and 'similarity' in context.task._last_cache_entry:
                similarity = context.task._last_cache_entry['similarity']
            
            from upsonic.utils.printing import cache_hit
            cache_hit(
                cache_method=context.task.cache_method,
                similarity=similarity,
                input_preview=(context.task._original_input or context.task.description)[:100] 
                    if (context.task._original_input or context.task.description) else None
            )
            
            context.final_output = cached_response
            context.task._response = cached_response
            context.task.task_end()
            context.agent._run_result.output = cached_response
            
            # Early return flag - we'll handle this specially
            context.task._cached_result = True
            
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Cache hit - using cached response",
                execution_time=0.0
            )
        else:
            from upsonic.utils.printing import cache_miss
            cache_miss(
                cache_method=context.task.cache_method,
                input_preview=(context.task._original_input or context.task.description)[:100] 
                    if (context.task._original_input or context.task.description) else None
            )
            
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Cache miss - will execute normally",
                execution_time=0.0
            )


class UserPolicyStep(Step):
    """Apply user policy to the task input."""
    
    @property
    def name(self) -> str:
        return "user_policy"
    
    @property
    def description(self) -> str:
        return "Apply user input safety policy"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Apply user policy to task input."""
        if not context.agent.user_policy or not context.task.description or context.task.is_paused:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="No user policy or task paused",
                execution_time=0.0
            )
        
        # Skip if we have cached result
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        
        from upsonic.safety_engine.models import PolicyInput, RuleOutput
        from upsonic.safety_engine.exceptions import DisallowedOperation
        
        policy_input = PolicyInput(input_texts=[context.task.description])
        
        try:
            rule_output, _action_output, policy_output = await context.agent.user_policy.execute_async(policy_input)
            action_taken = policy_output.action_output.get("action_taken", "UNKNOWN")
            
            if context.agent.debug and rule_output.confidence > 0.0:
                from upsonic.utils.printing import policy_triggered
                policy_triggered(
                    policy_name=context.agent.user_policy.name,
                    check_type="User Input Check",
                    action_taken=action_taken,
                    rule_output=rule_output
                )
            
            if action_taken == "BLOCK":
                context.task.task_end()
                context.task._response = policy_output.output_texts[0] if policy_output.output_texts else "Content blocked by user policy."
                context.final_output = context.task._response
                context.agent._run_result.output = context.final_output
                context.task._policy_blocked = True
                
                return StepResult(
                    status=StepStatus.SUCCESS,
                    message="User input blocked by policy",
                    execution_time=0.0
                )
            elif action_taken in ["REPLACE", "ANONYMIZE"]:
                context.task.description = policy_output.output_texts[0] if policy_output.output_texts else ""
                return StepResult(
                    status=StepStatus.SUCCESS,
                    message=f"User input {action_taken.lower()}d by policy",
                    execution_time=0.0
                )
                
        except DisallowedOperation as e:
            mock_rule_output = RuleOutput(
                confidence=1.0,
                content_type="DISALLOWED_OPERATION",
                details=str(e)
            )
            if context.agent.debug:
                from upsonic.utils.printing import policy_triggered
                policy_triggered(
                    policy_name=context.agent.user_policy.name,
                    check_type="User Input Check",
                    action_taken="DISALLOWED_EXCEPTION",
                    rule_output=mock_rule_output
                )
            
            context.task.task_end()
            context.task._response = f"Operation disallowed by user policy: {e}"
            context.final_output = context.task._response
            context.agent._run_result.output = context.final_output
            context.task._policy_blocked = True
            
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Operation disallowed",
                execution_time=0.0
            )
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="User policy passed",
            execution_time=0.0
        )


class ModelSelectionStep(Step):
    """Select the model to use for execution."""
    
    @property
    def name(self) -> str:
        return "model_selection"
    
    @property
    def description(self) -> str:
        return "Select model for execution"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Select the appropriate model."""
        if context.model:
            from upsonic.models import infer_model
            context.model = infer_model(context.model)
        else:
            context.model = context.agent.model
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message=f"Selected model: {context.model.model_name}",
            execution_time=0.0
        )


class ValidationStep(Step):
    """Validate task attachments and other requirements."""
    
    @property
    def name(self) -> str:
        return "validation"
    
    @property
    def description(self) -> str:
        return "Validate task requirements"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Validate task attachments."""
        from upsonic.utils.validators import validate_attachments_exist
        
        validate_attachments_exist(context.task)
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Validation passed",
            execution_time=0.0
        )


class ToolSetupStep(Step):
    """Setup tools for the task execution."""
    
    @property
    def name(self) -> str:
        return "tool_setup"
    
    @property
    def description(self) -> str:
        return "Setup tools for execution"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Setup tools for the task."""
        context.agent._setup_tools(context.task)
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Tools configured",
            execution_time=0.0
        )


class StorageConnectionStep(Step):
    """Setup storage connection for memory and database operations."""
    
    @property
    def name(self) -> str:
        return "storage_connection"
    
    @property
    def description(self) -> str:
        return "Setup storage connection"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Setup storage connection context manager."""
        # Storage connection is handled by the agent's _managed_storage_connection
        # which is wrapped around the entire pipeline execution
        # This step is just a marker for tracking
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Storage connection ready",
            execution_time=0.0
        )


class LLMManagerStep(Step):
    """Setup LLM manager for model selection and configuration."""
    
    @property
    def name(self) -> str:
        return "llm_manager"
    
    @property
    def description(self) -> str:
        return "Setup LLM manager"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Setup LLM manager and finalize model selection."""
        from upsonic.agent.context_managers.llm_manager import LLMManager
        
        # Create LLM manager with default and requested model
        llm_manager = LLMManager(
            default_model=context.agent.model,
            requested_model=context.model
        )
        
        # Use the LLM manager context
        async with llm_manager.manage_llm():
            selected_model = llm_manager.get_model()
            # The selected_model is a string identifier, we need to infer it
            if selected_model:
                from upsonic.models import infer_model
                context.model = infer_model(selected_model)
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message=f"LLM manager configured: {context.model.model_name}",
            execution_time=0.0
        )


class MessageBuildStep(Step):
    """Build the model request messages."""
    
    @property
    def name(self) -> str:
        return "message_build"
    
    @property
    def description(self) -> str:
        return "Build model request messages"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Build model request messages with memory manager."""
        # Skip if we have cached result or policy blocked
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        
        from upsonic.agent.context_managers import MemoryManager
        
        # Use memory manager with async context
        memory_manager = MemoryManager(context.agent.memory)
        async with memory_manager.manage_memory() as memory_handler:
            messages = await context.agent._build_model_request(
                context.task,
                memory_handler,
                context.state
            )
            context.messages = messages
            context.agent._current_messages = messages
            
            # Store memory handler reference for later steps
            context._memory_handler = memory_handler
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message=f"Built {len(messages)} messages",
            execution_time=0.0
        )


class ModelExecutionStep(Step):
    """Execute the model request."""
    
    @property
    def name(self) -> str:
        return "model_execution"
    
    @property
    def description(self) -> str:
        return "Execute model request"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Execute model request with guardrail support and memory manager."""
        # Skip if we have cached result or policy blocked
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        
        from upsonic.tools.processor import ExternalExecutionPause
        from upsonic.agent.context_managers import MemoryManager
        
        try:
            # Use memory manager with async context
            memory_manager = MemoryManager(context.agent.memory)
            async with memory_manager.manage_memory() as memory_handler:
                if context.task.guardrail:
                    final_response = await context.agent._execute_with_guardrail(
                        context.task,
                        memory_handler,
                        context.state
                    )
                else:
                    model_params = context.agent._build_model_request_parameters(context.task)
                    model_params = context.model.customize_request_parameters(model_params)
                    
                    response = await context.model.request(
                        messages=context.messages,
                        model_settings=context.model.settings,
                        model_request_parameters=model_params
                    )
                    
                    final_response = await context.agent._handle_model_response(
                        response,
                        context.messages
                    )
                
                context.response = final_response
                
                # Store memory handler reference for later steps
                context._memory_handler = memory_handler
            
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Model execution completed",
                execution_time=0.0
            )
            
        except ExternalExecutionPause as e:
            context.task.is_paused = True
            context.task._tools_awaiting_external_execution.append(e.tool_call)
            context.final_output = context.task.response
            context.agent._run_result.output = context.final_output
            
            # This is a valid pause state, not an error - use PENDING status
            return StepResult(
                status=StepStatus.PENDING,
                message="Execution paused for external tool - waiting for external execution",
                execution_time=0.0
            )


class ResponseProcessingStep(Step):
    """Process the model response."""
    
    @property
    def name(self) -> str:
        return "response_processing"
    
    @property
    def description(self) -> str:
        return "Process model response"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Process model response and extract output."""
        # Skip if we have cached result, policy blocked, or external pause
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        if context.task.is_paused:
            context.final_output = context.task.response
            context.agent._run_result.output = context.final_output
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to external pause",
                execution_time=0.0
            )
        
        output = context.agent._extract_output(context.response, context.task)
        context.task._response = output
        context.final_output = output
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Response processed",
            execution_time=0.0
        )


class ReflectionStep(Step):
    """Apply reflection processing to improve output."""
    
    @property
    def name(self) -> str:
        return "reflection"
    
    @property
    def description(self) -> str:
        return "Apply reflection processing"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Apply reflection to improve output."""
        if not (context.agent.reflection_processor and context.agent.reflection):
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Reflection not enabled",
                execution_time=0.0
            )
        
        # Skip if cache hit, policy blocked, or external pause
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        if context.task.is_paused:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to external pause",
                execution_time=0.0
            )
        
        improved_output = await context.agent.reflection_processor.process_with_reflection(
            context.agent,
            context.task,
            context.final_output
        )
        context.task._response = improved_output
        context.final_output = improved_output
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Reflection applied",
            execution_time=0.0
        )


class CallManagementStep(Step):
    """Manage call processing and statistics."""
    
    @property
    def name(self) -> str:
        return "call_management"
    
    @property
    def description(self) -> str:
        return "Process call management"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Handle call management."""
        # Skip if no response or special states
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        if context.task.is_paused:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to external pause",
                execution_time=0.0
            )
        
        from upsonic.agent.context_managers import CallManager
        
        if context.final_output is None and context.task:
            context.final_output = context.task.response
        context.agent._run_result.output = context.final_output
        
        call_manager = CallManager(
            context.model,
            context.task,
            debug=context.agent.debug,
            show_tool_calls=context.agent.show_tool_calls
        )
        
        async with call_manager.manage_call() as call_handler:
            call_handler.process_response(context.agent._run_result)
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Call management processed",
            execution_time=0.0
        )


class TaskManagementStep(Step):
    """Manage task processing and state."""
    
    @property
    def name(self) -> str:
        return "task_management"
    
    @property
    def description(self) -> str:
        return "Process task management"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Handle task management."""
        from upsonic.agent.context_managers import TaskManager
        
        task_manager = TaskManager(context.task, context.agent)
        
        async with task_manager.manage_task() as task_handler:
            task_handler.process_response(context.agent._run_result)
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Task management processed",
            execution_time=0.0
        )


class MemoryMessageTrackingStep(Step):
    """Track messages in memory."""
    
    @property
    def name(self) -> str:
        return "memory_message_tracking"
    
    @property
    def description(self) -> str:
        return "Track messages in memory"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Track messages in memory handler using async context."""
        # Skip if cache hit or policy blocked
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        
        from upsonic.agent.context_managers import MemoryManager
        
        # Use memory manager with async context for tracking
        memory_manager = MemoryManager(context.agent.memory)
        async with memory_manager.manage_memory() as memory_handler:
            # Add new messages to run result
            history_length = len(memory_handler.get_message_history())
            new_messages_start = history_length
            
            if context.messages and new_messages_start < len(context.messages):
                context.agent._run_result.add_messages(context.messages[new_messages_start:])
            if context.response:
                context.agent._run_result.add_message(context.response)
            
            # Process response in memory
            memory_handler.process_response(context.agent._run_result)
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Memory tracking completed",
            execution_time=0.0
        )


class ReliabilityStep(Step):
    """Apply reliability layer processing."""
    
    @property
    def name(self) -> str:
        return "reliability"
    
    @property
    def description(self) -> str:
        return "Apply reliability layer"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Apply reliability layer with async context manager."""
        if not context.agent.reliability_layer:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="No reliability layer",
                execution_time=0.0
            )
        
        # Skip for special states
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        
        from upsonic.agent.context_managers import ReliabilityManager
        
        # Use reliability manager with async context
        reliability_manager = ReliabilityManager(
            context.task,
            context.agent.reliability_layer,
            context.model
        )
        
        async with reliability_manager.manage_reliability() as rel_handler:
            processed_task = await rel_handler.process_task(context.task)
            context.task = processed_task
            context.final_output = processed_task.response
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Reliability applied",
            execution_time=0.0
        )


class AgentPolicyStep(Step):
    """Apply agent output policy."""
    
    @property
    def name(self) -> str:
        return "agent_policy"
    
    @property
    def description(self) -> str:
        return "Apply agent output safety policy"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Apply agent policy to output."""
        if not (context.agent.agent_policy and context.task.response):
            return StepResult(
                status=StepStatus.SUCCESS,
                message="No agent policy or no response",
                execution_time=0.0
            )
        
        # Skip for special states
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        
        processed_task = await context.agent._apply_agent_policy(context.task)
        context.task = processed_task
        context.final_output = processed_task.response
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Agent policy applied",
            execution_time=0.0
        )


class CacheStorageStep(Step):
    """Store the response in cache."""
    
    @property
    def name(self) -> str:
        return "cache_storage"
    
    @property
    def description(self) -> str:
        return "Store response in cache"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Store response in cache."""
        if not (context.task.enable_cache and context.task.response):
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Caching not enabled or no response",
                execution_time=0.0
            )
        
        # Don't cache if it was a cache hit or policy blocked
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Already from cache",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Not caching blocked content",
                execution_time=0.0
            )
        
        input_text = context.task._original_input or context.task.description
        await context.task.store_cache_entry(input_text, context.task.response)
        
        if context.agent.debug:
            from upsonic.utils.printing import cache_stored
            cache_stored(
                cache_method=context.task.cache_method,
                input_preview=(context.task._original_input or context.task.description)[:100] 
                    if (context.task._original_input or context.task.description) else None,
                duration_minutes=context.task.cache_duration_minutes
            )
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Response cached",
            execution_time=0.0
        )


class StreamModelExecutionStep(Step):
    """Execute the model request in streaming mode."""
    
    @property
    def name(self) -> str:
        return "stream_model_execution"
    
    @property
    def description(self) -> str:
        return "Execute model request with streaming"
    
    async def execute(self, context: StepContext) -> StepResult:
        """This is not used in streaming mode - execute_stream is used instead."""
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Streaming execution - see execute_stream",
            execution_time=0.0
        )
    
    async def execute_stream(self, context: StepContext) -> AsyncIterator[Any]:
        """Execute model request in streaming mode and yield events."""
        from upsonic.messages import PartStartEvent, PartDeltaEvent, TextPart, FinalResultEvent, ToolCallPart, ModelRequest
        
        start_time = time.time()
        accumulated_text = ""
        first_token_time = None
        
        # Skip if we have cached result or policy blocked
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            # Stream cached response character by character to simulate real streaming
            cached_content = str(context.final_output)
            
            # Yield PartStartEvent to begin the text part
            yield PartStartEvent(index=0, part=TextPart(content=""))
            
            # Stream the cached content character by character
            for i, char in enumerate(cached_content):
                # Create a delta event for each character
                from upsonic.messages import PartDeltaEvent, TextPartDelta
                delta = TextPartDelta(content_delta=char)
                yield PartDeltaEvent(index=0, delta=delta)
                
                # Update stream result if available
                if context.stream_result:
                    context.stream_result._accumulated_text += char
                    if first_token_time is None:
                        first_token_time = time.time()
                        context.stream_result._first_token_time = first_token_time
            
            # Yield final result event
            yield FinalResultEvent(tool_name=None, tool_call_id=None)
            
            # Update final output and completion status
            if context.stream_result:
                context.stream_result._final_output = cached_content
                context.stream_result._is_complete = True
                context.stream_result._end_time = time.time()
            
            self._last_result = StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=time.time() - start_time
            )
            return
        
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            yield FinalResultEvent(tool_name=None, tool_call_id=None)
            
            self._last_result = StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=time.time() - start_time
            )
            return
        
        # Build model parameters
        model_params = context.agent._build_model_request_parameters(context.task)
        model_params = context.model.customize_request_parameters(model_params)
        
        # Stream the model response
        final_result_received = False
        try:
            async with context.model.request_stream(
                messages=context.messages,
                model_settings=context.model.settings,
                model_request_parameters=model_params
            ) as stream:
                async for event in stream:
                    # Store event in context
                    context.streaming_events.append(event)
                    
                    # Update stream result if available
                    if context.stream_result:
                        context.stream_result._streaming_events.append(event)
                        
                        # Track text accumulation and timing
                        text_content = None
                        if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
                            text_content = event.part.content
                        elif isinstance(event, PartDeltaEvent) and hasattr(event.delta, 'content_delta'):
                            text_content = event.delta.content_delta
                        
                        if text_content:
                            if first_token_time is None:
                                first_token_time = time.time()
                                context.stream_result._first_token_time = first_token_time
                            
                            accumulated_text += text_content
                            context.stream_result._accumulated_text = accumulated_text
                    
                    # Yield the event
                    yield event
                    
                    if isinstance(event, FinalResultEvent):
                        final_result_received = True
            
            # Get the final response from the stream
            final_response = stream.get()
            
            # Check for tool calls
            tool_calls = [
                part for part in final_response.parts 
                if isinstance(part, ToolCallPart)
            ]
            
            if tool_calls:
                # Execute tool calls
                tool_results = await context.agent._execute_tool_calls(tool_calls)
                
                # Add tool calls and results to messages
                context.messages.append(final_response)
                context.messages.append(ModelRequest(parts=tool_results))
                
                # Continue streaming with tool results
                async with context.model.request_stream(
                    messages=context.messages,
                    model_settings=context.model.settings,
                    model_request_parameters=model_params
                ) as continuation_stream:
                    async for event in continuation_stream:
                        # Store event
                        context.streaming_events.append(event)
                        
                        # Update stream result if available
                        if context.stream_result:
                            context.stream_result._streaming_events.append(event)
                            
                            # Track text accumulation and timing
                            text_content = None
                            if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
                                text_content = event.part.content
                            elif isinstance(event, PartDeltaEvent) and hasattr(event.delta, 'content_delta'):
                                text_content = event.delta.content_delta
                            
                            if text_content:
                                if first_token_time is None:
                                    first_token_time = time.time()
                                    context.stream_result._first_token_time = first_token_time
                                
                                accumulated_text += text_content
                                context.stream_result._accumulated_text = accumulated_text
                        
                        # Yield the event
                        yield event
                        
                        if isinstance(event, FinalResultEvent):
                            final_result_received = True
                    
                    # Update final response
                    final_response = continuation_stream.get()
            
            # Extract output and update context
            output = context.agent._extract_output(final_response, context.task)
            context.task._response = output
            context.final_output = output
            context.response = final_response
            
            # Update stream result if available
            if context.stream_result:
                context.stream_result._final_output = output
                context.stream_result._is_complete = True
                context.stream_result._end_time = time.time()
            
            self._last_result = StepResult(
                status=StepStatus.SUCCESS,
                message="Streaming execution completed",
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self._last_result = StepResult(
                status=StepStatus.ERROR,
                message=f"Streaming execution failed: {str(e)}",
                execution_time=time.time() - start_time
            )
            raise


class StreamMemoryMessageTrackingStep(Step):
    """Track messages in memory for streaming execution."""
    
    @property
    def name(self) -> str:
        return "stream_memory_message_tracking"
    
    @property
    def description(self) -> str:
        return "Track messages in memory during streaming"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Track messages in memory handler and stream result."""
        # Skip if cache hit or policy blocked
        if hasattr(context.task, '_cached_result') and context.task._cached_result:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to cache hit",
                execution_time=0.0
            )
        if hasattr(context.task, '_policy_blocked') and context.task._policy_blocked:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Skipped due to policy block",
                execution_time=0.0
            )
        
        from upsonic.agent.context_managers import MemoryManager
        
        # Use memory manager with async context for tracking
        memory_manager = MemoryManager(context.agent.memory)
        async with memory_manager.manage_memory() as memory_handler:
            # Add new messages to stream result
            history_length = len(memory_handler.get_message_history())
            new_messages_start = history_length
            
            if context.messages and new_messages_start < len(context.messages):
                if context.stream_result:
                    context.stream_result.add_messages(context.messages[new_messages_start:])
            if context.response and context.stream_result:
                context.stream_result.add_message(context.response)
            
            # Process response in memory
            if context.stream_result:
                memory_handler.process_response(context.stream_result)
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Streaming memory tracking completed",
            execution_time=0.0
        )


class StreamFinalizationStep(Step):
    """Finalize the streaming execution."""
    
    @property
    def name(self) -> str:
        return "stream_finalization"
    
    @property
    def description(self) -> str:
        return "Finalize streaming execution"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Finalize streaming execution."""
        # Ensure final_output is set from task response if not already set
        if context.final_output is None and context.task:
            context.final_output = context.task.response
        
        # Set final output in stream result if available
        if context.stream_result:
            if context.stream_result._final_output is None:
                context.stream_result._final_output = context.final_output
        
        # End the task
        context.task.task_end()
        
        return StepResult(
            status=StepStatus.SUCCESS,
            message="Streaming finalized",
            execution_time=0.0
        )


class FinalizationStep(Step):
    """Finalize the execution."""
    
    @property
    def name(self) -> str:
        return "finalization"
    
    @property
    def description(self) -> str:
        return "Finalize execution"
    
    async def execute(self, context: StepContext) -> StepResult:
        """Finalize execution."""
        # Ensure final_output is set from task response if not already set
        if context.final_output is None and context.task:
            context.final_output = context.task.response

        # Set final output in run result
        context.agent._run_result.output = context.final_output

        # End the task to calculate duration
        context.task.task_end()

        # Print summary if needed
        if context.task and not context.task.not_main_task:
            from upsonic.utils.printing import print_price_id_summary
            print_price_id_summary(context.task.price_id, context.task)

        return StepResult(
            status=StepStatus.SUCCESS,
            message="Execution finalized",
            execution_time=0.0
        )
