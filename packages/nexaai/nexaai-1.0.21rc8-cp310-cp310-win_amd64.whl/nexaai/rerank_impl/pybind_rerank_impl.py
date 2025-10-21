from typing import List, Optional, Sequence, Union
import numpy as np

from nexaai.common import PluginID
from nexaai.rerank import Reranker, RerankConfig
from nexaai.binds import rerank_bind, common_bind
from nexaai.runtime import _ensure_runtime


class PyBindRerankImpl(Reranker):
    def __init__(self, _handle_ptr):
        """
        Internal initializer
        
        Args:
            _handle_ptr: Capsule handle to the C++ reranker object
        """
        super().__init__()
        self._handle = _handle_ptr

    @classmethod
    def _load_from(cls,
                   model_path: str,
                   model_name: str = None,
                   tokenizer_file: str = "tokenizer.json",
                   plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP,
                   device_id: Optional[str] = None
        ) -> 'PyBindRerankImpl':
        """
        Load reranker model from local path using PyBind backend.
        
        Args:
            model_path: Path to the model file
            model_name: Name of the model (optional)
            tokenizer_file: Path to the tokenizer file (default: "tokenizer.json")
            plugin_id: Plugin ID to use for the model (default: PluginID.LLAMA_CPP)
            device_id: Device ID to use for the model (optional)
            
        Returns:
            PyBindRerankImpl instance
        """
        _ensure_runtime()
        
        # Convert enum to string for C++ binding
        plugin_id_str = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        
        # Create model config
        model_config = common_bind.ModelConfig()
        
        # Create reranker handle with new API signature
        handle = rerank_bind.ml_reranker_create(
            model_path,
            model_name,
            tokenizer_file,
            model_config,
            plugin_id_str,
            device_id
        )
        
        return cls(handle)

    def eject(self):
        """
        Clean up resources and destroy the reranker
        """
        # Destructor of the handle will unload the model correctly
        if hasattr(self, '_handle') and self._handle is not None:
            del self._handle
            self._handle = None

    def load_model(self, model_path: str, extra_data: Optional[str] = None) -> bool:
        """
        Load model from path.
        
        Note: This method is not typically used directly. Use _load_from instead.
        
        Args:
            model_path: Path to the model file
            extra_data: Additional data (unused)
            
        Returns:
            True if successful
        """
        # This method is part of the BaseModel interface but typically not used
        # directly for PyBind implementations since _load_from handles creation
        raise NotImplementedError("Use _load_from class method to load models")

    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        config: Optional[RerankConfig] = None,
    ) -> List[float]:
        """
        Rerank documents given a query.
        
        Args:
            query: Query text as UTF-8 string
            documents: List of document texts to rerank
            config: Optional reranking configuration
            
        Returns:
            List of ranking scores (one per document)
        """
        if self._handle is None:
            raise RuntimeError("Reranker handle is None. Model may have been ejected.")
        
        # Use default config if not provided
        if config is None:
            config = RerankConfig()
        
        # Create bind config
        bind_config = rerank_bind.RerankConfig()
        bind_config.batch_size = config.batch_size
        bind_config.normalize = config.normalize
        bind_config.normalize_method = config.normalize_method
        
        # Convert documents to list if needed
        documents_list = list(documents)
        
        # Call the binding which returns a dict with scores and profile_data
        result = rerank_bind.ml_reranker_rerank(
            self._handle,
            query,
            documents_list,
            bind_config
        )
        
        # Extract scores from result dict
        scores_array = result.get("scores", np.array([]))
        
        # Convert numpy array to list of floats
        if isinstance(scores_array, np.ndarray):
            return scores_array.tolist()
        else:
            return []
