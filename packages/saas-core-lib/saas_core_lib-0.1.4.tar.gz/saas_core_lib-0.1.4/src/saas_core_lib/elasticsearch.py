"""
Elasticsearch Client Configuration
Centralized Elasticsearch connection management
"""

import logging
from functools import lru_cache
from typing import Optional, Dict, Any
from elasticsearch import AsyncElasticsearch 

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ElasticsearchManager:
    """Elasticsearch client wrapper with connection management"""
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self._client: Optional[AsyncElasticsearch] = None
        self._connected = False
    
    @property
    def client(self) -> AsyncElasticsearch:
        """Get Elasticsearch client instance"""
        if not self._client:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self) -> AsyncElasticsearch:
        """Create Elasticsearch client with configuration"""
        try:
            # Elasticsearch configuration from settings
            es_config = {
                "hosts": [settings.ELASTICSEARCH_URL or "https://elastic.soorgla.com"],
                "timeout": 30,
                "max_retries": 3,
                "retry_on_timeout": True,
                "http_compress": True,
                "verify_certs": True,
                "ssl_show_warn": False
            }
            
            # Add authentication if provided
            if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
                es_config["http_auth"] = (
                    settings.ELASTICSEARCH_USERNAME,
                    settings.ELASTICSEARCH_PASSWORD
                )
            
            client = AsyncElasticsearch(**es_config)
            logger.info("Elasticsearch client created successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create Elasticsearch client: {e}")
            raise
    
    async def connect(self) -> bool:
        """Test Elasticsearch connection"""
        try:
            if not self._client:
                self._client = self._create_client()
            
            # Test connection
            info = await self._client.info()
            self._connected = True
            
            logger.info(
                f"Connected to Elasticsearch cluster: {info['cluster_name']} "
                f"(version: {info['version']['number']})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Close Elasticsearch connection"""
        if self._client:
            await self._client.close()
            self._connected = False
            logger.info("Elasticsearch connection closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get Elasticsearch cluster health"""
        try:
            if not self._connected:
                await self.connect()
            
            health = await self._client.cluster.health()
            return {
                "status": health["status"],
                "cluster_name": health["cluster_name"],
                "number_of_nodes": health["number_of_nodes"],
                "active_primary_shards": health["active_primary_shards"],
                "active_shards": health["active_shards"],
                "relocating_shards": health["relocating_shards"],
                "initializing_shards": health["initializing_shards"],
                "unassigned_shards": health["unassigned_shards"],
                "delayed_unassigned_shards": health["delayed_unassigned_shards"],
                "number_of_pending_tasks": health["number_of_pending_tasks"],
                "task_max_waiting_in_queue_millis": health["task_max_waiting_in_queue_millis"],
                "active_shards_percent_as_number": health["active_shards_percent_as_number"]
            }
            
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return {
                "status": "red",
                "error": str(e),
                "connected": self._connected
            }
    
    async def index(
        self,
        index: str,
        body: Dict[str, Any],
        doc_id: Optional[str] = None,
        pipeline: Optional[str] = None,
        refresh: Optional[str] = None
    ) -> Dict[str, Any]:
        """Index a document"""
        try:
            if not self._connected:
                await self.connect()
            
            params = {}
            if pipeline:
                params["pipeline"] = pipeline
            if refresh:
                params["refresh"] = refresh
            
            if doc_id:
                response = await self._client.index(
                    index=index,
                    id=doc_id,
                    body=body,
                    **params
                )
            else:
                response = await self._client.index(
                    index=index,
                    body=body,
                    **params
                )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to index document to {index}: {e}",
                extra={"index": index, "doc_id": doc_id, "pipeline": pipeline}
            )
            raise
    
    async def search(
        self,
        index: str,
        body: Dict[str, Any],
        size: Optional[int] = None,
        from_: Optional[int] = None,
        timeout: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search documents"""
        try:
            if not self._connected:
                await self.connect()
            
            params = {}
            if size is not None:
                params["size"] = size
            if from_ is not None:
                params["from"] = from_
            if timeout:
                params["timeout"] = timeout
            
            response = await self._client.search(
                index=index,
                body=body,
                **params
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to search index {index}: {e}",
                extra={"index": index, "query": body}
            )
            raise
    
    async def bulk(
        self,
        operations: list,
        index: Optional[str] = None,
        pipeline: Optional[str] = None,
        refresh: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk operations"""
        try:
            if not self._connected:
                await self.connect()
            
            params = {}
            if index:
                params["index"] = index
            if pipeline:
                params["pipeline"] = pipeline
            if refresh:
                params["refresh"] = refresh
            
            response = await self._client.bulk(
                operations=operations,
                **params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Bulk operation failed: {e}")
            raise
    
    async def delete_by_query(
        self,
        index: str,
        body: Dict[str, Any],
        refresh: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete documents by query"""
        try:
            if not self._connected:
                await self.connect()
            
            params = {}
            if refresh:
                params["refresh"] = refresh
            
            response = await self._client.delete_by_query(
                index=index,
                body=body,
                **params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Delete by query failed for index {index}: {e}")
            raise
    
    async def create_index_template(
        self,
        name: str,
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update index template"""
        try:
            if not self._connected:
                await self.connect()
            
            response = await self._client.indices.put_index_template(
                name=name,
                body=body
            )
            
            logger.info(f"Index template '{name}' created/updated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create index template '{name}': {e}")
            raise
    
    async def put_pipeline(
        self,
        id: str,
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update ingest pipeline"""
        try:
            if not self._connected:
                await self.connect()
            
            response = await self._client.ingest.put_pipeline(
                id=id,
                body=body
            )
            
            logger.info(f"Ingest pipeline '{id}' created/updated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create ingest pipeline '{id}': {e}")
            raise
    
    async def put_lifecycle_policy(
        self,
        policy: str,
        body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update ILM policy"""
        try:
            if not self._connected:
                await self.connect()
            
            response = await self._client.ilm.put_lifecycle(
                policy=policy,
                body=body
            )
            
            logger.info(f"ILM policy '{policy}' created/updated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create ILM policy '{policy}': {e}")
            raise


# Global Elasticsearch manager instance

@lru_cache()
def get_elasticsearch_manager() -> ElasticsearchManager:
    """Get cached Elasticsearch manager instance"""
    return ElasticsearchManager()

def get_es_client() -> AsyncElasticsearch:
    """Get Elasticsearch client for direct access"""
    return get_elasticsearch_manager().client


async def check_elasticsearch_connection() -> bool:
    """Check Elasticsearch connection health"""
    try:
        es_manager = get_elasticsearch_manager()
        health = await es_manager.health_check()
        return health.get("status") in ["green", "yellow"]
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        return False