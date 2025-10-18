import os
import threading
import time
import pymongo
from pymongo import MongoClient, ReadPreference, WriteConcern
from pymongo.collection import Collection

class MongoDBClient:
    """
    MongoDBClient is a handler for managing MongoDB connections safely in forking environments.
    It lazily initializes the MongoClient to avoid fork-safety warnings and supports optimized
    connection strings for both single server and replica set configurations with automatic
    retry on failover. Provides dictionary-like access to collections within a specified user
    namespace and includes a method to execute operations with automatic retry on connection
    failures. Also includes a static method to ensure the existence of a specific index on a collection.
    """

    # Process-local connection pools to handle Gunicorn worker isolation
    _connection_pools = {}
    _pool_lock = threading.Lock()
    _process_id = os.getpid()  # Track current process ID
    
    # Connection metrics for monitoring
    _connection_metrics = {
        'total_connections_created': 0,
        'connection_failures': 0,
        'connection_retries': 0,
        'active_connections': 0,
        'last_connection_error': None,
        'last_connection_time': None
    }

    def __init__(self, user: str = 'SharedData') -> None:
        """
        Initialize MongoDB client handler by constructing the appropriate connection string.
        
        This constructor sets up the MongoDB connection string based on environment variables.
        If the environment variable 'MONGODB_REPLICA_SET' is not present, it creates a connection
        string for a single MongoDB server. Otherwise, it creates a connection string optimized
        for a replica set with failover and retry options enabled.
        
        Args:
            user (str): The database user namespace. Defaults to 'SharedData'.
        
        Attributes:
            _user (str): The user namespace for the database.
            mongodb_conn_str (str): The constructed MongoDB connection string.
            _client: Placeholder for the MongoDB client instance, initialized on first use.
        """
        self._user = user
        mongodb_host = os.environ["MONGODB_HOST"]
        if ':' not in mongodb_host:
            mongodb_host += ':' + os.environ.get("MONGODB_PORT", "27017")

        # Build connection string inside __init__ with correct indentation
        if 'MONGODB_REPLICA_SET' not in os.environ:
            # Single server connection with optimized settings
            self.mongodb_conn_str = (
                f'mongodb://{os.environ["MONGODB_USER"]}:'
                f'{os.environ["MONGODB_PWD"]}@'
                f'{mongodb_host}/'
                f'?retryWrites=true'
                f'&retryReads=true'
                f'&maxPoolSize=100'
                f'&minPoolSize=20'
                f'&maxIdleTimeMS=300000'
                f'&serverSelectionTimeoutMS=5000'
                f'&connectTimeoutMS=10000'
                f'&socketTimeoutMS=300000'
                f'&compressors=snappy,zlib'
            )
        else:
            # Replica set connection string optimized for performance and failover
            auth_db = os.environ.get("MONGODB_AUTH_DB", "admin")
            self.mongodb_conn_str = (
                f'mongodb://{os.environ["MONGODB_USER"]}:'
                f'{os.environ["MONGODB_PWD"]}@'
                f'{mongodb_host}/'
                f'?replicaSet={os.environ["MONGODB_REPLICA_SET"]}'
                f'&authSource={auth_db}'
                f'&retryWrites=true'
                f'&retryReads=true'
                f'&readPreference=secondaryPreferred'
                f'&w=1'
                f'&maxPoolSize=100'
                f'&minPoolSize=20'
                f'&maxIdleTimeMS=300000'
                f'&serverSelectionTimeoutMS=5000'
                f'&connectTimeoutMS=10000'
                f'&socketTimeoutMS=300000'
                f'&compressors=snappy,zlib'
            )
        self._client = None  # Client will be created on first access

    @property
    def client(self) -> MongoClient:
        """
        Get a process-safe MongoDB client with connection validation and automatic recovery.
        
        This property ensures that each process gets its own connection pool to avoid
        fork-safety issues with Gunicorn workers. It validates the connection with a ping
        and recreates it if necessary.
        
        Returns:
            MongoClient: A validated MongoDB client instance.
        """
        current_pid = os.getpid()
        
        # Reset connection pool if we're in a different process (forked)
        if current_pid != self._process_id:
            with self._pool_lock:
                self._connection_pools.clear()
                self._process_id = current_pid
                self._client = None
        
        # Get or create process-local client
        with self._pool_lock:
            pool_key = f"{self.mongodb_conn_str}_{current_pid}"
            
            if pool_key not in self._connection_pools or self._connection_pools[pool_key] is None:
                try:
                    # Note: Write concern must be set via URI or collection/database options, not here
                    self._connection_pools[pool_key] = MongoClient(
                        self.mongodb_conn_str,
                        # Additional performance options
                        tz_aware=False,  # Return naive datetime objects without timezone info
                        connect=False  # Lazy connection - only connect when needed
                    )
                    
                    # Update metrics
                    self._connection_metrics['total_connections_created'] += 1
                    self._connection_metrics['last_connection_time'] = time.time()
                    self._connection_metrics['active_connections'] += 1
                    
                except Exception as e:
                    self._connection_metrics['connection_failures'] += 1
                    self._connection_metrics['last_connection_error'] = str(e)
                    raise
            
            client = self._connection_pools[pool_key]
            
            # Validate connection with a quick ping
            try:
                client.admin.command('ping', maxTimeMS=5000)
                self._client = client
                return client
            except Exception as e:
                # Connection failed, recreate it
                self._connection_metrics['connection_failures'] += 1
                self._connection_metrics['last_connection_error'] = str(e)
                
                try:
                    client.close()
                    self._connection_metrics['active_connections'] = max(0, self._connection_metrics['active_connections'] - 1)
                except:
                    pass
                self._connection_pools[pool_key] = None
                # Recursive call to recreate connection
                return self.client

    @client.setter
    def client(self, value: MongoClient) -> None:
        """
        Set the MongoDB client instance.
        
        Parameters:
            value (MongoClient): An instance of MongoClient to be used as the database client.
        
        Returns:
            None
        """
        self._client = value

    def __getitem__(self, collection_name: str) -> Collection:
        """
        Retrieve a MongoDB collection from the user's database using dictionary-like access.
        
        Args:
            collection_name (str): The name of the collection to access.
        
        Returns:
            Collection: The MongoDB collection corresponding to the given name.
        """
        return self.client[self._user][collection_name]
    
    def execute_with_retry(self, operation, max_retries: int = 3, delay: float = 0.5):
        """
        Execute a MongoDB operation with automatic retries on connection-related failures.
        
        This method attempts to execute the provided MongoDB operation callable. If the operation
        raises a connection-related exception (such as ServerSelectionTimeoutError, NetworkTimeout,
        or AutoReconnect), it will retry the operation up to `max_retries` times with exponential
        backoff delay between attempts. On each retry, the MongoDB client is closed and reset to
        force a fresh connection.
        
        Args:
            operation (callable): A callable that performs the MongoDB operation.
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
            delay (float, optional): Initial delay between retries in seconds. Defaults to 0.5.
        
        Returns:
            The result of the MongoDB operation if successful.
        
        Raises:
            Exception: Re-raises the last connection-related exception if all retries fail.
            Exception: Immediately raises any non-connection-related exceptions encountered during operation.
        """
        import pymongo.errors
        
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                return operation()
            except (pymongo.errors.ServerSelectionTimeoutError, 
                    pymongo.errors.NetworkTimeout,
                    pymongo.errors.AutoReconnect,
                    pymongo.errors.ConnectionFailure) as e:
                last_exception = e
                if attempt < max_retries:
                    # Reset client connection on failure
                    current_pid = os.getpid()
                    pool_key = f"{self.mongodb_conn_str}_{current_pid}"
                    with self._pool_lock:
                        if pool_key in self._connection_pools:
                            try:
                                self._connection_pools[pool_key].close()
                            except:
                                pass
                            self._connection_pools[pool_key] = None
                    
                    # Exponential backoff
                    time.sleep(delay * (2 ** attempt))
                    continue
            except Exception as e:
                # Non-connection related exception, re-raise immediately
                raise e
                
        # All retries exhausted
        raise last_exception
        
    @classmethod
    def get_connection_metrics(cls):
        """
        Get current connection metrics for monitoring and debugging.
        
        Returns:
            dict: Dictionary containing connection pool metrics including:
                - total_connections_created: Total number of connections created
                - connection_failures: Number of connection failures
                - connection_retries: Number of retry attempts
                - active_connections: Current number of active connections
                - last_connection_error: Last connection error message
                - last_connection_time: Timestamp of last connection creation
                - pool_size: Current size of connection pool
        """
        with cls._pool_lock:
            metrics = cls._connection_metrics.copy()
            metrics['pool_size'] = len(cls._connection_pools)
            metrics['process_id'] = cls._process_id
            return metrics
    
    @classmethod
    def reset_connection_metrics(cls):
        """Reset all connection metrics to zero."""
        with cls._pool_lock:
            cls._connection_metrics = {
                'total_connections_created': 0,
                'connection_failures': 0,
                'connection_retries': 0,
                'active_connections': 0,
                'last_connection_error': None,
                'last_connection_time': None
            }
    
    @classmethod
    def close_all_connections(cls):
        """
        Close all connections in the pool and reset metrics.
        Useful for cleanup during shutdown or testing.
        """
        with cls._pool_lock:
            for pool_key, client in cls._connection_pools.items():
                if client:
                    try:
                        client.close()
                    except:
                        pass
            cls._connection_pools.clear()
            cls._connection_metrics['active_connections'] = 0
    
    def get_server_status(self):
        """
        Get MongoDB server status for monitoring.
        
        Returns:
            dict: Server status information including connections, operations, etc.
        """
        try:
            return self.client.admin.command('serverStatus')
        except Exception as e:
            return {'error': str(e)}
    
    def get_replica_set_status(self):
        """
        Get replica set status if connected to a replica set.
        
        Returns:
            dict: Replica set status or error information.
        """
        try:
            return self.client.admin.command('replSetGetStatus')
        except Exception as e:
            return {'error': str(e)}
        
    @staticmethod
    def ensure_index(coll, index_fields, **kwargs):
        """
        Ensure that a specified index exists on the given MongoDB collection.
        
        This method checks if an index with the specified fields and options already exists on the collection.
        If the index does not exist, it creates the index using the provided fields and options.
        
        Parameters:
            coll (pymongo.collection.Collection): The MongoDB collection to operate on.
            index_fields (list of tuples): A list of (field, direction) pairs specifying the index keys,
                e.g., [('status', pymongo.ASCENDING)].
            **kwargs: Additional keyword arguments to pass to the create_index method, such as 'name' or 'unique'.
        
        Returns:
            None
        """
        existing_indexes = coll.index_information()

        # Normalize input index spec for comparison
        target_index = pymongo.helpers._index_list(index_fields)

        for index_name, index_data in existing_indexes.items():
            if pymongo.helpers._index_list(index_data['key']) == target_index:
                return  # Index already exists

        coll.create_index(index_fields, **kwargs)