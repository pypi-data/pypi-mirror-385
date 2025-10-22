"""AgentBill SDK Client"""
import time
from typing import Any, Optional
from .tracer import AgentBillTracer
from .types import AgentBillConfig


class AgentBill:
    """
    AgentBill SDK for Python
    
    Example:
        >>> from agentbill import AgentBill
        >>> import openai
        >>> 
        >>> # Initialize AgentBill
        >>> agentbill = AgentBill.init({
        ...     "api_key": "your-api-key",
        ...     "customer_id": "customer-123",
        ...     "debug": True
        ... })
        >>> 
        >>> # Wrap your OpenAI client
        >>> client = agentbill.wrap_openai(openai.OpenAI(api_key="sk-..."))
        >>> 
        >>> # Use normally - all calls are tracked!
        >>> response = client.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Hello!"}]
        ... )
    """
    
    def __init__(self, config: AgentBillConfig):
        self.config = config
        self.tracer = AgentBillTracer(config)
    
    @classmethod
    def init(cls, config: AgentBillConfig) -> "AgentBill":
        """Initialize AgentBill SDK"""
        return cls(config)
    
    def wrap_openai(self, client: Any) -> Any:
        """Wrap OpenAI client to track usage across all endpoints"""
        
        # Track chat completions
        original_chat_create = client.chat.completions.create
        def tracked_chat_create(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting OpenAI chat.completions.create with model: {kwargs.get('model', 'unknown')}")
            
            start_time = time.time()
            span = self.tracer.start_span("openai.chat.completions.create", {
                "model": kwargs.get("model", "unknown"),
                "provider": "openai"
            })
            
            try:
                response = original_chat_create(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                span.set_attributes({
                    "response.prompt_tokens": response.usage.prompt_tokens,
                    "response.completion_tokens": response.usage.completion_tokens,
                    "response.total_tokens": response.usage.total_tokens,
                    "latency_ms": latency
                })
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.chat.completions.create = tracked_chat_create
        
        # Track embeddings
        original_embeddings_create = client.embeddings.create
        def tracked_embeddings_create(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting OpenAI embeddings.create with model: {kwargs.get('model', 'unknown')}")
            
            start_time = time.time()
            span = self.tracer.start_span("openai.embeddings.create", {
                "model": kwargs.get("model", "unknown"),
                "provider": "openai"
            })
            
            try:
                response = original_embeddings_create(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                span.set_attributes({
                    "response.prompt_tokens": response.usage.prompt_tokens,
                    "response.total_tokens": response.usage.total_tokens,
                    "latency_ms": latency
                })
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.embeddings.create = tracked_embeddings_create
        
        # Track image generation
        original_images_generate = client.images.generate
        def tracked_images_generate(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting OpenAI images.generate")
            
            start_time = time.time()
            span = self.tracer.start_span("openai.images.generate", {
                "model": kwargs.get("model", "dall-e-3"),
                "provider": "openai",
                "size": kwargs.get("size", "1024x1024"),
                "quality": kwargs.get("quality", "standard")
            })
            
            try:
                response = original_images_generate(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                span.set_attributes({"latency_ms": latency})
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.images.generate = tracked_images_generate
        
        # Track audio transcription (Whisper)
        original_audio_transcriptions_create = client.audio.transcriptions.create
        def tracked_audio_transcriptions_create(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting OpenAI audio.transcriptions.create")
            
            start_time = time.time()
            span = self.tracer.start_span("openai.audio.transcriptions.create", {
                "model": kwargs.get("model", "whisper-1"),
                "provider": "openai"
            })
            
            try:
                response = original_audio_transcriptions_create(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                span.set_attributes({"latency_ms": latency})
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.audio.transcriptions.create = tracked_audio_transcriptions_create
        
        # Track text-to-speech
        original_audio_speech_create = client.audio.speech.create
        def tracked_audio_speech_create(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting OpenAI audio.speech.create")
            
            start_time = time.time()
            span = self.tracer.start_span("openai.audio.speech.create", {
                "model": kwargs.get("model", "tts-1"),
                "provider": "openai",
                "voice": kwargs.get("voice", "alloy")
            })
            
            try:
                response = original_audio_speech_create(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                span.set_attributes({"latency_ms": latency})
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.audio.speech.create = tracked_audio_speech_create
        
        # Track moderations
        original_moderations_create = client.moderations.create
        def tracked_moderations_create(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting OpenAI moderations.create")
            
            start_time = time.time()
            span = self.tracer.start_span("openai.moderations.create", {
                "model": kwargs.get("model", "text-moderation-latest"),
                "provider": "openai"
            })
            
            try:
                response = original_moderations_create(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                span.set_attributes({"latency_ms": latency})
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.moderations.create = tracked_moderations_create
        
        return client
    
    def wrap_anthropic(self, client: Any) -> Any:
        """Wrap Anthropic client to track usage"""
        original_create = client.messages.create
        
        def tracked_create(*args, **kwargs):
            start_time = time.time()
            
            span = self.tracer.start_span("anthropic.message", {
                "model": kwargs.get("model", "unknown"),
                "provider": "anthropic"
            })
            
            try:
                response = original_create(*args, **kwargs)
                
                latency = (time.time() - start_time) * 1000
                span.set_attributes({
                    "response.input_tokens": response.usage.input_tokens,
                    "response.output_tokens": response.usage.output_tokens,
                    "latency_ms": latency
                })
                span.set_status(0)
                
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.messages.create = tracked_create
        return client
    
    def wrap_bedrock(self, client: Any) -> Any:
        """Wrap AWS Bedrock client to track usage"""
        original_invoke_model = client.invoke_model
        
        def tracked_invoke_model(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting Bedrock invoke_model with model: {kwargs.get('modelId', 'unknown')}")
            
            start_time = time.time()
            span = self.tracer.start_span("bedrock.invoke_model", {
                "model": kwargs.get("modelId", "unknown"),
                "provider": "bedrock"
            })
            
            try:
                response = original_invoke_model(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                
                # Parse response body for token usage
                import json
                body = json.loads(response['body'].read())
                
                # Handle different Bedrock model response formats
                if 'usage' in body:  # Claude models
                    span.set_attributes({
                        "response.input_tokens": body['usage'].get('input_tokens', 0),
                        "response.output_tokens": body['usage'].get('output_tokens', 0),
                        "latency_ms": latency
                    })
                elif 'inputTextTokenCount' in body:  # Titan models
                    span.set_attributes({
                        "response.input_tokens": body.get('inputTextTokenCount', 0),
                        "response.output_tokens": body['results'][0].get('tokenCount', 0) if 'results' in body else 0,
                        "latency_ms": latency
                    })
                
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.invoke_model = tracked_invoke_model
        return client
    
    def wrap_azure_openai(self, client: Any) -> Any:
        """Wrap Azure OpenAI client to track usage"""
        # Azure OpenAI uses the same API as OpenAI
        original_create = client.chat.completions.create
        
        def tracked_create(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting Azure OpenAI chat.completions.create")
            
            start_time = time.time()
            span = self.tracer.start_span("azure_openai.chat.completions", {
                "model": kwargs.get("model", "unknown"),
                "provider": "azure_openai"
            })
            
            try:
                response = original_create(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                span.set_attributes({
                    "response.prompt_tokens": response.usage.prompt_tokens,
                    "response.completion_tokens": response.usage.completion_tokens,
                    "response.total_tokens": response.usage.total_tokens,
                    "latency_ms": latency
                })
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.chat.completions.create = tracked_create
        return client
    
    def wrap_mistral(self, client: Any) -> Any:
        """Wrap Mistral AI client to track usage"""
        original_create = client.chat.complete
        
        def tracked_create(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting Mistral chat.complete with model: {kwargs.get('model', 'unknown')}")
            
            start_time = time.time()
            span = self.tracer.start_span("mistral.chat.complete", {
                "model": kwargs.get("model", "unknown"),
                "provider": "mistral"
            })
            
            try:
                response = original_create(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                span.set_attributes({
                    "response.prompt_tokens": response.usage.prompt_tokens,
                    "response.completion_tokens": response.usage.completion_tokens,
                    "response.total_tokens": response.usage.total_tokens,
                    "latency_ms": latency
                })
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.chat.complete = tracked_create
        return client
    
    def wrap_google_ai(self, client: Any) -> Any:
        """Wrap Google AI (Gemini) client to track usage"""
        original_generate_content = client.generate_content
        
        def tracked_generate_content(*args, **kwargs):
            if self.config.get("debug"):
                print(f"[AgentBill] Intercepting Google AI generate_content")
            
            start_time = time.time()
            span = self.tracer.start_span("google_ai.generate_content", {
                "model": getattr(client, '_model_name', 'unknown'),
                "provider": "google_ai"
            })
            
            try:
                response = original_generate_content(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                
                # Google AI has usage metadata
                if hasattr(response, 'usage_metadata'):
                    span.set_attributes({
                        "response.prompt_tokens": response.usage_metadata.prompt_token_count,
                        "response.completion_tokens": response.usage_metadata.candidates_token_count,
                        "response.total_tokens": response.usage_metadata.total_token_count,
                        "latency_ms": latency
                    })
                
                span.set_status(0)
                return response
            except Exception as e:
                span.set_status(1, str(e))
                raise
            finally:
                span.end()
        
        client.generate_content = tracked_generate_content
        return client
    
    def track_signal(self, event_name: str, revenue: float = 0, data: dict = None):
        """Track a custom signal/event with revenue"""
        import httpx
        import time
        
        url = f"{self.config.get('base_url', 'https://bgwyprqxtdreuutzpbgw.supabase.co')}/functions/v1/record-signals"
        
        payload = {
            "event_name": event_name,
            "revenue": revenue,
            "customer_id": self.config.get("customer_id"),
            "timestamp": time.time(),
            "data": data or {}
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                if self.config.get("debug"):
                    print(f"[AgentBill] Signal tracked: {event_name}, revenue: ${revenue}")
        except Exception as e:
            if self.config.get("debug"):
                print(f"[AgentBill] Failed to track signal: {e}")
    
    async def flush(self):
        """Flush pending telemetry data"""
        await self.tracer.flush()
