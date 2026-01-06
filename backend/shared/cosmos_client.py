import os
import logging
from typing import Optional, List, Dict, Any, Type, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class CosmosService:
    """Cosmos DB service with Pydantic model support (Azure-safe, lazy init)"""

    # Container definitions with partition keys
    CONTAINERS = {
        "Users": "/userId",
        "LessonPlans": "/userId",
        "Lessons": "/userId",
        "Quizzes": "/userId",
        "QuizAttempts": "/userId",
        "TutorSessions": "/userId",
        "Progress": "/userId",
    }

    def __init__(self, use_async: bool = False):
        # Configuration only — NO NETWORK CALLS
        self.connection_string = os.getenv("COSMOS_CONNECTION_STRING")
        self.database_name = os.getenv("COSMOS_DB_NAME", "learning-platform-db")

        if not self.connection_string:
            raise ValueError("COSMOS_CONNECTION_STRING environment variable not set")

        self.use_async = use_async
        self._client = None
        self._database = None

    # ---------- Lazy Azure-safe initialization ----------

    def _get_client(self):
        if self._client is None:
            if self.use_async:
                self._client = AsyncCosmosClient.from_connection_string(
                    self.connection_string
                )
            else:
                self._client = CosmosClient.from_connection_string(
                    self.connection_string
                )
        return self._client

    def _get_database(self):
        if self._database is None:
            client = self._get_client()
            self._database = client.get_database_client(self.database_name)
        return self._database

    def _get_container(self, container_name: str):
        db = self._get_database()
        return db.get_container_client(container_name)

    # ---------- Model helpers ----------

    def _model_to_dict(self, model: BaseModel) -> Dict[str, Any]:
        return model.model_dump(mode="json", exclude_none=False)

    def _dict_to_model(self, data: Dict[str, Any], model_class: Type[T]) -> T:
        return model_class.model_validate(data)

    # ---------- CRUD Operations ----------

    def create_item(self, container: str, item: BaseModel) -> BaseModel:
        try:
            container_client = self._get_container(container)
            item_dict = self._model_to_dict(item)
            result = container_client.create_item(body=item_dict)
            logger.info(f"Created item in {container}: {result.get('id')}")
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
        model_class: Type[T],
    ) -> Optional[T]:
        try:
            container_client = self._get_container(container)
            result = container_client.read_item(
                item=item_id,
                partition_key=partition_key,
            )
            return self._dict_to_model(result, model_class)
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Item not found: {item_id} in {container}")
            return None
        except Exception as e:
            logger.error(f"Error getting item from {container}: {e}")
            raise

    def update_item(self, container: str, item: BaseModel) -> BaseModel:
        try:
            container_client = self._get_container(container)
            item_dict = self._model_to_dict(item)
            result = container_client.replace_item(
                item=item.id,
                body=item_dict,
            )
            logger.info(f"Updated item in {container}: {result.get('id')}")
            return self._dict_to_model(result, type(item))
        except exceptions.CosmosResourceNotFoundError:
            logger.error(f"Item not found for update: {item.id}")
            raise
        except Exception as e:
            logger.error(f"Error updating item in {container}: {e}")
            raise

    def upsert_item(self, container: str, item: BaseModel) -> BaseModel:
        try:
            container_client = self._get_container(container)
            item_dict = self._model_to_dict(item)
            result = container_client.upsert_item(body=item_dict)
            logger.info(f"Upserted item in {container}: {result.get('id')}")
            return self._dict_to_model(result, type(item))
        except Exception as e:
            logger.error(f"Error upserting item in {container}: {e}")
            raise

    def delete_item(
        self,
        container: str,
        item_id: str,
        partition_key: str,
    ) -> bool:
        try:
            container_client = self._get_container(container)
            container_client.delete_item(
                item=item_id,
                partition_key=partition_key,
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
        parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Any]:
        try:
            container_client = self._get_container(container)

            query_kwargs = {
                "query": query,
                "enable_cross_partition_query": partition_key is None,
            }

            if partition_key:
                query_kwargs["partition_key"] = partition_key

            if parameters:
                query_kwargs["parameters"] = parameters

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
        item_type: Optional[str] = None,
    ) -> List[T]:
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
            parameters=parameters,
        )

    def get_items_by_filter(
        self,
        container: str,
        filters: Dict[str, Any],
        partition_key: Optional[str] = None,
        model_class: Optional[Type[T]] = None,
    ) -> List[Any]:
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
            parameters=parameters,
        )

    def close(self):
        if self._client and hasattr(self._client, "close"):
            self._client.close()


# ---------- Singleton (FastAPI-safe) ----------

_cosmos_service: Optional[CosmosService] = None


def get_cosmos_service() -> CosmosService:
    global _cosmos_service
    if _cosmos_service is None:
        _cosmos_service = CosmosService()
    return _cosmos_service
