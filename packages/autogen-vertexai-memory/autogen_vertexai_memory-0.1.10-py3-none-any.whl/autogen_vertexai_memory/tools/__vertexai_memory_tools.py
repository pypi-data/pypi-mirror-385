import os
import asyncio
from typing import List, Optional, Any

from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
from autogen_core import CancellationToken
from autogen_core.tools import BaseTool

from vertexai import Client


class SearchQueryInputArgs(BaseModel):
    query: str = Field(
        ..., description="Semantic search query to retrive information about user."
    )
    top_k: int = Field(
        5, description="The maximum number of relevant memories to retrieve."
    )


class SearchQueryReturn(BaseModel):
    results: List[str] = Field(
        ..., description="Semantic search query results from Vertex AI Memory Bank."
    )


class SearchVertexaiMemoryToolConfig(BaseModel):
    """
    This model defines and validates all required configuration parameters
    for connecting to and using VertexAI for memory search. It ensures
    type safety and provides clear documentation.

    Attributes:
        project_id (str): Google Cloud project ID. Falls back to
            `VERTEX_PROJECT_ID` environment variable.
        location (str): Google Cloud region. Falls back to
            `VERTEX_LOCATION` environment variable.
        user_id (str): Unique identifier for the user. Falls back to
            `VERTEX_USER_ID` environment variable.
        api_resource_name (str): Name of the VertexAI memory resource.
            Falls back to `VERTEX_API_RESOURCE_NAME` environment variable.
    """

    project_id: str = Field(
        default_factory=lambda: os.getenv("VERTEX_PROJECT_ID", ""),
        description="Google Cloud project ID",
    )
    location: str = Field(
        default_factory=lambda: os.getenv("VERTEX_LOCATION", ""),
        description="GCP region where the memory resource is located",
    )
    user_id: str = Field(
        default_factory=lambda: os.getenv("VERTEX_USER_ID", ""),
        description="Unique identifier for the user associated with the memory",
    )
    api_resource_name: str = Field(
        default_factory=lambda: os.getenv("VERTEX_API_RESOURCE_NAME", ""),
        description="Full resource name of the VertexAI memory",
    )

    @field_validator("project_id", "location", "user_id", "api_resource_name")
    @classmethod
    def validate_not_empty(cls, v: str, info: FieldValidationInfo) -> str:
        """
        Validate that required fields are not empty strings.

        Args:
            v: The field value to validate.
            info: Provides context about the field being validated (Pydantic v2).

        Returns:
            The validated value.

        Raises:
            ValueError: If the field is empty.
        """
        if not v or not v.strip():
            env_var_map = {
                "project_id": "VERTEX_PROJECT_ID",
                "location": "VERTEX_LOCATION",
                "user_id": "VERTEX_USER_ID",
                "api_resource_name": "VERTEX_API_RESOURCE_NAME",
            }
            env_var = env_var_map.get(info.field_name, info.field_name.upper())
            raise ValueError(
                f"{info.field_name} must be provided or {env_var} "
                f"environment variable must be set"
            )
        return v


