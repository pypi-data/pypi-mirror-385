"""Conversation management utilities for the agent system."""

import json
import logging
from pathlib import Path
from typing import Any

import tiktoken

from ..prompts import SYSTEM_PROMPT
from ..providers import LLMProvider

logger = logging.getLogger(__name__)


def create_system_prompt() -> str:
    """
    Create the system prompt for the agent.

    Checks for agent documentation files (AGENTS.md, agents.md, agent.md, AGENT.md)
    and appends their content to the base system prompt if found.

    Returns:
        The system prompt with optional project documentation appended
    """
    # Check for agent documentation files in order of preference
    agent_docs = ["AGENTS.md", "agents.md", "agent.md", "AGENT.md"]
    for doc_file in agent_docs:
        doc_path = Path(doc_file)
        if doc_path.exists():
            try:
                agents_content = doc_path.read_text(encoding="utf-8")
                # Append the agent documentation content to the system prompt
                return f"{SYSTEM_PROMPT}\n\nPROJECT_DOCUMENTATION:\n{agents_content}"
            except Exception as e:
                logger.warning(f"Failed to read {doc_file}: {e}")
                # Continue to next file if reading fails
                continue

    # Return base prompt if no documentation files exist
    return SYSTEM_PROMPT


def get_token_count(
    conversation_history: list[dict[str, Any]], model: str, base_url: str | None
) -> dict[str, Any]:
    """
    Get token usage statistics for a conversation.

    Args:
        conversation_history: List of conversation messages
        model: Model identifier
        base_url: Base URL for the provider (optional)

    Returns:
        Dictionary with token usage information including:
        - total_tokens: Total tokens in conversation history
        - usage_percent: Percentage of typical context window used (estimate)
        - message_count: Number of messages in history
        - system_tokens: Tokens from system messages
        - system_messages: Number of system messages
        - user_tokens: Tokens from user messages
        - user_messages: Number of user messages
        - assistant_tokens: Tokens from assistant messages
        - assistant_messages: Number of assistant messages
        - tool_tokens: Tokens from tool messages
        - tool_messages: Number of tool messages
    """
    try:
        # Try to get the appropriate encoding for the model
        # Default to cl100k_base which works for GPT-4, GPT-3.5-turbo, etc.
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fall back to cl100k_base for unknown models
            encoding = tiktoken.get_encoding("cl100k_base")

        # Initialize counters
        total_tokens = 0
        system_tokens = 0
        user_tokens = 0
        assistant_tokens = 0
        tool_tokens = 0

        system_messages = 0
        user_messages = 0
        assistant_messages = 0
        tool_messages = 0

        # Count tokens in conversation history
        for message in conversation_history:
            role = message.get("role", "")
            content = message.get("content", "")

            # Count tokens in role
            role_tokens = len(encoding.encode(role))
            total_tokens += role_tokens

            # Count tokens in content
            content_tokens = len(encoding.encode(content)) if content else 0
            total_tokens += content_tokens

            # Count tokens in tool calls (if present)
            tool_call_tokens = 0
            if message.get("tool_calls"):
                tool_call_tokens = len(encoding.encode(json.dumps(message["tool_calls"])))
                total_tokens += tool_call_tokens

            # Add overhead for message formatting (~4 tokens per message)
            message_overhead = 4
            total_tokens += message_overhead

            # Categorize by role
            if role == "system":
                system_tokens += role_tokens + content_tokens + tool_call_tokens + message_overhead
                system_messages += 1
            elif role == "user":
                user_tokens += role_tokens + content_tokens + tool_call_tokens + message_overhead
                user_messages += 1
            elif role == "assistant":
                assistant_tokens += (
                    role_tokens + content_tokens + tool_call_tokens + message_overhead
                )
                assistant_messages += 1
            elif role == "tool":
                tool_tokens += role_tokens + content_tokens + tool_call_tokens + message_overhead
                tool_messages += 1

        # Estimate context window (most models have 128k, some have 8k-32k)
        # This is a rough estimate
        estimated_context_window = 128000  # Conservative estimate
        usage_percent = (total_tokens / estimated_context_window) * 100

        return {
            "total_tokens": total_tokens,
            "usage_percent": usage_percent,
            "message_count": len(conversation_history),
            "model": model,
            "base_url": base_url,
            "system_tokens": system_tokens,
            "system_messages": system_messages,
            "user_tokens": user_tokens,
            "user_messages": user_messages,
            "assistant_tokens": assistant_tokens,
            "assistant_messages": assistant_messages,
            "tool_tokens": tool_tokens,
            "tool_messages": tool_messages,
        }

    except Exception as e:
        # Return error info if token counting fails
        return {
            "error": str(e),
            "message_count": len(conversation_history),
            "model": model,
            "base_url": base_url,
        }


