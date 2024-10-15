from collections.abc import Sequence
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableWithMessageHistory
from langchain_core.tools import BaseTool



class MemoryToolsAgent:
    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an assistant that helps people book appointments with their calendar"),
                # Placeholder to provide memory to the agent
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                # Scratchpad for tools
                ("placeholder", "{agent_scratchpad}")
            ])
    _session_id: str
    _agent: RunnableWithMessageHistory

    ############
    #  Public  #
    ############

    def __init__(self, model: BaseLanguageModel, tools, session_id: str):
        # Session id is bound to the agent here
        self._session_id = session_id
        self._initialize_agent(model, tools)


    def invoke(self, msg: str):
        result = self._agent.invoke({"input": msg},
                                    RunnableConfig({"configurable":
                                                    {"session_id":
                                                     self._session_id}}))
        return result["output"]


    #############
    #  Private  #
    #############


    def _initialize_agent(self, model: BaseLanguageModel, tools: Sequence[BaseTool]):
        memory = InMemoryChatMessageHistory(session_id=self._session_id)
        base_agent = create_tool_calling_agent(model, tools, self.prompt)
        executor = AgentExecutor(agent=base_agent, tools=tools)
        self._agent = RunnableWithMessageHistory(
            executor, # type: ignore
                lambda _: memory,
                input_messages_key="input",
                history_messages_key="chat_history",
                )

