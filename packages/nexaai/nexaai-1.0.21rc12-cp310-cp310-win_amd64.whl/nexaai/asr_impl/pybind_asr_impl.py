from typing import List, Optional, Union

from nexaai.common import PluginID, ModelConfig
from nexaai.asr import ASR, ASRConfig, ASRResult
from nexaai.binds import asr_bind, common_bind
from nexaai.runtime import _ensure_runtime


class PyBindASRImpl(ASR):
    def __init__(self, handle: any, m_cfg: ModelConfig = ModelConfig()):
        """Private constructor, should not be called directly."""
        super().__init__(m_cfg)
        self._handle = handle  # This is a py::capsule
        self._model_config = None

    @classmethod
    def _load_from(cls,
                   model_path: str,
                   model_name: Optional[str] = None,
                   tokenizer_path: Optional[str] = None,
                   language: Optional[str] = None,
                   m_cfg: ModelConfig = ModelConfig(),
                   plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP,
                   device_id: Optional[str] = None
        ) -> 'PyBindASRImpl':
        """Load ASR model from local path using PyBind backend."""
        _ensure_runtime()
        
        # Create model config
        config = common_bind.ModelConfig()
        
        config.n_ctx = m_cfg.n_ctx
        if m_cfg.n_threads is not None:
            config.n_threads = m_cfg.n_threads
        if m_cfg.n_threads_batch is not None:
            config.n_threads_batch = m_cfg.n_threads_batch
        if m_cfg.n_batch is not None:
            config.n_batch = m_cfg.n_batch
        if m_cfg.n_ubatch is not None:
            config.n_ubatch = m_cfg.n_ubatch
        if m_cfg.n_seq_max is not None:
            config.n_seq_max = m_cfg.n_seq_max
        config.n_gpu_layers = m_cfg.n_gpu_layers
        
        # handle chat template strings
        if m_cfg.chat_template_path:
            config.chat_template_path = m_cfg.chat_template_path
        
        if m_cfg.chat_template_content:
            config.chat_template_content = m_cfg.chat_template_content
        
        # Convert plugin_id to string
        plugin_id_str = plugin_id.value if isinstance(plugin_id, PluginID) else str(plugin_id)
        
        # Create ASR handle using the binding
        handle = asr_bind.ml_asr_create(
            model_path=model_path,
            model_name=model_name,
            tokenizer_path=tokenizer_path,
            model_config=config,
            language=language,
            plugin_id=plugin_id_str,
            device_id=device_id,
            license_id=None,  # Optional
            license_key=None  # Optional
        )
        
        return cls(handle, m_cfg)

    def eject(self):
        """Release the model from memory."""
        # py::capsule handles cleanup automatically
        if hasattr(self, '_handle') and self._handle is not None:
            del self._handle
            self._handle = None

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        config: Optional[ASRConfig] = None,
    ) -> ASRResult:
        """Transcribe audio file to text."""
        if self._handle is None:
            raise RuntimeError("ASR model not loaded. Call _load_from first.")
        
        # Convert ASRConfig to binding format if provided
        asr_config = None
        if config:
            asr_config = asr_bind.ASRConfig()
            asr_config.timestamps = config.timestamps
            asr_config.beam_size = config.beam_size
            asr_config.stream = config.stream
        
        # Perform transcription using the binding
        result_dict = asr_bind.ml_asr_transcribe(
            handle=self._handle,
            audio_path=audio_path,
            language=language,
            config=asr_config
        )
        
        # Convert result to ASRResult
        transcript = result_dict.get("transcript", "")
        confidence_scores = result_dict.get("confidence_scores")
        timestamps = result_dict.get("timestamps")
        
        # Convert timestamps to the expected format
        timestamp_pairs = []
        if timestamps:
            for start, end in timestamps:
                timestamp_pairs.append((float(start), float(end)))
        
        return ASRResult(
            transcript=transcript,
            confidence_scores=confidence_scores or [],
            timestamps=timestamp_pairs
        )

    def list_supported_languages(self) -> List[str]:
        """List supported languages."""
        if self._handle is None:
            raise RuntimeError("ASR model not loaded. Call _load_from first.")
        
        # Get supported languages using the binding
        languages = asr_bind.ml_asr_list_supported_languages(handle=self._handle)
        return languages