class SearchVertexaiMemoryTool(BaseTool[SearchQueryInputArgs, SearchQueryReturn]):
    """
    Semantic memory search interface for VertexAI.

    This class provides a high-level interface to search and retrieve
    memories stored in Google Cloud's VertexAI platform using semantic
    similarity. It maintains a stateful connection to VertexAI and
    supports scoped memory retrieval per user and application.

    The class uses a Pydantic v2 `SearchMemoryConfig` for robust configuration
    management and implements lazy initialization of the VertexAI client,
    establishing the connection only when the first search is performed.
    This approach optimizes resource usage and connection management.

    Attributes:
        project_id (str): The Google Cloud project ID where VertexAI
            resources are hosted.
        location (str): The geographic location of the VertexAI service
            (e.g., 'us-central1', 'europe-west1').
        user_id (str): Unique identifier for the user whose memories
            are being queried. Used to scope memory retrieval.
        api_resource_name (str): The name of the VertexAI memory resource
            that stores the memories. Also used as the app_name in scope.
        client (Optional[Client]): The initialized VertexAI client instance.
            None until initialize_client() is called.

    Raises:
        ValueError: If any required configuration parameter is missing,
            as validated by `SearchMemoryConfig`.
    """

    def __init__(
        self,
        config: Optional[SearchVertexaiMemoryToolConfig] = None,
        **kwargs: Any,  # For backward compatibility if args are passed, but config is preferred.
    ):
        """
        Initialize the SearchMemory instance with VertexAI configuration.

        This constructor accepts configuration primarily through a
        `SearchMemoryConfig` object. If `config` is None, it attempts to
        load configuration from environment variables by instantiating
        `SearchMemoryConfig` without arguments.

        The client connection is not established during initialization;
        instead, it uses lazy initialization when the first search is
        performed.

        Args:
            config (Optional[SearchMemoryConfig]): Pre-validated configuration
                object. If None, configuration will be loaded from
                environment variables (and validated) when the instance is
                created.
            **kwargs: Allows for direct passing of config values for convenience
                      (e.g., `SearchMemory(project_id="abc")`), which will be
                      used to construct a `SearchMemoryConfig` object if `config`
                      is not provided. However, passing a `config` object is
                      the recommended approach for clarity and validation.

        Raises:
            pydantic.ValidationError: If `config` is None and environment
                variables are not set correctly for `SearchMemoryConfig`.

        Example:
            >>> # Using a config object
            >>> config_obj = SearchVertexaiMemoryToolConfig( # Changed from SearchMemoryConfig
            ...     project_id="my-gcp-project",
            ...     location="us-central1",
            ...     user_id="user_12345",
            ...     api_resource_name="chat-memories"
            ... )
            >>> search = SearchVertexaiMemoryTool(config=config_obj) # Changed from SearchMemory

            >>> # Using environment variables (Pydantic will load and validate)
            >>> import os
            >>> os.environ['VERTEX_PROJECT_ID'] = 'my-gcp-project'
            >>> os.environ['VERTEX_LOCATION'] = 'us-central1'
            >>> os.environ['VERTEX_USER_ID'] = 'user_abc'
            >>> os.environ['VERTEX_API_RESOURCE_NAME'] = 'my-mem-store'
            >>> search_from_env = SearchVertexaiMemoryTool() # Changed from SearchMemory

            >>> # Using kwargs for direct config (less preferred for complex apps)
            >>> search_from_kwargs = SearchVertexaiMemoryTool( # Changed from SearchMemory
            ...     project_id="another-project",
            ...     location="us-central1",
            ...     user_id="user_xyz",
            ...     api_resource_name="another-mem-store"
            ... )
        """
        super().__init__(
            args_type=SearchQueryInputArgs,
            return_type=SearchQueryReturn,
            name="search_vertexai_memory_tool",
            description="Perform a search with given parameters using vertexai memory bank.",
        )
        if config is None:
            # If no config object is passed, try to create one.
            # Kwargs will be passed to the config model constructor, allowing
            # convenient initialization like SearchMemory(project_id="...")
            self._config = SearchVertexaiMemoryToolConfig(**kwargs)
        else:
            self._config = config

        self.project_id = self._config.project_id
        self.location = self._config.location
        self.user_id = self._config.user_id
        self.api_resource_name = self._config.api_resource_name

        self.client: Optional[Client] = None  # Client is initialized lazily

    def initialize_client(self):
        """
        Establish connection to the VertexAI service.

        This method creates and initializes the VertexAI Client instance
        using the configured project_id and location. The client provides
        access to VertexAI's agent engines and memory retrieval capabilities.

        The initialization is performed lazily (only when needed) to:
        - Reduce startup time and resource usage
        - Avoid connection errors during object construction
        - Allow object serialization without active connections

        This method is called automatically by __call__ if the client
        hasn't been initialized yet, so direct invocation is rarely needed.

        Side Effects:
            Sets self.client to an initialized Client instance.

        Note:
            This method assumes valid GCP credentials are available in
            the environment (via Application Default Credentials or
            service account key file).
        """
        self.client = Client(project=self.project_id, location=self.location)

    async def run(
        self,
        args: SearchQueryInputArgs,
        cancellation_token: CancellationToken | None = None,
    ) -> SearchQueryReturn:
        if self.client is None:
            self.initialize_client()

        # Helper function to encapsulate the synchronous retrieve call and list conversion.
        def _retrieve_memories_sync():
            return list(
                self.client.agent_engines.memories.retrieve(
                    name=self.api_resource_name,
                    scope={"app_name": self.api_resource_name, "user_id": self.user_id},
                    similarity_search_params={
                        "search_query": args.query,
                        "top_k": args.top_k,
                    },
                )
            )

        retrieved_memories_list = await asyncio.to_thread(_retrieve_memories_sync)

        fact_strings = [memory.memory.fact for memory in retrieved_memories_list]
        return SearchQueryReturn(results=fact_strings)
