import asyncio
from typing import Any, Dict, List, Optional, Type, Tuple, Literal, Union
import json
import copy

from upsonic.messages.messages import ModelMessagesTypeAdapter, ModelRequest, ModelResponse, SystemPromptPart, UserPromptPart
from pydantic import BaseModel, Field, create_model

from upsonic.storage.base import Storage
from upsonic.storage.session.sessions import InteractionSession, UserProfile
from upsonic.storage.types import SessionId, UserId
from upsonic.schemas import UserTraits
from upsonic.models import Model
from upsonic.utils.printing import info_log


class Memory:
    """
    A comprehensive, configurable memory orchestrator for an AI agent.

    This class serves as a centralized module for managing different types of
    memory and respects the specific data formats and logic established in
    the original application design for handling chat history.
    """

    def __init__(
        self,
        storage: Storage,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        full_session_memory: bool = False,
        summary_memory: bool = False,
        user_analysis_memory: bool = False,
        user_profile_schema: Optional[Type[BaseModel]] = None,
        dynamic_user_profile: bool = False,
        num_last_messages: Optional[int] = None,
        model: Optional[Union[Model, str]] = None,
        debug: bool = False,
        feed_tool_call_results: bool = False,
        user_memory_mode: Literal['update', 'replace'] = 'update'
    ):
        
        self.storage = storage
        self.num_last_messages = num_last_messages
        self.full_session_memory_enabled = full_session_memory
        self.summary_memory_enabled = summary_memory
        self.user_analysis_memory_enabled = user_analysis_memory
        self.model = model
        self.debug = debug
        self.feed_tool_call_results = feed_tool_call_results

        self.profile_schema_model = user_profile_schema or UserTraits
        self.is_profile_dynamic = dynamic_user_profile
        self.user_memory_mode = user_memory_mode

        if self.is_profile_dynamic and user_profile_schema:
            from upsonic.utils.printing import warning_log
            warning_log("`dynamic_user_profile` is True, so the provided `user_profile_schema` will be ignored.", "MemoryStorage")
            self.profile_schema_model = None
        else:
            self.profile_schema_model = user_profile_schema or UserTraits        

        if self.full_session_memory_enabled or self.summary_memory_enabled:
            if not session_id:
                raise ValueError("`session_id` is required when full_session_memory or summary_memory is enabled.")
            self.session_id: Optional[SessionId] = SessionId(session_id)
        else:
            self.session_id = None
        if self.user_analysis_memory_enabled:
            if not user_id:
                raise ValueError("`user_id` is required when user_analysis_memory is enabled.")
            self.user_id: Optional[UserId] = UserId(user_id)
        elif user_id:
            self.user_id: Optional[UserId] = UserId(user_id)
        else:
            self.user_id = None

    async def prepare_inputs_for_task(self) -> Dict[str, Any]:
        """
        Gathers all relevant memory data before a task execution, correctly
        parsing and limiting the chat history.
        """
        prepared_data = {
            "message_history": [],
            "context_injection": "",
            "system_prompt_injection": ""
        }

        if self.user_analysis_memory_enabled and self.user_id:
            profile = await self.storage.read_async(self.user_id, UserProfile)
            if profile and profile.profile_data:
                profile_str = "\n".join(f"- {key}: {value}" for key, value in profile.profile_data.items())
                prepared_data["system_prompt_injection"] = f"<UserProfile>\n{profile_str}\n</UserProfile>"

        if self.session_id:
            session = await self.storage.read_async(self.session_id, InteractionSession)
            if session:
                if self.summary_memory_enabled and session.summary:
                    prepared_data["context_injection"] = f"<SessionSummary>\n{session.summary}\n</SessionSummary>"
                if self.full_session_memory_enabled and session.chat_history:
                    try:
                        raw_messages = session.chat_history
                        if not self.feed_tool_call_results:
                            TOOL_RELATED_TYPES = {'tool_call_request', 'tool_response'}
                            filtered_messages = [
                                element for element in raw_messages
                                if not any(
                                    part.get('part_kind') in ['tool-call', 'tool-return']
                                    for part in element.get('parts', [])
                                )
                            ]
                            raw_messages = filtered_messages

                        validated_history = ModelMessagesTypeAdapter.validate_python(raw_messages)
                        limited_history = self._limit_message_history(validated_history)
                        prepared_data["message_history"] = limited_history
                        
                    except Exception as e:
                        from upsonic.utils.printing import warning_log
                        warning_log(f"Could not validate or process stored chat history. Starting fresh. Error: {e}", "MemoryStorage")
                        prepared_data["message_history"] = []
        return prepared_data

    async def update_memories_after_task(self, model_response) -> None:
        """
        Updates all relevant memories after a task has been completed, saving
        the chat history in the correct format.
        """
        await asyncio.gather(
            self._update_interaction_session(model_response),
            self._update_user_profile(model_response)
        )

    async def _update_interaction_session(self, model_response):
        """Helper to handle updating the InteractionSession object."""
        if not (self.full_session_memory_enabled or self.summary_memory_enabled) or not self.session_id:
            return

        session = await self.storage.read_async(self.session_id, InteractionSession)
        if not session:
            session = InteractionSession(session_id=self.session_id, user_id=self.user_id)
        
        if self.full_session_memory_enabled:
            from pydantic_core import to_jsonable_python
            # Get only the new messages from this run
            new_messages_only = model_response.new_messages()
            all_messages_as_dicts = to_jsonable_python(new_messages_only)
            session.chat_history.extend(all_messages_as_dicts)  # Store as a list of messages

        if self.summary_memory_enabled:
            try:
                session.summary = await self._generate_new_summary(session.summary, model_response)
            except Exception as e:
                from upsonic.utils.printing import warning_log
                warning_log(f"Failed to generate session summary: {e}", "MemoryStorage")
        
        await self.storage.upsert_async(session)

    async def _update_user_profile(self, model_response):
        """Helper to handle updating the UserProfile object."""
        if not self.user_analysis_memory_enabled or not self.user_id:
            return
        
        profile = await self.storage.read_async(self.user_id, UserProfile)

        if not profile:
            profile = UserProfile(user_id=self.user_id)

        if self.user_analysis_memory_enabled:
            try:
                updated_traits = await self._analyze_interaction_for_traits(profile.profile_data, model_response)
                
                if self.debug:
                    info_log(f"Extracted traits: {updated_traits}", "Memory")
                
                if self.user_memory_mode == 'replace':
                    profile.profile_data = updated_traits
                elif self.user_memory_mode == 'update':
                    profile.profile_data.update(updated_traits)
                else:
                    raise ValueError(f"Unexpected update mode: {self.user_memory_mode}")
            except Exception as e:
                from upsonic.utils.printing import warning_log
                warning_log(f"Failed to analyze user profile: {e}", "MemoryStorage")

        await self.storage.upsert_async(profile)


    def _limit_message_history(self, message_history: List) -> List:
        """
        Limits conversation history to the last N runs, creating a new synthetic
        first request that combines the original system prompt with the user prompt
        from the beginning of the limited window.

        Args:
            message_history: The full, flat list of ModelRequest and ModelResponse objects.

        Returns:
            A new, limited message history list.
        """
        if not self.num_last_messages or self.num_last_messages <= 0:
            return message_history

        if not message_history:
            return []

        all_runs = []
        for i in range(0, len(message_history) - 1, 2):
            request = message_history[i]
            response = message_history[i+1]
            if isinstance(request, ModelRequest) and isinstance(response, ModelResponse):
                all_runs.append((request, response))

        if len(all_runs) <= self.num_last_messages:
            return message_history

        kept_runs = all_runs[-self.num_last_messages:]
        
        if not kept_runs:
            return []

        original_system_prompt = None
        if message_history:
            for part in message_history[0].parts:
                if isinstance(part, SystemPromptPart):
                    original_system_prompt = part
                    break
        
        if not original_system_prompt:
            from upsonic.utils.printing import warning_log
            warning_log("Could not find original SystemPromptPart. History might be malformed.", "MemoryStorage")
            return [message for run in kept_runs for message in run]

        first_request_in_window = kept_runs[0][0]

        new_user_prompt = None
        for part in first_request_in_window.parts:
            if isinstance(part, UserPromptPart):
                new_user_prompt = part
                break
                
        if not new_user_prompt:
            from upsonic.utils.printing import warning_log
            warning_log("Could not find UserPromptPart in the first message of the limited window.", "MemoryStorage")
            return [message for run in kept_runs for message in run]

        modified_first_request = copy.deepcopy(first_request_in_window)
        modified_first_request.parts = [original_system_prompt, new_user_prompt]
        
        final_history = []
        final_history.append(modified_first_request)
        final_history.append(kept_runs[0][1])
        
        for run in kept_runs[1:]:
            final_history.extend(run)
            
        info_log(f"Original history had {len(all_runs)} runs. "
                f"Limited to the last {self.num_last_messages}, resulting in {len(final_history)} messages.", 
                context="Memory")

        return final_history
        

    async def _generate_new_summary(self, previous_summary: str, model_response) -> str:
        from upsonic.agent.agent import Agent
        from upsonic.tasks.tasks import Task
        from pydantic_core import to_jsonable_python

        last_turn = to_jsonable_python(model_response.new_messages())
        session = await self.storage.read_async(self.session_id, InteractionSession)
        
        summarizer = Agent(name="Summarizer", model=self.model, debug=self.debug)
        
        prompt = f"""Update the conversation summary based on the new interaction.

Previous Summary: {previous_summary or 'None (this is the first interaction)'}

New Conversation Turn:
{json.dumps(last_turn, indent=2)}

Full Chat History:
{json.dumps(session.chat_history, indent=2) if session and session.chat_history else 'None'}

YOUR TASK: Create a concise summary that captures the key points of the entire conversation, including the new turn. Focus on important information, user preferences, and topics discussed.
"""
        task = Task(description=prompt, response_format=str)
        
        summary_response = await summarizer.do_async(task)
        return str(summary_response)

    def _extract_user_prompt_content(self, messages: list) -> list[str]:
        """Extracts the content string from all UserPromptParts in a list of messages."""
        user_prompts = []
        if not messages:
            return user_prompts
            
        for message in messages:
            if isinstance(message, ModelRequest):
                for part in message.parts:
                    if isinstance(part, UserPromptPart):
                        user_prompts.append(part.content)
        return user_prompts


    async def _analyze_interaction_for_traits(self, current_profile: dict, model_response) -> dict:
        """
        Analyzes user interaction to extract traits.

        It gathers user prompt content from two independent sources:
        1. The full session history from storage (if available).
        2. The new messages from the latest model response (if available).

        It then feeds this combined, clearly demarcated context to the analyzer LLM.
        """
        from upsonic.agent.agent import Agent
        from upsonic.tasks.tasks import Task

        if not self.model:
            raise ValueError("A model must be configured on the Memory object to analyze user traits.")

        historical_prompts_content = []
        new_prompts_content = []

        session = await self.storage.read_async(self.session_id, InteractionSession)
        if session and session.chat_history:
            try:
                validated_history = ModelMessagesTypeAdapter.validate_python(session.chat_history)
                historical_prompts_content = self._extract_user_prompt_content(validated_history)
            except Exception as e:
                from upsonic.utils.printing import warning_log
                warning_log(f"Could not validate session history. It will be skipped for analysis. Error: {e}", "MemoryStorage")

        new_messages = model_response.new_messages()
        if new_messages:
            new_prompts_content = self._extract_user_prompt_content(new_messages)
            # Extracted new user prompts from the latest response

        if not historical_prompts_content and not new_prompts_content:
            from upsonic.utils.printing import warning_log
            warning_log("No user prompts found in history or new messages. Cannot analyze traits.", "MemoryStorage")
            return {}

        prompt_context_parts = []
        source_log = []
        if historical_prompts_content:
            history_str = "\n".join(f"- {p}" for p in historical_prompts_content)
            prompt_context_parts.append(f"### Historical User Prompts:\n{history_str}")
            source_log.append("session history")
            
        if new_prompts_content:
            new_str = "\n".join(f"- {p}" for p in new_prompts_content)
            prompt_context_parts.append(f"### Latest User Prompts:\n{new_str}")
            source_log.append("new messages")

        conversation_context_str = "\n\n".join(prompt_context_parts)
        info_log(f"Analyzing traits using context from: {', '.join(source_log)}.", context="Memory")
        
        from upsonic.utils.printing import warning_log
        
        analyzer = Agent(name="User Trait Analyzer", model=self.model, debug=self.debug)

        if self.is_profile_dynamic:
            from typing import List
            
            class FieldDefinition(BaseModel):
                """A single field definition"""
                name: str = Field(..., description="Snake_case field name")
                description: str = Field(..., description="Description of what this field represents")
            
            class ProposedSchema(BaseModel):
                """Schema for defining user trait fields"""
                fields: List[FieldDefinition] = Field(
                    ..., 
                    min_length=2,
                    description="List of 2-5 field definitions extracted from the conversation"
                )
                

            schema_generator_prompt = f"""Analyze this conversation and identify 2-5 specific traits about the user.

=== USER CONVERSATION ===
{conversation_context_str}

=== YOUR TASK ===
Create a list of field definitions where each field has:
- name: snake_case field name (e.g., preferred_name, occupation, expertise_level, primary_interest, hobbies)
- description: what that field represents

You MUST provide at least 2-3 fields based on what the user explicitly mentioned in the conversation.

Examples:
- If user says "I'm Alex interested in ML": fields like preferred_name, primary_interest, expertise_level
- If user says "I work as engineer and love coding": fields like occupation, hobbies, expertise_area
"""
            schema_task = Task(description=schema_generator_prompt, response_format=ProposedSchema)
            
            try:
                proposed_schema_response = await analyzer.do_async(schema_task)
                field_count = len(proposed_schema_response.fields) if proposed_schema_response and hasattr(proposed_schema_response, 'fields') else 0
                info_log(f"LLM generated schema with {field_count} fields", "Memory")
                if field_count > 0:
                    info_log(f"Generated field names: {[f.name for f in proposed_schema_response.fields]}", "Memory")
            except Exception as e:
                warning_log(f"Dynamic schema generation failed with error: {e}. No user traits extracted.", "Memory")
                return {}

            if not proposed_schema_response or not hasattr(proposed_schema_response, 'fields') or not proposed_schema_response.fields:
                field_count = len(proposed_schema_response.fields) if proposed_schema_response and hasattr(proposed_schema_response, 'fields') else 0
                info_log(f"Schema generation result: {field_count} fields generated", "Memory")
                warning_log(f"Dynamic schema generation returned {field_count} fields (expected at least 2). No user traits extracted.", "Memory")
                return {}

            # Create dynamic model with Optional[str] type for all fields (more compatible with structured output)
            dynamic_fields = {field_def.name: (Optional[str], Field(None, description=field_def.description)) for field_def in proposed_schema_response.fields}
            DynamicUserTraitModel = create_model('DynamicUserTraitModel', **dynamic_fields)

            trait_extractor_prompt = f"""Extract user traits from this conversation.

Current Profile Data:
{json.dumps(current_profile, indent=2)}

User's Conversation:
{conversation_context_str}

YOUR TASK: Fill in the trait fields based on what the user explicitly stated. Extract concrete, specific information from the conversation. If information is not available for a field, you may leave it as null.
"""
            trait_task = Task(description=trait_extractor_prompt, response_format=DynamicUserTraitModel)
            trait_response = await analyzer.do_async(trait_task)
            
            if trait_response and hasattr(trait_response, 'model_dump'):
                return trait_response.model_dump()
            return {}

        else:
            prompt = f"""Analyze the user's conversation and extract their traits.

Current Profile Data:
{json.dumps(current_profile, indent=2)}

User's Conversation:
{conversation_context_str}

YOUR TASK: Fill in trait fields based on what the user explicitly stated in the conversation. Extract concrete, specific information. Update existing traits if new information is provided. Leave fields as None if information is not available.
"""
            task = Task(description=prompt, response_format=self.profile_schema_model)
            
            trait_response = await analyzer.do_async(task)
            # trait_response is the output directly (profile_schema_model instance)
            if trait_response and hasattr(trait_response, 'model_dump'):
                return trait_response.model_dump()
            return {}