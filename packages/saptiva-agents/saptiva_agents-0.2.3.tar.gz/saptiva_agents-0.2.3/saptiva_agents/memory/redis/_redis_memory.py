from autogen_ext.memory.redis import RedisMemoryConfig, RedisMemory


class RedisMemoryConfig(RedisMemoryConfig):
    """
    Configuration for Redis-based vector memory.

    This class defines the configuration options for using Redis as a vector memory store,
    supporting semantic memory. It allows customization of the Redis connection, index settings,
    similarity search parameters, and embedding model.
    """
    pass

class RedisMemory(RedisMemory):
    """
    Store and retrieve memory using vector similarity search powered by RedisVL.

    `RedisMemory` provides a vector-based memory implementation that uses RedisVL for storing and
    retrieving content based on semantic similarity or sequential order. It enhances agents with the
    ability to recall relevant information during conversations by leveraging vector embeddings to
    find similar content.

        This implementation requires the RedisVL extra to be installed. Install with:

        .. code-block:: bash

        Additionally, you will need access to a Redis instance.
        To run a local instance of redis in docker:

        .. code-block:: bash

            docker run -d --name redis -p 6379:6379 redis:8

        To download and run Redis locally:

        .. code-block:: bash

            curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
            echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
            sudo apt-get update  > /dev/null 2>&1
            sudo apt-get install redis-server  > /dev/null 2>&1
            redis-server --daemonize yes

    Args:
        config (RedisMemoryConfig | None): Configuration for the Redis memory.
            If None, defaults to a RedisMemoryConfig with recommended settings.

    """
    pass