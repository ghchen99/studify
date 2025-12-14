from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Type, TypeVar
from pydantic import BaseModel
import logging

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class CosmosService:
    """Cosmos DB service with Pydantic model support"""
    
    # Container definitions with partition keys
    CONTAINERS = {
        'Users': '/userId',
        'LessonPlans': '/userId',
        'Lessons': '/userId',
        'Quizzes': '/userId',
        'QuizAttempts': '/userId',
        'TutorSessions': '/userId',
        'Progress': '/userId'
    }
    
    def __init__(self, use_async: bool = False):
        """Initialize Cosmos client with auto-create containers"""
        self.endpoint = os.getenv("COSMOS_DB_ENDPOINT")
        self.database_name = os.getenv("COSMOS_DB_NAME", "learning-platform-db")
        
        if not self.endpoint:
            raise ValueError("COSMOS_DB_ENDPOINT environment variable not set")
        
        # Use DefaultAzureCredential for authentication
        credential = DefaultAzureCredential()
        
        if use_async:
            self.client = AsyncCosmosClient(self.endpoint, credential)
        else:
            self.client = CosmosClient(self.endpoint, credential)
        
        self.use_async = use_async
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database and containers if they don't exist"""
        try:
            # Create database if not exists
            self.database = self.client.create_database_if_not_exists(
                id=self.database_name
            )
            logger.info(f"Database '{self.database_name}' ready")
            
            # Create containers if they don't exist
            for container_name, partition_key_path in self.CONTAINERS.items():
                try:
                    self.database.create_container_if_not_exists(
                        id=container_name,
                        partition_key=PartitionKey(path=partition_key_path)
                    )
                    logger.info(f"Container '{container_name}' ready")
                except exceptions.CosmosHttpResponseError as e:
                    logger.error(f"Error creating container {container_name}: {e}")
                    raise
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _get_container(self, container: str):
        """Get container client"""
        return self.database.get_container_client(container)
    
    def _model_to_dict(self, model: BaseModel) -> Dict[str, Any]:
        """Convert Pydantic model to dict with datetime serialization"""
        return model.model_dump(mode='json', exclude_none=False)
    
    def _dict_to_model(self, data: Dict[str, Any], model_class: Type[T]) -> T:
        """Convert dict to Pydantic model"""
        return model_class.model_validate(data)
    
    # CRUD Operations
    
    def create_item(self, container: str, item: BaseModel) -> BaseModel:
        """Create an item from Pydantic model"""
        try:
            container_client = self._get_container(container)
            item_dict = self._model_to_dict(item)
            result = container_client.create_item(body=item_dict)
            logger.info(f"Created item in {container}: {result['id']}")
            return self._dict_to_model(result, type(item))
        except exceptions.CosmosResourceExistsError:
            logger.error(f"Item already exists: {item.id}")
            raise
        except Exception as e:
            logger.error(f"Error creating item in {container}: {e}")
            raise
    
    def get_item(
        self, 
        container: str, 
        item_id: str, 
        partition_key: str,
        model_class: Type[T]
    ) -> Optional[T]:
        """Get an item and return as Pydantic model"""
        try:
            container_client = self._get_container(container)
            result = container_client.read_item(
                item=item_id,
                partition_key=partition_key
            )
            return self._dict_to_model(result, model_class)
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Item not found: {item_id} in {container}")
            return None
        except Exception as e:
            logger.error(f"Error getting item from {container}: {e}")
            raise
    
    def update_item(self, container: str, item: BaseModel) -> BaseModel:
        """Update an item from Pydantic model"""
        try:
            container_client = self._get_container(container)
            item_dict = self._model_to_dict(item)
            
            # Extract partition key value from item
            partition_key_path = self.CONTAINERS[container].lstrip('/')
            partition_key = item_dict.get(partition_key_path)
            
            result = container_client.replace_item(
                item=item.id,
                body=item_dict,
                partition_key=partition_key
            )
            logger.info(f"Updated item in {container}: {result['id']}")
            return self._dict_to_model(result, type(item))
        except exceptions.CosmosResourceNotFoundError:
            logger.error(f"Item not found for update: {item.id}")
            raise
        except Exception as e:
            logger.error(f"Error updating item in {container}: {e}")
            raise
    
    def upsert_item(self, container: str, item: BaseModel) -> BaseModel:
        """Create or update an item"""
        try:
            container_client = self._get_container(container)
            item_dict = self._model_to_dict(item)
            result = container_client.upsert_item(body=item_dict)
            logger.info(f"Upserted item in {container}: {result['id']}")
            return self._dict_to_model(result, type(item))
        except Exception as e:
            logger.error(f"Error upserting item in {container}: {e}")
            raise
    
    def delete_item(
        self, 
        container: str, 
        item_id: str, 
        partition_key: str
    ) -> bool:
        """Delete an item"""
        try:
            container_client = self._get_container(container)
            container_client.delete_item(
                item=item_id,
                partition_key=partition_key
            )
            logger.info(f"Deleted item from {container}: {item_id}")
            return True
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Item not found for deletion: {item_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting item from {container}: {e}")
            raise
    
    def query_items(
        self,
        container: str,
        query: str,
        partition_key: Optional[str] = None,
        model_class: Optional[Type[T]] = None,
        parameters: Optional[List[Dict[str, Any]]] = None
    ) -> List[T]:
        """Query items with optional Pydantic model conversion"""
        try:
            container_client = self._get_container(container)
            
            query_kwargs = {
                'query': query,
                'enable_cross_partition_query': partition_key is None
            }
            
            if partition_key:
                query_kwargs['partition_key'] = partition_key
            
            if parameters:
                query_kwargs['parameters'] = parameters
            
            results = list(container_client.query_items(**query_kwargs))
            
            if model_class:
                return [self._dict_to_model(item, model_class) for item in results]
            return results
            
        except Exception as e:
            logger.error(f"Error querying items from {container}: {e}")
            raise
    
    def get_items_by_user(
        self,
        container: str,
        user_id: str,
        model_class: Type[T],
        item_type: Optional[str] = None
    ) -> List[T]:
        """Get all items for a user, optionally filtered by type"""
        query = "SELECT * FROM c WHERE c.userId = @userId"
        parameters = [{"name": "@userId", "value": user_id}]
        
        if item_type:
            query += " AND c.type = @type"
            parameters.append({"name": "@type", "value": item_type})
        
        return self.query_items(
            container=container,
            query=query,
            partition_key=user_id,
            model_class=model_class,
            parameters=parameters
        )
    
    def get_items_by_filter(
        self,
        container: str,
        filters: Dict[str, Any],
        partition_key: Optional[str] = None,
        model_class: Optional[Type[T]] = None
    ) -> List[T]:
        """Get items with dynamic filters"""
        conditions = []
        parameters = []
        
        for i, (key, value) in enumerate(filters.items()):
            param_name = f"@param{i}"
            conditions.append(f"c.{key} = {param_name}")
            parameters.append({"name": param_name, "value": value})
        
        query = f"SELECT * FROM c WHERE {' AND '.join(conditions)}"
        
        return self.query_items(
            container=container,
            query=query,
            partition_key=partition_key,
            model_class=model_class,
            parameters=parameters
        )
    
    def close(self):
        """Close the client connection"""
        if hasattr(self.client, 'close'):
            self.client.close()


# Create a singleton instance
_cosmos_service: Optional[CosmosService] = None

def get_cosmos_service() -> CosmosService:
    """Get or create the Cosmos service singleton"""
    global _cosmos_service
    if _cosmos_service is None:
        _cosmos_service = CosmosService()
    return _cosmos_service