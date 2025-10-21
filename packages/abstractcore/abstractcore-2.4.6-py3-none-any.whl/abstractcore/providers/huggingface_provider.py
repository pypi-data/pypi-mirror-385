"""
HuggingFace provider implementation with GGUF support.
Supports both transformers models and GGUF models via llama-cpp-python.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Iterator, Type

try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None
from .base import BaseProvider
from ..core.types import GenerateResponse
from ..exceptions import ModelNotFoundError, format_model_error
from ..tools import UniversalToolHandler, execute_tools
from ..events import EventType

# Try to import transformers (standard HuggingFace support)
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Try to import llama-cpp-python (GGUF support)
try:
    from llama_cpp import Llama
    LLAMACPP_AVAILABLE = True
except ImportError:
    LLAMACPP_AVAILABLE = False

# We no longer download models - cache-only approach
# huggingface_hub not required for basic operation


class HuggingFaceProvider(BaseProvider):
    """HuggingFace provider with dual support for transformers and GGUF models"""

    def __init__(self, model: str = "Qwen/Qwen3-4B",
                 device: Optional[str] = None,
                 n_gpu_layers: Optional[int] = None,
                 **kwargs):

        # Handle legacy context_size parameter with deprecation warning
        context_size = kwargs.pop("context_size", None)
        if context_size is not None:
            import warnings
            warnings.warn(
                "The 'context_size' parameter is deprecated. Use 'max_tokens' instead. "
                "context_size will be removed in a future version.",
                DeprecationWarning,
                stacklevel=2
            )
            if "max_tokens" not in kwargs:
                kwargs["max_tokens"] = context_size

        super().__init__(model, **kwargs)

        # Handle timeout parameter for local models
        self._handle_timeout_parameter(kwargs)

        # Initialize tool handler
        self.tool_handler = UniversalToolHandler(model)

        # Store provider-specific configuration
        self.n_gpu_layers = n_gpu_layers
        self.model_type = None  # Will be "transformers" or "gguf"
        self.device = device

        # Model instances
        self.tokenizer = None
        self.model_instance = None
        self.pipeline = None
        self.llm = None  # For GGUF models

        # Detect model type and load accordingly
        if self._is_gguf_model(model):
            if not LLAMACPP_AVAILABLE:
                raise ImportError("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            self.model_type = "gguf"
            self._setup_device_gguf()
            self._load_gguf_model()
        else:
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Transformers not installed. Install with: pip install transformers torch")
            self.model_type = "transformers"
            self._setup_device_transformers()
            self._load_transformers_model()

    def unload(self) -> None:
        """
        Unload the model from memory.

        For GGUF models, calls llm.close() to free llama.cpp resources.
        For transformers models, clears model and tokenizer references.
        """
        import gc
        try:
            if hasattr(self, 'llm') and self.llm is not None:
                # Try to properly close the Llama object (GGUF models)
                if hasattr(self.llm, 'close'):
                    self.llm.close()
                # Clear the reference
                self.llm = None

            if hasattr(self, 'tokenizer') and self.tokenizer is not None:
                self.tokenizer = None

            if hasattr(self, 'model') and hasattr(self, 'model') and self.model is not None:
                # For transformers models, clear the model
                self.model = None

            # Force garbage collection to free memory immediately
            gc.collect()
        except Exception as e:
            # Log but don't raise - unload should be best-effort
            if hasattr(self, 'logger'):
                self.logger.warning(f"Error during unload: {e}")

    def __del__(self):
        """Properly clean up resources to minimize garbage collection issues"""
        try:
            self.unload()
        except Exception:
            # Silently handle any cleanup errors - this is expected during shutdown
            pass

    def _is_gguf_model(self, model: str) -> bool:
        """Detect if the model is a GGUF model"""
        # Check if it's a .gguf file path
        if model.endswith('.gguf'):
            return True

        # Check if local file exists with .gguf extension
        model_path = Path(model)
        if model_path.exists() and model_path.suffix == '.gguf':
            return True

        # Check if it's a HF repo with GGUF in the name (various formats)
        model_lower = model.lower()
        if 'gguf' in model_lower:
            # Handle formats like:
            # - "unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF"
            # - "unsloth--Qwen3-Coder-30B-A3B-Instruct-GGUF" (cache format)
            # - "repo/model-GGUF"
            return True

        return False

    def _setup_device_transformers(self):
        """Setup device for transformers models"""
        if not TRANSFORMERS_AVAILABLE:
            return

        if self.device:
            self.device = self.device
        elif torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

    def _setup_device_gguf(self):
        """Setup device for GGUF models"""
        # Auto-detect GPU layers if not specified
        if self.n_gpu_layers is None:
            if self.device == "cuda" or (self.device is None and self._has_cuda()):
                # Use all layers on GPU for CUDA
                self.n_gpu_layers = -1
            elif self.device == "mps" or (self.device is None and self._has_metal()):
                # Use GPU layers for Metal
                self.n_gpu_layers = 1  # Metal works differently
            else:
                # CPU only
                self.n_gpu_layers = 0

    def _has_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False

    def _has_metal(self) -> bool:
        """Check if Metal (Apple Silicon) is available"""
        try:
            import platform
            return platform.system() == "Darwin" and platform.processor() == "arm"
        except:
            return False

    def _load_transformers_model(self):
        """Load standard HuggingFace transformers model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model)
            self.model_instance = AutoModelForCausalLM.from_pretrained(self.model)

            # Move to device
            if self.device in ["cuda", "mps"]:
                self.model_instance = self.model_instance.to(self.device)

            # Create pipeline
            device_arg = 0 if self.device == "cuda" else -1
            if self.device == "mps":
                device_arg = -1

            self.pipeline = pipeline(
                "text-generation",
                model=self.model_instance,
                tokenizer=self.tokenizer,
                device=device_arg
            )

        except Exception as e:
            error_str = str(e).lower()
            if ('not found' in error_str or 'does not exist' in error_str or
                'not a valid model identifier' in error_str):
                available_models = self.list_available_models()
                error_message = format_model_error("HuggingFace", self.model, available_models)
                raise ModelNotFoundError(error_message)
            else:
                raise RuntimeError(f"Failed to load HuggingFace model {self.model}: {str(e)}")

    def _find_gguf_in_cache(self, model_name: str) -> Optional[str]:
        """Find GGUF model in HuggingFace cache (cache-only, no downloading)"""

        # Normalize model name to cache format
        # Convert "unsloth/model" or "unsloth--model" to "models--unsloth--model"
        cache_name = self._normalize_to_cache_format(model_name)

        cache_base = Path.home() / ".cache" / "huggingface" / "hub"
        model_cache_dir = cache_base / cache_name

        if not model_cache_dir.exists():
            return None

        # Look for GGUF files in snapshots
        snapshots_dir = model_cache_dir / "snapshots"
        if not snapshots_dir.exists():
            return None

        # Find the latest snapshot (most recent directory)
        try:
            snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
            if not snapshot_dirs:
                return None

            # Use the most recent snapshot
            latest_snapshot = max(snapshot_dirs, key=lambda x: x.stat().st_mtime)

            # Look for GGUF files in the snapshot
            gguf_files = list(latest_snapshot.glob("*.gguf"))

            if gguf_files:
                # Prefer certain quantizations
                preferred_quants = ['Q4_K_M', 'Q5_K_M', 'Q4_0', 'Q4_1', 'Q5_0', 'Q8_0']

                for quant in preferred_quants:
                    for gguf_file in gguf_files:
                        if quant in gguf_file.name:
                            return str(gguf_file)

                # Return first available GGUF file
                return str(gguf_files[0])

        except Exception:
            pass

        return None

    def _normalize_to_cache_format(self, model_name: str) -> str:
        """Convert model name to HuggingFace cache directory format"""
        # Remove any ":filename" suffix
        if ':' in model_name:
            model_name = model_name.split(':', 1)[0]

        # Handle different input formats:
        if model_name.startswith('models--'):
            # Already in cache format
            return model_name
        elif '/' in model_name:
            # Standard format: "unsloth/model" -> "models--unsloth--model"
            return f"models--{model_name.replace('/', '--')}"
        elif '--' in model_name and not model_name.startswith('models--'):
            # Cache format without prefix: "unsloth--model" -> "models--unsloth--model"
            return f"models--{model_name}"
        else:
            # Single name, assume it's just the model part
            return f"models--{model_name}"

    def _load_gguf_model(self):
        """Load GGUF model using llama-cpp-python (cache-only, no downloading)"""
        import os
        try:
            model_path = None

            # First, try as a direct file path
            if Path(self.model).exists() and self.model.endswith('.gguf'):
                model_path = self.model
            else:
                # Try to find in HuggingFace cache
                model_path = self._find_gguf_in_cache(self.model)

            if not model_path:
                # Model not found in cache - provide graceful fallback
                self._handle_gguf_not_found()
                return

            # Verify file exists and is accessible
            if not Path(model_path).exists():
                raise FileNotFoundError(f"GGUF model file not found: {model_path}")

            # Determine chat format for function calling
            chat_format = None
            model_lower = self.model.lower()
            if 'qwen' in model_lower or 'coder' in model_lower:
                # Qwen models often support function calling
                chat_format = "chatml-function-calling"
            elif 'functionary' in model_lower:
                chat_format = "functionary-v2"

            # Initialize llama-cpp-python with stderr redirected to our logger
            llama_kwargs = {
                "model_path": model_path,
                "n_ctx": self.max_tokens,  # Use unified max_tokens for context window
                "n_gpu_layers": self.n_gpu_layers,
                "chat_format": chat_format,
                "verbose": self.debug,  # Use debug flag for verbose output
                "n_threads": os.cpu_count() // 2 if os.cpu_count() else 4,
                # Additional performance settings
                "n_batch": 512,
                "use_mmap": True,
                "use_mlock": False
            }

            # Redirect stderr during initialization to avoid GGUF loading noise
            from contextlib import redirect_stderr

            if self.debug:
                # In debug mode, keep stderr visible
                self.llm = Llama(**llama_kwargs)
            else:
                # In non-debug mode, silence stderr during model loading
                with open(os.devnull, 'w') as devnull:
                    with redirect_stderr(devnull):
                        self.llm = Llama(**llama_kwargs)

        except Exception as e:
            raise RuntimeError(f"Failed to load GGUF model {self.model}: {str(e)}")

    def _handle_gguf_not_found(self):
        """Handle GGUF model not found with graceful fallback like other providers"""
        # Suggest the correct repo format
        suggested_repo = self._suggest_correct_repo_format(self.model)

        # List any similar models in cache
        similar_models = self._find_similar_gguf_models()

        error_parts = [
            f"❌ GGUF model '{self.model}' not found in HuggingFace cache.",
            "",
            "💡 To download this model, run:",
            f"   huggingface-cli download {suggested_repo}",
            "",
            "🔍 Suggested formats:",
            f"   • Correct: '{suggested_repo}'",
            f"   • Your input: '{self.model}'",
        ]

        if similar_models:
            error_parts.extend([
                "",
                "📂 Similar GGUF models found in cache:",
            ])
            for model in similar_models[:5]:  # Show max 5
                error_parts.append(f"   • {model}")

        error_parts.extend([
            "",
            "📖 For more info: https://huggingface.co/docs/hub/en/gguf",
            "🔧 AbstractCore only uses cached models - we never download automatically."
        ])

        error_message = "\n".join(error_parts)
        raise ModelNotFoundError(error_message)

    def _suggest_correct_repo_format(self, model_name: str) -> str:
        """Suggest the correct repository format"""
        # Handle various input formats and suggest the standard format
        if model_name.startswith('models--'):
            # "models--unsloth--model" -> "unsloth/model"
            parts = model_name.replace('models--', '').split('--', 1)
            if len(parts) == 2:
                return f"{parts[0]}/{parts[1]}"

        elif '--' in model_name and not '/' in model_name:
            # "unsloth--model" -> "unsloth/model"
            parts = model_name.split('--', 1)
            if len(parts) == 2:
                return f"{parts[0]}/{parts[1]}"

        # Return as-is if already in correct format or unknown format
        return model_name

    def _find_similar_gguf_models(self) -> List[str]:
        """Find similar GGUF models in cache"""
        cache_base = Path.home() / ".cache" / "huggingface" / "hub"

        if not cache_base.exists():
            return []

        similar_models = []
        try:
            for cache_dir in cache_base.iterdir():
                if cache_dir.is_dir() and 'gguf' in cache_dir.name.lower():
                    # Convert cache format back to standard format
                    if cache_dir.name.startswith('models--'):
                        repo_name = cache_dir.name.replace('models--', '').replace('--', '/', 1)
                        similar_models.append(repo_name)

        except Exception:
            pass

        return sorted(similar_models)

    def _handle_timeout_parameter(self, kwargs: Dict[str, Any]) -> None:
        """
        Handle timeout parameter for HuggingFace provider.
        
        Since HuggingFace models run locally (both transformers and GGUF),
        timeout parameters don't apply. If a non-None timeout is provided,
        issue a warning and treat it as None (infinity).
        
        Args:
            kwargs: Initialization kwargs that may contain timeout
        """
        timeout_value = kwargs.get('timeout')
        if timeout_value is not None:
            import warnings
            warnings.warn(
                f"HuggingFace provider runs models locally and does not support timeout parameters. "
                f"Provided timeout={timeout_value} will be ignored and treated as None (unlimited).",
                UserWarning,
                stacklevel=3
            )
            # Force timeout to None for local models
            self._timeout = None
        else:
            # Keep None value (unlimited timeout is appropriate for local models)
            self._timeout = None

    def _update_http_client_timeout(self) -> None:
        """
        HuggingFace provider doesn't use HTTP clients for model inference.
        Local models (transformers and GGUF) don't have timeout constraints.
        """
        # No-op for local models - they don't use HTTP clients
        pass

    def generate(self, *args, **kwargs):
        """Public generate method that includes telemetry"""
        return self.generate_with_telemetry(*args, **kwargs)

    def _generate_internal(self,
                          prompt: str,
                          messages: Optional[List[Dict[str, str]]] = None,
                          system_prompt: Optional[str] = None,
                          tools: Optional[List[Dict[str, Any]]] = None,
                          media: Optional[List['MediaContent']] = None,
                          stream: bool = False,
                          response_model: Optional[Type[BaseModel]] = None,
                          **kwargs) -> Union[GenerateResponse, Iterator[GenerateResponse]]:
        """Generate response using appropriate backend"""

        if self.model_type == "gguf":
            return self._generate_gguf(prompt, messages, system_prompt, tools, media, stream, **kwargs)
        else:
            return self._generate_transformers(prompt, messages, system_prompt, tools, media, stream, **kwargs)

    def _generate_transformers(self,
                               prompt: str,
                               messages: Optional[List[Dict[str, str]]] = None,
                               system_prompt: Optional[str] = None,
                               tools: Optional[List[Dict[str, Any]]] = None,
                               media: Optional[List['MediaContent']] = None,
                               stream: bool = False,
                               **kwargs) -> Union[GenerateResponse, Iterator[GenerateResponse]]:
        """Generate using transformers backend (original implementation)"""

        if not self.pipeline:
            return GenerateResponse(
                content="Error: Transformers model not loaded",
                model=self.model,
                finish_reason="error"
            )

        # Build input text with tool and media support
        # Handle media content first if present
        if media:
            try:
                from ..media.handlers import LocalMediaHandler
                media_handler = LocalMediaHandler("huggingface", self.model_capabilities, model_name=self.model)

                # Create multimodal message combining text and media
                multimodal_message = media_handler.create_multimodal_message(prompt, media)

                # For local providers, we get text-embedded content
                if isinstance(multimodal_message, str):
                    prompt = multimodal_message
                else:
                    # If we get a structured message, extract the content
                    if isinstance(multimodal_message, dict) and "content" in multimodal_message:
                        if isinstance(multimodal_message["content"], list):
                            # Find text content in the structured message
                            text_content = ""
                            for item in multimodal_message["content"]:
                                if item.get("type") == "text":
                                    text_content = item.get("text", "")
                                    break
                            prompt = text_content or prompt
                        else:
                            prompt = str(multimodal_message["content"])
            except ImportError:
                self.logger.warning("Media processing not available. Install with: pip install abstractcore[media]")
            except Exception as e:
                self.logger.warning(f"Failed to process media content: {e}")

        input_text = self._build_input_text_transformers(prompt, messages, system_prompt, tools)

        # Generation parameters using unified system
        generation_kwargs = self._prepare_generation_kwargs(**kwargs)
        max_new_tokens = self._get_provider_max_tokens_param(generation_kwargs)
        temperature = kwargs.get("temperature", self.temperature)
        top_p = kwargs.get("top_p", 0.9)
        seed_value = kwargs.get("seed", self.seed)

        try:
            if stream:
                return self._stream_generate_transformers_with_tools(input_text, max_new_tokens, temperature, top_p, tools, kwargs.get('tool_call_tags'), seed_value)
            else:
                response = self._single_generate_transformers(input_text, max_new_tokens, temperature, top_p, seed_value)

                # Handle tool execution for prompted models
                if tools and self.tool_handler.supports_prompted and response.content:
                    response = self._handle_prompted_tool_execution(response, tools)

                return response

        except Exception as e:
            return GenerateResponse(
                content=f"Error generating response: {str(e)}",
                model=self.model,
                finish_reason="error"
            )

    def _generate_gguf(self,
                       prompt: str,
                       messages: Optional[List[Dict[str, str]]] = None,
                       system_prompt: Optional[str] = None,
                       tools: Optional[List[Dict[str, Any]]] = None,
                       media: Optional[List['MediaContent']] = None,
                       stream: bool = False,
                       **kwargs) -> Union[GenerateResponse, Iterator[GenerateResponse]]:
        """Generate using GGUF backend with llama-cpp-python"""

        if not self.llm:
            return GenerateResponse(
                content="Error: GGUF model not loaded",
                model=self.model,
                finish_reason="error"
            )

        # Build messages for chat completion
        chat_messages = []

        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})

        if messages:
            chat_messages.extend(messages)

        # Handle media content for the user message - use proper vision format for GGUF models
        if media:
            try:
                from ..architectures.detection import supports_vision

                # Check if this model supports vision natively
                if supports_vision(self.model):
                    # Use HuggingFace multimodal format for vision-capable GGUF models
                    user_message_content = []

                    # Add text content
                    user_message_content.append({"type": "text", "text": prompt})

                    # Add media content
                    for media_item in media:
                        if hasattr(media_item, 'file_path') and media_item.file_path:
                            # Use file:// URL format as specified in HuggingFace docs
                            file_path = str(media_item.file_path)
                            if not file_path.startswith('file://'):
                                file_path = f"file://{file_path}"
                            user_message_content.append({
                                "type": "image",
                                "image": file_path
                            })
                        elif hasattr(media_item, 'content') and media_item.content:
                            # For base64 or other content, we might need to save to temp file
                            import tempfile
                            import base64
                            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                                if isinstance(media_item.content, str) and media_item.content.startswith('data:'):
                                    # Handle base64 data URLs
                                    header, data = media_item.content.split(',', 1)
                                    decoded_data = base64.b64decode(data)
                                    tmp_file.write(decoded_data)
                                else:
                                    tmp_file.write(media_item.content)
                                tmp_file.flush()
                                user_message_content.append({
                                    "type": "image",
                                    "image": f"file://{tmp_file.name}"
                                })
                else:
                    # Fallback to text-based media handling for non-vision models
                    from ..media.handlers import LocalMediaHandler
                    media_handler = LocalMediaHandler("huggingface", self.model_capabilities, model_name=self.model)
                    multimodal_message = media_handler.create_multimodal_message(prompt, media)
                    user_message_content = multimodal_message if isinstance(multimodal_message, str) else prompt

            except ImportError:
                self.logger.warning("Media processing not available. Install with: pip install abstractcore[media]")
                user_message_content = prompt
            except Exception as e:
                self.logger.warning(f"Failed to process media content: {e}")
                user_message_content = prompt
        else:
            user_message_content = prompt

        chat_messages.append({"role": "user", "content": user_message_content})

        # Prepare parameters using unified system
        unified_kwargs = self._prepare_generation_kwargs(**kwargs)
        max_output_tokens = self._get_provider_max_tokens_param(unified_kwargs)

        generation_kwargs = {
            "messages": chat_messages,
            "max_tokens": max_output_tokens,  # This is max_output_tokens for llama-cpp
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", 0.9),
            "stream": stream
        }

        # Add seed if provided (GGUF/llama-cpp supports seed)
        seed_value = kwargs.get("seed", self.seed)
        if seed_value is not None:
            generation_kwargs["seed"] = seed_value

        # Handle tools - both native and prompted support
        has_native_tools = False
        if tools:
            # Check if model supports native tools - but fall back to prompted for now
            # TODO: Re-enable native tools once parameter default handling is fixed
            if False and self.llm.chat_format in ["chatml-function-calling", "functionary-v2"]:
                # Use unified tool handler for consistent formatting
                openai_tools = self.tool_handler.prepare_tools_for_native(tools)
                generation_kwargs["tools"] = openai_tools

                # Debug: Print what we're sending to the model
                print(f"DEBUG: Sending tools to HuggingFace model (unified handler):")
                import json
                print(json.dumps(openai_tools, indent=2))

                # Don't use auto for streaming (limitation of llama-cpp-python)
                if not stream:
                    generation_kwargs["tool_choice"] = "auto"
                has_native_tools = True

            elif self.tool_handler.supports_prompted:
                # Add tools as system prompt for prompted models
                tool_prompt = self.tool_handler.format_tools_prompt(tools)
                if chat_messages and chat_messages[0]["role"] == "system":
                    chat_messages[0]["content"] += f"\n\n{tool_prompt}"
                else:
                    chat_messages.insert(0, {"role": "system", "content": tool_prompt})
                generation_kwargs["messages"] = chat_messages

        try:
            if stream:
                return self._stream_generate_gguf_with_tools(generation_kwargs, tools, has_native_tools, kwargs.get('tool_call_tags'))
            else:
                response = self._single_generate_gguf(generation_kwargs)

                # Handle tool execution for both native and prompted responses
                if tools and (response.has_tool_calls() or
                             (self.tool_handler.supports_prompted and response.content)):
                    response = self._handle_tool_execution_gguf(response, tools, has_native_tools)

                return response

        except Exception as e:
            if stream:
                # Return error as a generator
                def error_generator():
                    yield GenerateResponse(
                        content=f"Error: {str(e)}",
                        model=self.model,
                        finish_reason="error"
                    )
                return error_generator()
            else:
                return GenerateResponse(
                    content=f"Error: {str(e)}",
                    model=self.model,
                    finish_reason="error"
                )

    def _single_generate_gguf(self, kwargs: Dict[str, Any]) -> GenerateResponse:
        """Generate single response using GGUF"""
        response = self.llm.create_chat_completion(**kwargs)

        choice = response['choices'][0]
        message = choice['message']

        # Extract tool calls if present
        tool_calls = None
        if 'tool_calls' in message:
            tool_calls = []
            for tc in message['tool_calls']:
                tool_calls.append({
                    "id": tc.get('id'),
                    "type": tc.get('type', 'function'),
                    "name": tc['function']['name'],
                    "arguments": tc['function']['arguments']
                })

        # Extract usage
        usage = None
        if 'usage' in response:
            usage = {
                "prompt_tokens": response['usage'].get('prompt_tokens', 0),
                "completion_tokens": response['usage'].get('completion_tokens', 0),
                "total_tokens": response['usage'].get('total_tokens', 0)
            }

        # Fix HTML escaping in llama-cpp-python responses
        content = message.get('content', '')
        if content:
            import html
            content = html.unescape(content)

        return GenerateResponse(
            content=content,
            model=self.model,
            finish_reason=choice.get('finish_reason', 'stop'),
            usage=usage,
            tool_calls=tool_calls
        )

    def _stream_generate_gguf(self, kwargs: Dict[str, Any], tool_call_tags: Optional[str] = None) -> Iterator[GenerateResponse]:
        """Stream response using GGUF with tool tag rewriting support"""
        stream = self.llm.create_chat_completion(**kwargs)

        current_tool_call = None
        accumulated_arguments = ""
        
        # Initialize tool tag rewriter if needed
        rewriter = None
        buffer = ""
        if tool_call_tags:
            try:
                from ..tools.tag_rewriter import create_tag_rewriter
                rewriter = create_tag_rewriter(tool_call_tags)
            except ImportError:
                pass

        for chunk in stream:
            if 'choices' not in chunk or not chunk['choices']:
                continue

            choice = chunk['choices'][0]
            delta = choice.get('delta', {})

            # Handle text content
            if 'content' in delta and delta['content']:
                # Fix HTML escaping in streaming content
                content = delta['content']
                if content:
                    import html
                    content = html.unescape(content)
                    
                    # Apply tool tag rewriting if enabled
                    if rewriter:
                        rewritten_content, buffer = rewriter.rewrite_streaming_chunk(content, buffer)
                        content = rewritten_content

                yield GenerateResponse(
                    content=content,
                    model=self.model,
                    finish_reason=choice.get('finish_reason')
                )

            # Handle tool calls
            if 'tool_calls' in delta:
                for tc in delta['tool_calls']:
                    if 'function' in tc:
                        if tc.get('id'):  # New tool call
                            if current_tool_call and accumulated_arguments:
                                # Yield the previous tool call
                                current_tool_call['arguments'] = accumulated_arguments
                                yield GenerateResponse(
                                    content="",
                                    model=self.model,
                                    tool_calls=[current_tool_call]
                                )

                            # Start new tool call
                            current_tool_call = {
                                "id": tc.get('id'),
                                "type": tc.get('type', 'function'),
                                "name": tc['function'].get('name'),
                                "arguments": ""
                            }
                            accumulated_arguments = tc['function'].get('arguments', '')
                        else:
                            # Accumulate arguments
                            if current_tool_call:
                                accumulated_arguments += tc['function'].get('arguments', '')

            # Handle finish reason
            if choice.get('finish_reason'):
                # Yield any pending tool call
                if current_tool_call and accumulated_arguments:
                    current_tool_call['arguments'] = accumulated_arguments
                    yield GenerateResponse(
                        content="",
                        model=self.model,
                        finish_reason=choice['finish_reason'],
                        tool_calls=[current_tool_call]
                    )
                else:
                    yield GenerateResponse(
                        content="",
                        model=self.model,
                        finish_reason=choice['finish_reason']
                    )

    def _single_generate_transformers(self, input_text: str, max_new_tokens: int,
                                     temperature: float, top_p: float, seed: Optional[int] = None) -> GenerateResponse:
        """Generate single response using transformers (original implementation)"""
        try:
            # Set seed for deterministic generation if provided
            if seed is not None:
                import torch
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)

            outputs = self.pipeline(
                input_text,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                truncation=True,
                return_full_text=False
            )

            if outputs and len(outputs) > 0:
                response_text = outputs[0]['generated_text'].strip()

                # Calculate token usage using centralized utilities
                usage = self._calculate_usage(input_text, response_text)

                return GenerateResponse(
                    content=response_text,
                    model=self.model,
                    finish_reason="stop",
                    usage=usage
                )
            else:
                return GenerateResponse(
                    content="",
                    model=self.model,
                    finish_reason="stop"
                )

        except Exception as e:
            return GenerateResponse(
                content=f"Error: {str(e)}",
                model=self.model,
                finish_reason="error"
            )

    def _calculate_usage(self, prompt: str, response: str) -> Dict[str, int]:
        """Calculate token usage using centralized token utilities."""
        from ..utils.token_utils import TokenUtils

        prompt_tokens = TokenUtils.estimate_tokens(prompt, self.model)
        completion_tokens = TokenUtils.estimate_tokens(response, self.model)
        total_tokens = prompt_tokens + completion_tokens

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

    def _stream_generate_transformers(self, input_text: str, max_new_tokens: int,
                                     temperature: float, top_p: float, tool_call_tags: Optional[str] = None, seed: Optional[int] = None) -> Iterator[GenerateResponse]:
        """Stream response using transformers (simulated, original implementation) with tool tag rewriting support"""
        try:
            # HuggingFace doesn't have native streaming, so we simulate it
            full_response = self._single_generate_transformers(input_text, max_new_tokens, temperature, top_p, seed)

            if full_response.content:
                # Apply tool tag rewriting if enabled
                content = full_response.content
                if tool_call_tags:
                    try:
                        from ..tools.tag_rewriter import create_tag_rewriter
                        rewriter = create_tag_rewriter(tool_call_tags)
                        content = rewriter.rewrite_text(content)
                    except ImportError:
                        pass
                
                words = content.split()
                for i, word in enumerate(words):
                    chunk_content = word + (" " if i < len(words) - 1 else "")
                    yield GenerateResponse(
                        content=chunk_content,
                        model=self.model,
                        finish_reason="stop" if i == len(words) - 1 else None
                    )
            else:
                yield GenerateResponse(
                    content="",
                    model=self.model,
                    finish_reason="stop"
                )

        except Exception as e:
            yield GenerateResponse(
                content=f"Error: {str(e)}",
                model=self.model,
                finish_reason="error"
            )

    def _build_input_text_transformers(self, prompt: str, messages: Optional[List[Dict[str, str]]],
                                      system_prompt: Optional[str], tools: Optional[List[Dict[str, Any]]] = None) -> str:
        """Build input text for transformers model with tool support"""

        # Add tools to system prompt if provided
        enhanced_system_prompt = system_prompt
        if tools and self.tool_handler.supports_prompted:
            tool_prompt = self.tool_handler.format_tools_prompt(tools)
            if enhanced_system_prompt:
                enhanced_system_prompt += f"\n\n{tool_prompt}"
            else:
                enhanced_system_prompt = tool_prompt

        # Check if model has chat template
        if hasattr(self.tokenizer, 'chat_template') and self.tokenizer.chat_template:
            # Use chat template if available
            chat_messages = []

            if enhanced_system_prompt:
                chat_messages.append({"role": "system", "content": enhanced_system_prompt})

            if messages:
                chat_messages.extend(messages)

            chat_messages.append({"role": "user", "content": prompt})

            try:
                return self.tokenizer.apply_chat_template(
                    chat_messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            except:
                # Fallback if chat template fails
                pass

        # Build simple conversational format
        text_parts = []

        if system_prompt:
            text_parts.append(f"System: {system_prompt}\n")

        if messages:
            for msg in messages:
                role = msg["role"].capitalize()
                content = msg["content"]
                text_parts.append(f"{role}: {content}\n")

        text_parts.append(f"User: {prompt}\n")
        text_parts.append("Assistant:")

        return "".join(text_parts)

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities supported by this provider"""
        capabilities = ["chat", "streaming"]

        if self.model_type == "gguf":
            capabilities.append("gguf")
            if self.llm and self.llm.chat_format:
                capabilities.append("tools")
        else:
            # Check for specific model capabilities
            model_lower = self.model.lower()

            if "gpt2" in model_lower or "dialogpt" in model_lower:
                capabilities.append("dialogue")

            if "codegen" in model_lower or "starcoder" in model_lower or "coder" in model_lower:
                capabilities.append("code")

        return capabilities

    def validate_config(self) -> bool:
        """Validate provider configuration"""
        if self.model_type == "gguf":
            return self.llm is not None
        else:
            return self.pipeline is not None


    # Removed override - using BaseProvider method with JSON capabilities

    def _get_provider_max_tokens_param(self, kwargs: Dict[str, Any]) -> int:
        """Get max tokens parameter appropriate for the model type"""
        max_output_tokens = kwargs.get("max_output_tokens", self.max_output_tokens)

        if self.model_type == "gguf":
            # For GGUF models, this is the generation limit
            return max_output_tokens
        else:
            # For transformers, this is max_new_tokens
            return max_output_tokens


    def _stream_generate_transformers_with_tools(self, input_text: str, max_new_tokens: int,
                                               temperature: float, top_p: float,
                                               tools: Optional[List[Dict[str, Any]]] = None,
                                               tool_call_tags: Optional[str] = None, seed: Optional[int] = None) -> Iterator[GenerateResponse]:
        """Stream generate with tool execution at the end"""
        collected_content = ""

        # Stream the response content
        for chunk in self._stream_generate_transformers(input_text, max_new_tokens, temperature, top_p, tool_call_tags, seed):
            collected_content += chunk.content
            yield chunk

        # Handle tool execution if we have tools and content
        if tools and self.tool_handler.supports_prompted and collected_content:
            # Create complete response for tool processing
            complete_response = GenerateResponse(
                content=collected_content,
                model=self.model,
                finish_reason="stop"
            )

            # Handle tool execution using base method
            final_response = self._handle_prompted_tool_execution(complete_response, tools)

            # If tools were executed, yield the tool results as final chunk
            if final_response.content != collected_content:
                tool_results_content = final_response.content[len(collected_content):]
                yield GenerateResponse(
                    content=tool_results_content,
                    model=self.model,
                    finish_reason="stop"
                )

    def _handle_tool_execution_gguf(self, response: GenerateResponse, tools: List[Dict[str, Any]], has_native_tools: bool) -> GenerateResponse:
        """Handle tool execution for GGUF responses - both native and prompted"""
        if has_native_tools and response.has_tool_calls():
            # Handle native tool calls using base method
            tool_calls = self._convert_native_tool_calls_to_standard(response.tool_calls)
            return self._execute_tools_with_events(response, tool_calls)
        elif self.tool_handler.supports_prompted and response.content:
            # Handle prompted tool calls using base method
            return self._handle_prompted_tool_execution(response, tools)

        return response

    def _stream_generate_gguf_with_tools(self, generation_kwargs: Dict[str, Any],
                                       tools: Optional[List[Dict[str, Any]]] = None,
                                       has_native_tools: bool = False,
                                       tool_call_tags: Optional[str] = None) -> Iterator[GenerateResponse]:
        """Stream generate GGUF with tool execution at the end"""
        collected_content = ""
        collected_tool_calls = []

        # Stream the response content
        for chunk in self._stream_generate_gguf(generation_kwargs, tool_call_tags):
            collected_content += chunk.content
            if chunk.tool_calls:
                collected_tool_calls.extend(chunk.tool_calls)
            yield chunk

        # Handle tool execution if we have tools and content/calls
        if tools and (collected_tool_calls or
                     (self.tool_handler.supports_prompted and collected_content)):
            # Create complete response for tool processing
            complete_response = GenerateResponse(
                content=collected_content,
                model=self.model,
                finish_reason="stop",
                tool_calls=collected_tool_calls
            )

            # Handle tool execution using simplified method
            final_response = self._handle_tool_execution_gguf(complete_response, tools, has_native_tools)

            # If tools were executed, yield the tool results as final chunk
            if final_response.content != collected_content:
                tool_results_content = final_response.content[len(collected_content):]
                yield GenerateResponse(
                    content=tool_results_content,
                    model=self.model,
                    finish_reason="stop"
                )

    @classmethod
    def list_available_models(cls, **kwargs) -> List[str]:
        """List available HuggingFace models from local cache (excluding MLX models)."""
        try:
            hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
            if not hf_cache.exists():
                return []

            models = []
            for item in hf_cache.iterdir():
                if item.is_dir() and item.name.startswith("models--"):
                    # Convert models--microsoft--DialoGPT-medium to microsoft/DialoGPT-medium
                    model_name = item.name.replace("models--", "").replace("--", "/")

                    # CRITICAL: Exclude MLX models from HuggingFace list
                    # Any model with "mlx" in the name should be classified as MLX, not HuggingFace
                    if "mlx" not in model_name.lower():
                        models.append(model_name)

            return sorted(models)

        except Exception:
            return []
