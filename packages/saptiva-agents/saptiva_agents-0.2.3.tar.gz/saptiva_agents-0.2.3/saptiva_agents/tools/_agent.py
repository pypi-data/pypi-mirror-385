from autogen_agentchat.tools import AgentTool


class AgentTool(AgentTool):
    """Tool that can be used to run a task using an agent.

    .. important::
        When using AgentTool, you **must** disable parallel tool calls in the model client configuration
        to avoid concurrency issues. Agents cannot run concurrently as they maintain internal state
        that would conflict with parallel execution. For example, set ``parallel_tool_calls=False``
        for :class:`~autogen_ext.models.openai.OpenAIChatCompletionClient` and
        :class:`~autogen_ext.models.openai.AzureOpenAIChatCompletionClient`.

    Args:
        agent (BaseChatAgent): The agent to be used for running the task.
        return_value_as_last_message (bool): Whether to use the last message content of the task result
            as the return value of the tool in :meth:`~autogen_agentchat.tools.TaskRunnerTool.return_value_as_string`.
            If set to True, the last message content will be returned as a string.
            If set to False, the tool will return all messages in the task result as a string concatenated together,
            with each message prefixed by its source (e.g., "writer: ...", "assistant: ...").
    """
    pass
