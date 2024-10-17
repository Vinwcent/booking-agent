from collections.abc import Sequence
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from langchain_core.messages import HumanMessage, SystemMessage



class MemoryToolsAgent:
    _agent: Runnable
    _model: BaseChatModel

    ############
    #  Public  #
    ############

    def __init__(self, model: BaseChatModel, tools,
                 system_prompt: str = "You are an assistant that tries to answer questions"):
        # Session id is bound to the agent here
        self._messages = []
        self._tools = tools
        self._model = model
        self._initialize_agent(tools, system_prompt)


    def invoke(self, msg: str):
        # We add the user input
        self._messages.append(HumanMessage(content=msg))
        # We get the ai answer and add it
        ai_answer = self._agent.invoke({"messages": self._messages})
        self._messages.append(ai_answer)

        tools_map = {tool.func.__name__: tool for tool in self._tools}
        # If it's not a classical stop, we are in a tool calling case
        while ai_answer.response_metadata["finish_reason"] != "stop":
            # We call each tool one after the other and store permanently their
            # output
            for tool_call in ai_answer.tool_calls:
                selected_tool = tools_map[tool_call["name"].lower()]
                tool_msg = selected_tool.invoke(tool_call)
                self._messages.append(tool_msg)
            ai_answer = self._agent.invoke({"messages": self._messages})
            self._messages.append(ai_answer)
        return ai_answer.content


    #############
    #  Private  #
    #############

    def _reset_memory_and_rebind_tools(self, tools):
        # We keep the system msg, this function is made for testing with gradio
        self._messages = [self._messages[0]]
        self._tools = tools
        self._initialize_agent(tools, self._messages[0].content)


    def _initialize_agent(self, tools:
                          Sequence[BaseTool], system_prompt: str):
        # Here I don't use the "magic" RunnableWithMessageHistory because I want
        # to keep ToolMessage persistent in memory. Indeed, since
        # RunnableWithMessageHistory doesn't store ToolMessages between
        # HumanMessages, the LLM was forgetting what "today" was meaning since
        # it was found thanks to a tool (same for some dates and it was
        # extremely annoying to see him forget between two inputs)
        self._messages.append(SystemMessage(system_prompt))
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="messages")
            ]
        )
        self._agent = prompt | self._model.bind_tools(tools)
