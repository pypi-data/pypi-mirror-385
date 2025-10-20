from typing import Any

from modaic import Indexer, PrecompiledAgent, PrecompiledConfig
from modaic.context import Context

from .registry import builtin_agent, builtin_config, builtin_indexer

agent_name = "basic-rag"


@builtin_config(agent_name)
class RAGAgentConfig(PrecompiledConfig):
    def __init__(self):
        pass

    def forward(self, query: str) -> str:
        return "hello"


@builtin_indexer(agent_name)
class RAGIndexer(Indexer):
    def __init__(self, config: RAGAgentConfig):
        super().__init__(config)

    def index(self, contents: Any):
        pass


@builtin_agent(agent_name)
class RAGAgent(PrecompiledAgent):
    def __init__(self, config: RAGAgentConfig, indexer: RAGIndexer):
        super().__init__(config)
        self.indexer = indexer

    def forward(self, query: str) -> str:
        return "hello"
