import pytest
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / "src"))

from astrogeo.utils.vector_store import VectorStoreManager
from astrogeo.utils.config_loader import ConfigLoader

class TestPipeline:
    """Test data pipeline and vector store integration"""
    
    def test_vector_store_initialization(self):
        """Test that vector store can be initialized"""
        try:
            config_loader = ConfigLoader()
            rag_config = config_loader.load_config('rag')
            
            vector_store = VectorStoreManager(rag_config)
            vector_store.initialize_vector_store()
            
            assert vector_store.client is not None, "Vector store client not initialized"
            
        except Exception as e:
            pytest.fail(f"Vector store initialization failed: {e}")
    
    def test_vector_db_connection(self):
        """Test vector database connection"""
        vector_db_path = Path("data/vector_store/vector_db")
        assert vector_db_path.exists(), "Vector database directory not found"
        
        # Check for ChromaDB files
        files = list(vector_db_path.glob("*"))
        assert len(files) > 0, "Vector database appears to be empty"
    
    def test_data_harvesting_to_vector_store(self):
        """Test that data from harvesting is correctly added to vector store"""
        try:
            config_loader = ConfigLoader()
            rag_config = config_loader.load_config('rag')
            
            vector_store = VectorStoreManager(rag_config)
            vector_store.initialize_vector_store()
            
            # Test adding sample documents
            test_documents = [
                "The International Space Station orbits Earth at approximately 408 kilometers altitude.",
                "NASA's James Webb Space Telescope has revolutionized our understanding of distant galaxies."
            ]
            
            test_metadatas = [
                {"source": "test", "type": "space_fact"},
                {"source": "test", "type": "astronomy"}
            ]
            
            # This should not fail if vector store is properly configured
            vector_store.add_documents(test_documents, test_metadatas)
            
            # Test similarity search
            results = vector_store.similarity_search("space station", k=1)
            assert len(results) > 0, "Vector search returned no results"
            
        except Exception as e:
            pytest.fail(f"Data pipeline test failed: {e}")
    
    def test_config_loading(self):
        """Test that all configuration files can be loaded"""
        config_loader = ConfigLoader()
        
        configs = ['agents', 'tasks', 'rag', 'settings']
        for config_name in configs:
            try:
                config = config_loader.load_config(config_name)
                assert config is not None, f"Config {config_name} is empty"
                assert isinstance(config, dict), f"Config {config_name} is not a dictionary"
            except Exception as e:
                pytest.fail(f"Failed to load {config_name} config: {e}")
