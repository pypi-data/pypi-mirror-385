"""
Memory Search Module for VertexAI Integration.

This module provides a SearchMemory class that enables semantic search
and retrieval of stored memories from Google Cloud's VertexAI platform.
It leverages VertexAI's agent engines to perform similarity-based memory
queries, allowing applications to retrieve contextually relevant information
based on natural language queries.

The module supports flexible configuration through a Pydantic v2 model,
allowing direct parameter passing or environment variable fallback, making
it suitable for various deployment scenarios including local development
and production environments.

Environment Variables (used by SearchMemoryConfig):
    VERTEX_PROJECT_ID: Google Cloud project identifier
    VERTEX_LOCATION: Google Cloud region (e.g., 'us-central1')
    VERTEX_USER_ID: Unique identifier for the user session
    VERTEX_API_RESOURCE_NAME: Name of the VertexAI memory resource

Example:
    Basic usage with direct parameters:
        >>> config = SearchMemoryConfig(
        ...     project_id="my-project",
        ...     location="us-central1",
        ...     user_id="user123",
        ...     api_resource_name="my-memory-store"
        ... )
        >>> search = SearchMemory(config=config)
        >>> results = search("What did I say about Python?", top_k=3)

    Usage with environment variables:
        >>> # Set environment variables first (e.g., os.environ['VERTEX_PROJECT_ID'] = 'my-project')
        >>> search = SearchMemory() # Will automatically load config from environment
        >>> results = search("Tell me about my preferences")
"""

import os
from typing import List, Optional, Any

from pydantic import BaseModel, Field, field_validator, FieldValidationInfo

from vertexai import Client


class SearchMemoryConfig(BaseModel):
    """
    Pydantic v2 configuration model for SearchMemory.

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


class SearchMemory:
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
        config: Optional[SearchMemoryConfig] = None,
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
            >>> config_obj = SearchMemoryConfig(
            ...     project_id="my-gcp-project",
            ...     location="us-central1",
            ...     user_id="user_12345",
            ...     api_resource_name="chat-memories"
            ... )
            >>> search = SearchMemory(config=config_obj)

            >>> # Using environment variables (Pydantic will load and validate)
            >>> import os
            >>> os.environ['VERTEX_PROJECT_ID'] = 'my-gcp-project'
            >>> os.environ['VERTEX_LOCATION'] = 'us-central1'
            >>> os.environ['VERTEX_USER_ID'] = 'user_abc'
            >>> os.environ['VERTEX_API_RESOURCE_NAME'] = 'my-mem-store'
            >>> search_from_env = SearchMemory()

            >>> # Using kwargs for direct config (less preferred for complex apps)
            >>> search_from_kwargs = SearchMemory(
            ...     project_id="another-project",
            ...     location="us-central1",
            ...     user_id="user_xyz",
            ...     api_resource_name="another-mem-store"
            ... )
        """
        if config is None:
            # If no config object is passed, try to create one.
            # Kwargs will be passed to the config model constructor, allowing
            # convenient initialization like SearchMemory(project_id="...")
            self._config = SearchMemoryConfig(**kwargs)
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

    def __call__(self, query: str, top_k: int = 5) -> List[str]:
        """
        Perform semantic search to retrieve relevant memories.

        This method implements the callable interface, allowing the instance
        to be invoked like a function. It performs a similarity-based search
        across stored memories and returns the most semantically relevant
        results based on the input query.

        The search is scoped to the specific user and application context
        configured during initialization, ensuring isolation between
        different users and applications sharing the same VertexAI resource.

        Args:
            query (str): The natural language search query. This should be
                a descriptive phrase or question about the information you
                want to retrieve. The semantic search will find memories
                with similar meaning, not just exact keyword matches.
                Example: "What are my dietary preferences?"
            top_k (int, optional): Maximum number of memory results to
                return, ordered by relevance score. Defaults to 5.
                Larger values provide more context but may include less
                relevant results. Valid range depends on VertexAI limits.

        Returns:
            List[str]: A list of memory facts (strings) ordered by
                relevance to the query. Each string represents a discrete
                piece of stored information. The list may contain fewer
                than top_k items if insufficient relevant memories exist.
                Returns an empty list if no relevant memories are found.

        Side Effects:
            On first call, initializes the VertexAI client connection
            via initialize_client() if not already initialized.

        Example:
            >>> # Assuming 'search' instance is already created with valid config
            >>> results = search("What programming languages do I like?")
            >>> for memory in results:
            ...     print(f"- {memory}")
            - User prefers Python for data analysis
            - User is learning Rust for systems programming

        Note:
            The quality of results depends on:
            - The quality and quantity of stored memories
            - The specificity of the search query
            - The semantic model used by VertexAI
        """
        # Lazy initialization: only create client when first search
        # is performed. This avoids connection overhead during setup.
        if self.client is None:
            self.initialize_client()

        # Retrieve memories using VertexAI's semantic search API.
        # The scope parameter ensures we only access memories for
        # the specific user and application context.
        retrieved_memories = list(
            self.client.agent_engines.memories.retrieve(
                # Resource identifier for the memory store
                name=self.api_resource_name,
                # Scope limits results to specific user and app context,
                # preventing cross-contamination of user data
                scope={"app_name": self.api_resource_name, "user_id": self.user_id},
                # Parameters controlling the similarity search behavior
                similarity_search_params={
                    "search_query": query,
                    "top_k": top_k,  # Limit number of results
                },
            )
        )

        # Extract just the fact strings from the memory objects.
        # The API returns complex objects, but we simplify to strings
        # for easier consumption by calling code.
        retrieved_memories = [memory.memory.fact for memory in retrieved_memories]
        return retrieved_memories