def compact_conversation(
    conversation_history: list[dict[str, Any]],
    provider: LLMProvider,
    model: str,
    keep_recent: int = 4,
) -> tuple[bool, str, dict[str, Any], list[dict[str, Any]]]:
    """
    Compact conversation history by summarizing older messages.

    This helps manage context window limits by condensing older conversation
    history into a summary while keeping recent messages intact.

    Args:
        conversation_history: Current conversation history
        provider: LLM provider instance for generating summary
        model: Model identifier to use
        keep_recent: Number of recent messages to keep intact (default: 4)

    Returns:
        Tuple of (success: bool, message: str, stats: dict, new_history: list)
        Stats include before/after token counts and reduction percentage
        new_history is the compacted conversation history (empty if failed)
    """
    # Need at least system + user + assistant + keep_recent messages to compact
    min_messages = 3 + keep_recent
    if len(conversation_history) <= min_messages:
        return (
            False,
            f"Conversation too short to compact (need >{min_messages} messages)",
            {},
            [],
        )

    # Get token count before compaction
    # We need to extract model and base_url from somewhere - they should be passed in
    # For now, we'll use empty base_url
    before_stats = get_token_count(conversation_history, model, None)
    if "error" in before_stats:
        return False, f"Error counting tokens: {before_stats['error']}", {}, []

    before_tokens = before_stats["total_tokens"]

    try:
        # Separate conversation parts
        system_msg = conversation_history[0]  # Keep system prompt
        recent_msgs = conversation_history[-keep_recent:]  # Keep recent messages
        to_summarize = conversation_history[1:-keep_recent]  # Messages to compact

        if not to_summarize:
            return False, "No messages to compact", {}, []

        # Create summarization prompt
        summary_request = {
            "role": "user",
            "content": """Please create a concise summary of the conversation so far.
Focus on:
- Key tasks and requests made
- Important decisions and outcomes
- Relevant code changes or file operations
- Any ongoing context needed for future requests

Keep the summary brief but informative (aim for 200-400 words).""",
        }

        # Build temporary conversation for summarization
        summarization_conversation = [system_msg] + to_summarize + [summary_request]

        # Call LLM to create summary
        response = provider.create_message(
            messages=summarization_conversation,
            tools=[],  # No tools needed for summarization
            model=model,
        )

        summary_content = response.get("content", "")
        if not summary_content:
            return False, "Failed to generate summary", {}, []

        # Create new conversation history
        summary_msg = {
            "role": "assistant",
            "content": f"[CONVERSATION SUMMARY]\n\n{summary_content}\n\n[END SUMMARY]",
        }

        # Rebuild conversation: system + summary + recent messages
        new_history = [system_msg, summary_msg] + recent_msgs

        # Get token count after compaction
        after_stats = get_token_count(new_history, model, None)
        after_tokens = after_stats["total_tokens"]

        # Calculate reduction
        tokens_saved = before_tokens - after_tokens
        reduction_percent = (tokens_saved / before_tokens) * 100 if before_tokens > 0 else 0

        stats = {
            "before_tokens": before_tokens,
            "after_tokens": after_tokens,
            "tokens_saved": tokens_saved,
            "reduction_percent": reduction_percent,
            "messages_before": before_stats["message_count"],
            "messages_after": len(new_history),
            "messages_summarized": len(to_summarize),
        }

        success_msg = (
            f"Conversation compacted: {before_tokens:,} → {after_tokens:,} tokens "
            f"({reduction_percent:.1f}% reduction)"
        )

        return True, success_msg, stats, new_history

    except Exception as e:
        logger.error(f"Error during conversation compaction: {e}", exc_info=True)
        return False, f"Error compacting conversation: {e}", {}, []
