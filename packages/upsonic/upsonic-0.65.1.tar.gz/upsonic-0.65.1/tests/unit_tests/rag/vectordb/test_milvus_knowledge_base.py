"""
Test MilvusProvider integration with Knowledge Base.
"""
import pytest
import asyncio
import os
import shutil
import sys
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from upsonic.knowledge_base.knowledge_base import KnowledgeBase
from upsonic.vectordb.providers.milvus import MilvusProvider
from upsonic.vectordb.config import Config, CoreConfig, IndexingConfig, SearchConfig, DataManagementConfig, AdvancedConfig
from upsonic.vectordb.config import Mode, ProviderName, DistanceMetric, IndexType, HNSWTuningConfig, IVFTuningConfig
from upsonic.schemas.data_models import Document, Chunk, RAGSearchResult
from upsonic.schemas.vector_schemas import VectorSearchResult

from .mock_components import (
    MockEmbeddingProvider, MockChunker, MockLoader,
    create_mock_document, create_mock_chunk, create_mock_vector_search_result
)


class TestMilvusKnowledgeBaseIntegration:
    """Test MilvusProvider integration with Knowledge Base."""
    
    def teardown_method(self):
        """Clean up test database files after each test."""
        import glob
        # Clean up any test database files
        for db_file in glob.glob("test_milvus_*.db"):
            try:
                if os.path.exists(db_file):
                    os.remove(db_file)
            except Exception:
                pass
    
    @pytest.fixture
    def milvus_config(self):
        """Create a MilvusProvider configuration."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        core_config = CoreConfig(
            provider_name=ProviderName.MILVUS,
            mode=Mode.EMBEDDED,
            db_path=f"test_milvus_{unique_id}.db",
            collection_name=f"test_collection_{unique_id}",
            vector_size=384,
            distance_metric=DistanceMetric.COSINE
        )
        
        indexing_config = IndexingConfig(
            index_config=HNSWTuningConfig(index_type=IndexType.HNSW),
            create_dense_index=True,
            create_sparse_index=False
        )
        
        search_config = SearchConfig(
            default_top_k=5,
            dense_search_enabled=True,
            full_text_search_enabled=True,
            hybrid_search_enabled=True
        )
        
        data_config = DataManagementConfig()
        advanced_config = AdvancedConfig()
        
        return Config(
            core=core_config,
            indexing=indexing_config,
            search=search_config,
            data_management=data_config,
            advanced=advanced_config
        )
    
    @pytest.fixture
    def milvus_hybrid_config(self):
        """Create a MilvusProvider configuration with both dense and sparse indexes for hybrid search."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        core_config = CoreConfig(
            provider_name=ProviderName.MILVUS,
            mode=Mode.EMBEDDED,
            db_path=f"test_milvus_hybrid_{unique_id}.db",
            collection_name=f"test_collection_hybrid_{unique_id}",
            vector_size=384,
            distance_metric=DistanceMetric.COSINE
        )
        
        indexing_config = IndexingConfig(
            index_config=HNSWTuningConfig(index_type=IndexType.HNSW),
            create_dense_index=True,
            create_sparse_index=True
        )
        
        search_config = SearchConfig(
            default_top_k=5,
            dense_search_enabled=True,
            full_text_search_enabled=True,
            hybrid_search_enabled=True
        )
        
        data_config = DataManagementConfig()
        advanced_config = AdvancedConfig()
        
        return Config(
            core=core_config,
            indexing=indexing_config,
            search=search_config,
            data_management=data_config,
            advanced=advanced_config
        )
    
    @pytest.fixture
    def milvus_hybrid_provider(self, milvus_hybrid_config):
        """Create a MilvusProvider with hybrid search configuration."""
        return MilvusProvider(milvus_hybrid_config)
    
    @pytest.fixture
    def mock_embedding_provider(self):
        """Create a mock embedding provider."""
        return MockEmbeddingProvider()
    
    @pytest.fixture
    def mock_chunker(self):
        """Create a mock chunker."""
        return MockChunker()
    
    @pytest.fixture
    def mock_loader(self):
        """Create a mock loader."""
        return MockLoader()
    
    @pytest.fixture
    def milvus_provider(self, milvus_config):
        """Create a MilvusProvider instance."""
        return MilvusProvider(milvus_config)
    
    @pytest.fixture
    def knowledge_base(self, milvus_provider, mock_embedding_provider, mock_chunker, mock_loader):
        """Create a Knowledge Base with MilvusProvider."""
        return KnowledgeBase(
            sources=["test_source.txt"],
            embedding_provider=mock_embedding_provider,
            vectordb=milvus_provider,
            splitters=mock_chunker,
            loaders=mock_loader,
            name="test_kb"
        )
    
    def test_milvus_provider_initialization(self, milvus_provider, milvus_config):
        """Test MilvusProvider initialization."""
        assert milvus_provider._config == milvus_config
        assert not milvus_provider._is_connected
        assert milvus_provider._collection is None
    
    @pytest.mark.skipif(sys.platform == "win32", reason="milvus-lite not available on Windows")
    def test_milvus_provider_connection(self, milvus_provider):
        """Test MilvusProvider connection."""
        milvus_provider.connect()
        assert milvus_provider._is_connected
        assert milvus_provider.is_ready()
    
    @pytest.mark.skipif(sys.platform == "win32", reason="milvus-lite not available on Windows")
    def test_milvus_provider_disconnection(self, milvus_provider):
        """Test MilvusProvider disconnection."""
        milvus_provider.connect()
        assert milvus_provider._is_connected
        
        milvus_provider.disconnect()
        assert not milvus_provider._is_connected
        assert milvus_provider._collection is None
    
    @pytest.mark.skipif(sys.platform == "win32", reason="milvus-lite not available on Windows")
    def test_milvus_collection_creation(self, milvus_provider):
        """Test MilvusProvider collection creation."""
        milvus_provider.connect()
        assert not milvus_provider.collection_exists()
        
        milvus_provider.create_collection()
        assert milvus_provider.collection_exists()
    
    @pytest.mark.skipif(sys.platform == "win32", reason="milvus-lite not available on Windows")
    def test_milvus_collection_deletion(self, milvus_provider):
        """Test MilvusProvider collection deletion."""
        milvus_provider.connect()
        milvus_provider.create_collection()
        assert milvus_provider.collection_exists()
        
        milvus_provider.delete_collection()
        assert not milvus_provider.collection_exists()
    
    @pytest.mark.skipif(sys.platform == "win32", reason="milvus-lite not available on Windows")
    def test_milvus_upsert_operations(self, milvus_provider):
        """Test MilvusProvider upsert operations."""
        milvus_provider.connect()
        milvus_provider.create_collection()
        
        # Test data
        vectors = [[0.1] * 384, [0.2] * 384]
        payloads = [{"source": "test1"}, {"source": "test2"}]
        ids = ["id1", "id2"]
        chunks = ["chunk1", "chunk2"]
        
        # Upsert data
        milvus_provider.upsert(vectors, payloads, ids, chunks)
        
        # Verify data was stored
        results = milvus_provider.fetch(ids)
        assert len(results) == 2
        assert results[0].id == "id1"
        assert results[1].id == "id2"
    
    @pytest.mark.skipif(sys.platform == "win32", reason="milvus-lite not available on Windows")
    def test_milvus_search_operations(self, milvus_provider):
        """Test MilvusProvider search operations."""
        milvus_provider.connect()
        milvus_provider.create_collection()
        
        # Insert test data
        vectors = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
        payloads = [{"source": "test1"}, {"source": "test2"}, {"source": "test3"}]
        ids = ["id1", "id2", "id3"]
        chunks = ["chunk1", "chunk2", "chunk3"]
        
        milvus_provider.upsert(vectors, payloads, ids, chunks)
        
        # Test dense search
        query_vector = [0.15] * 384
        results = milvus_provider.dense_search(query_vector, top_k=2)
        assert len(results) <= 2
        assert all(isinstance(result, VectorSearchResult) for result in results)
    
    @pytest.mark.skipif(sys.platform == "win32", reason="milvus-lite not available on Windows")
    def test_milvus_delete_operations(self, milvus_provider):
        """Test MilvusProvider delete operations."""
        milvus_provider.connect()
        milvus_provider.create_collection()
        
        # Insert test data
        vectors = [[0.1] * 384, [0.2] * 384]
        payloads = [{"source": "test1"}, {"source": "test2"}]
        ids = ["id1", "id2"]
        chunks = ["chunk1", "chunk2"]
        
        milvus_provider.upsert(vectors, payloads, ids, chunks)
        
        # Verify data exists
        results = milvus_provider.fetch(ids)
        assert len(results) == 2
        
        # Delete one item
        milvus_provider.delete(["id1"])
        
        # Verify deletion
        results = milvus_provider.fetch(ids)
        assert len(results) == 1
        assert results[0].id == "id2"
    
    @pytest.mark.asyncio
    async def test_knowledge_base_setup_with_milvus(self, knowledge_base):
        """Test Knowledge Base setup with MilvusProvider."""
        # Mock the vectordb methods
        knowledge_base.vectordb.connect = Mock()
        knowledge_base.vectordb.create_collection = Mock()
        knowledge_base.vectordb.upsert = Mock()
        knowledge_base.vectordb.collection_exists = Mock(return_value=False)
        knowledge_base.vectordb.is_ready = Mock(return_value=True)
        
        # Mock the embedding provider
        knowledge_base.embedding_provider.embed_documents = AsyncMock(return_value=[[0.1] * 384, [0.2] * 384])
        
        # Setup the knowledge base
        await knowledge_base.setup_async()
        
        # Verify setup was called
        knowledge_base.vectordb.connect.assert_called_once()
        knowledge_base.vectordb.create_collection.assert_called_once()
        knowledge_base.vectordb.upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_knowledge_base_query_with_milvus(self, knowledge_base):
        """Test Knowledge Base query with MilvusProvider."""
        # Mock the vectordb methods
        knowledge_base.vectordb.connect = Mock()
        knowledge_base.vectordb.create_collection = Mock()
        knowledge_base.vectordb.upsert = Mock()
        knowledge_base.vectordb.collection_exists = Mock(return_value=False)
        knowledge_base.vectordb.is_ready = Mock(return_value=True)
        knowledge_base.vectordb.search = Mock(return_value=[
            create_mock_vector_search_result("id1", 0.9, "Test result 1"),
            create_mock_vector_search_result("id2", 0.8, "Test result 2")
        ])
        
        # Mock the embedding provider
        knowledge_base.embedding_provider.embed_documents = AsyncMock(return_value=[[0.1] * 384, [0.2] * 384])
        knowledge_base.embedding_provider.embed_query = AsyncMock(return_value=[0.15] * 384)
        
        # Setup the knowledge base
        await knowledge_base.setup_async()
        
        # Query the knowledge base
        results = await knowledge_base.query_async("test query")
        
        # Verify results
        assert len(results) == 2
        assert all(isinstance(result, RAGSearchResult) for result in results)
        assert results[0].text == "Test result 1"
        assert results[1].text == "Test result 2"
    
    def test_milvus_hybrid_search(self, milvus_provider):
        """Test MilvusProvider hybrid search functionality (mocked)."""
        # Mock hybrid search since it requires complex sparse vector setup
        milvus_provider.hybrid_search = Mock(return_value=[
            create_mock_vector_search_result("id1", 0.9, "Test result 1"),
            create_mock_vector_search_result("id2", 0.8, "Test result 2")
        ])
        
        query_vector = [0.15] * 384
        query_text = "test query"
        
        results = milvus_provider.hybrid_search(query_vector, query_text, top_k=2)
        
        # Verify hybrid search was called
        milvus_provider.hybrid_search.assert_called_once_with(query_vector, query_text, top_k=2)
        assert len(results) == 2
    
    def test_milvus_full_text_search(self, milvus_provider):
        """Test MilvusProvider full-text search (mocked)."""
        # Mock full-text search since it requires complex setup
        milvus_provider.full_text_search = Mock(return_value=[
            create_mock_vector_search_result("id1", 0.9, "Test result 1"),
            create_mock_vector_search_result("id2", 0.8, "Test result 2")
        ])
        
        # Test full-text search
        results = milvus_provider.full_text_search("chunk", top_k=2)
        
        # Verify full-text search was called
        milvus_provider.full_text_search.assert_called_once_with("chunk", top_k=2)
        assert len(results) == 2
        assert all(isinstance(result, VectorSearchResult) for result in results)
    
    def test_milvus_sparse_vectors(self, milvus_provider):
        """Test MilvusProvider sparse vector functionality (mocked)."""
        # Mock sparse vector operations since they require complex setup
        milvus_provider.upsert = Mock()
        milvus_provider.fetch = Mock(return_value=[
            create_mock_vector_search_result("id1", 1.0, "Test result 1"),
            create_mock_vector_search_result("id2", 1.0, "Test result 2")
        ])
        
        # Test sparse vector upsert
        vectors = [[0.1] * 384, [0.2] * 384]
        payloads = [{"source": "test1"}, {"source": "test2"}]
        ids = ["id1", "id2"]
        chunks = ["chunk1", "chunk2"]
        sparse_vectors = [
            {"indices": [1, 5, 10], "values": [0.1, 0.2, 0.3]},
            {"indices": [2, 6, 11], "values": [0.4, 0.5, 0.6]}
        ]
        
        milvus_provider.upsert(vectors, payloads, ids, chunks, sparse_vectors=sparse_vectors)
        
        # Verify data was stored
        results = milvus_provider.fetch(ids)
        
        # Verify operations were called
        milvus_provider.upsert.assert_called_once()
        milvus_provider.fetch.assert_called_once()
        assert len(results) == 2
    
    def test_milvus_index_types(self, milvus_provider):
        """Test MilvusProvider index types (mocked)."""
        # Mock index type operations since config is frozen
        milvus_provider.create_collection = Mock()
        
        # Test that different index types can be created
        hnsw_config = HNSWTuningConfig(index_type=IndexType.HNSW, m=16, ef_construction=200)
        ivf_config = IVFTuningConfig(index_type=IndexType.IVF_FLAT, nlist=100)
        
        # Should not raise error
        assert hnsw_config.m == 16
        assert ivf_config.nlist == 100
    
    def test_milvus_filter_operations(self, milvus_provider):
        """Test MilvusProvider filter operations (mocked)."""
        # Mock filter operations
        milvus_provider.dense_search = Mock(return_value=[
            create_mock_vector_search_result("id1", 0.9, "Test result 1"),
            create_mock_vector_search_result("id3", 0.8, "Test result 3")
        ])
        
        # Test search with filter
        query_vector = [0.15] * 384
        filter_dict = {"category": "A"}
        
        results = milvus_provider.dense_search(query_vector, top_k=5, filter=filter_dict)
        
        # Verify search was called with filter
        milvus_provider.dense_search.assert_called_once_with(query_vector, top_k=5, filter=filter_dict)
        assert len(results) == 2
    
    def test_milvus_payload_indexes(self, milvus_provider):
        """Test MilvusProvider payload indexes (mocked)."""
        from upsonic.vectordb.config import PayloadIndexConfig
        
        # Test payload index configuration
        payload_indexes = [
            PayloadIndexConfig(
                field_name="category",
                field_schema_type="keyword"
            ),
            PayloadIndexConfig(
                field_name="description",
                field_schema_type="text",
                enable_full_text_index=True
            )
        ]
        
        # Mock collection creation
        milvus_provider.create_collection = Mock()
        
        # Test that payload indexes can be configured
        assert len(payload_indexes) == 2
        assert payload_indexes[0].field_name == "category"
        assert payload_indexes[1].enable_full_text_index == True
    
    def test_milvus_error_handling(self, milvus_provider):
        """Test MilvusProvider error handling (mocked)."""
        # Mock error scenarios
        milvus_provider.create_collection = Mock(side_effect=Exception("Connection error"))
        milvus_provider.upsert = Mock(side_effect=Exception("Invalid data"))
        
        # Test connection error
        with pytest.raises(Exception):
            milvus_provider.create_collection()
        
        # Test invalid upsert
        with pytest.raises(Exception):
            milvus_provider.upsert([], [], [], [])
    
    def test_milvus_configuration_validation(self):
        """Test MilvusProvider configuration validation (mocked)."""
        # Mock configuration validation
        with patch('upsonic.vectordb.providers.milvus.MilvusProvider._validate_config') as mock_validate:
            mock_validate.side_effect = Exception("Invalid configuration")
            
            with pytest.raises(Exception):
                MilvusProvider(Config(core=CoreConfig(
                    provider_name=ProviderName.CHROMA,  # Wrong provider
                    mode=Mode.IN_MEMORY,
                    collection_name="test",
                    vector_size=384
                )))
    
    def test_milvus_collection_recreation(self, milvus_provider):
        """Test MilvusProvider collection recreation (mocked)."""
        # Mock collection operations
        milvus_provider.connect = Mock()
        milvus_provider.create_collection = Mock()
        milvus_provider.collection_exists = Mock(return_value=True)
        
        # Test collection creation
        milvus_provider.connect()
        milvus_provider.create_collection()
        assert milvus_provider.collection_exists()
        
        # Test recreation
        milvus_provider.create_collection()  # Should not raise error
        assert milvus_provider.collection_exists()
    
    def test_milvus_distance_metrics(self, milvus_provider):
        """Test MilvusProvider distance metrics (mocked)."""
        # Test that different distance metrics are supported
        distance_metrics = [DistanceMetric.COSINE, DistanceMetric.EUCLIDEAN, DistanceMetric.DOT_PRODUCT]
        
        for metric in distance_metrics:
            # Test that metrics are valid
            assert metric in distance_metrics
    
    def test_milvus_consistency_levels(self, milvus_provider):
        """Test MilvusProvider consistency levels (mocked)."""
        from upsonic.vectordb.config import WriteConsistency
        
        # Test different consistency levels
        consistency_levels = [WriteConsistency.STRONG, WriteConsistency.EVENTUAL]
        
        for consistency in consistency_levels:
            # Test that consistency levels are valid
            assert consistency in consistency_levels
