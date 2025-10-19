from typing import Any

from vertexai import Client
from autogen_core import CancellationToken
from autogen_core.memory import (
    Memory,
    UpdateContextResult,
    MemoryContent,
    MemoryQueryResult,
    MemoryMimeType,
)
from autogen_core.model_context import ChatCompletionContext
from autogen_core.models import SystemMessage


class VertexaiMemory(Memory):
    """
    An implementation of the memory protocol for VertexAI Memory for Autogen
    Agents.
    """

    component_type = "memory"

    def __init__(
        self,
        api_resource_name: str,
        project_id: str,
        location: str,
        client: Client | None = None,
    ):
        self.api_resource_name = api_resource_name
        self.project_id = project_id
        self.location = location
        self.client = client

    async def vertexai_client(self) -> Client:
        """Initialize and return VertexAI client."""
        if self.client is None:
            self.client = Client(project=self.project_id, location=self.location)
        return self.client

    async def update_context(
        self, model_context: ChatCompletionContext
    ) -> UpdateContextResult:
        """Update chat context with memories."""
        contents = await self.query()

        results = contents.results

        if not results:
            return UpdateContextResult(memories=MemoryQueryResult(results=[]))

        memory_strings = [
            f"{i}. {str(memory.content)}" for i, memory in enumerate(results, 1)
        ]

        if memory_strings:
            memory_context = (
                "\nRelevant memory content (in chronological order):\n"
                + "\n".join(memory_strings)
                + "\n"
            )
            await model_context.add_message(SystemMessage(content=memory_context))

        return UpdateContextResult(memories=contents)

    async def add(
        self,
        content: MemoryContent,
        user_id: str,
        cancellation_token: CancellationToken | None = None,
    ) -> None:
        """Add to VertexAI memory."""
        if self.client is None:
            await self.vertexai_client()

        r = self.client.agent_engines.memories.generate(
            name=self.api_resource_name,
            direct_memories_source={
                "direct_memories": [{"fact": str(content.content)}]
            },
            scope={"app_name": self.api_resource_name, "user_id": user_id},
        )
        print(r)  # FIXED: Changed from print(s) to print(r)

    async def query(
        self,
        query: str | MemoryContent = "",
        user_id: str = "",
        cancellation_token: CancellationToken | None = None,
        **kwargs: Any,
    ) -> MemoryQueryResult:
        """Query vertex ai."""
        if self.client is None:
            await self.vertexai_client()

        if query != "":
            query_text = query if isinstance(query, str) else str(query.content)
            retrieved_memories = list(
                self.client.agent_engines.memories.retrieve(
                    name=self.api_resource_name,
                    scope={"app_name": self.api_resource_name, "user_id": user_id},
                    similarity_search_params={
                        "search_query": query_text,
                        "top_k": 3,
                    },
                )
            )
            print(retrieved_memories)
        else:
            retrieved_memories = list(
                self.client.agent_engines.memories.retrieve(
                    name=self.api_resource_name,
                    scope={"user_id": user_id},
                )
            )

        results = [
            MemoryContent(
                content=retrieved_memory.memory.fact, mime_type=MemoryMimeType.TEXT
            )
            for retrieved_memory in retrieved_memories
        ]

        return MemoryQueryResult(results=results)

    async def clear(self) -> None:
        """Clear all memory content."""
        if self.client is None:
            await self.vertexai_client()
        self.client.delete(force=True)

    async def close(self) -> None:
        """Cleanup resources if needed."""
        pass
