from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate



class :
    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an assistant that helps people book appointments with their calendar"),
                # Placeholder to provide memory to the agent
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                # Scratchpad for tools
                ("placeholder", "{agent_scratchpad}")
            ])

    def __init__(self, model: BaseLanguageModel):
        self._initialize_agent(model)

    def _initialize_agent(self, model: BaseLanguageModel):
        # I suppose a unique session and so, directly initialize the
        # memory with a hardcoded id
        memory = InMemoryChatMessageHistory(session_id="unique")
        agent = create_tool_calling_agent(model, tools

