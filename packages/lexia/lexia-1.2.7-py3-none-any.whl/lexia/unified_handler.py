"""
Unified Lexia Handler
=====================

Single, clean interface for all Lexia platform communication.
Supports both production (Centrifugo) and dev mode (in-memory streaming).
"""

import logging
import threading
import os
import traceback
from urllib.parse import urlparse
from .centrifugo_client import CentrifugoClient
from .dev_stream_client import DevStreamClient
from .api_client import APIClient
from .response_handler import create_complete_response

logger = logging.getLogger(__name__)


class LexiaHandler:
    """Clean, unified interface for all Lexia communication."""
    
    def __init__(self, dev_mode: bool = None):
        """
        Initialize LexiaHandler with optional dev mode.
        
        Args:
            dev_mode: If True, uses DevStreamClient instead of Centrifugo.
                     If None, checks LEXIA_DEV_MODE environment variable.
        """
        # Determine dev mode from parameter or environment
        if dev_mode is None:
            dev_mode = os.environ.get('LEXIA_DEV_MODE', 'false').lower() in ('true', '1', 'yes')
        
        self.dev_mode = dev_mode
        
        # Initialize appropriate streaming client
        if self.dev_mode:
            self.stream_client = DevStreamClient()
            logger.info("🔧 LexiaHandler initialized in DEV MODE (no Centrifugo)")
        else:
            self.stream_client = CentrifugoClient()
            logger.info("🚀 LexiaHandler initialized in PRODUCTION MODE (Centrifugo)")
        
        self.api = APIClient()
        
        # Internal aggregation buffers keyed by response UUID
        self._buffers = {}
        self._buffers_lock = threading.Lock()
        
        # Simple alias map to turn semantic commands into Lexia markers
        self._marker_aliases = {
            # image
            'show image load': "[lexia.loading.image.start]\n\n",
            'end image load': "[lexia.loading.image.end]\n\n",
            'hide image load': "[lexia.loading.image.end]\n\n",
            # code
            'show code load': "[lexia.loading.code.start]\n\n",
            'end code load': "[lexia.loading.code.end]\n\n",
            # search
            'show search load': "[lexia.loading.search.start]\n\n",
            'end search load': "[lexia.loading.search.end]\n\n",
            # thinking
            'show thinking load': "[lexia.loading.thinking.start]\n\n",
            'end thinking load': "[lexia.loading.thinking.end]\n\n",
        }

    def _get_loading_marker(self, kind: str, action: str) -> str:
        """Return a standardized loading marker string for a given kind/action."""
        kind_norm = (kind or '').strip().lower()
        if kind_norm not in ("image", "code", "search", "thinking"):
            kind_norm = "thinking"
        action_norm = "start" if action == "start" else "end"
        return f"[lexia.loading.{kind_norm}.{action_norm}]\n\n"

    # Per-response session object to avoid passing data repeatedly
    class _Session:
        def __init__(self, handler: 'LexiaHandler', data):
            self._handler = handler
            # Keep original request object to preserve headers/urls/ids
            self._data = data
            # Optionally preconfigure centrifugo (prod only)
            if (not handler.dev_mode and 
                hasattr(data, 'stream_url') and hasattr(data, 'stream_token')):
                handler.update_centrifugo_config(data.stream_url, data.stream_token)

        def stream(self, content: str) -> None:
            self._handler.stream(self._data, content)

        def close(self, usage_info=None, file_url=None) -> str:
            return self._handler.close(self._data, usage_info=usage_info, file_url=file_url)

        def error(self, error_message: str, exception: Exception = None, trace: str = None) -> None:
            self._handler.send_error(self._data, error_message, trace=trace, exception=exception)

        # Developer-friendly loading helpers
        def start_loading(self, kind: str = "thinking") -> None:
            marker = self._handler._get_loading_marker(kind, "start")
            self._handler.stream(self._data, marker)

        def end_loading(self, kind: str = "thinking") -> None:
            marker = self._handler._get_loading_marker(kind, "end")
            self._handler.stream(self._data, marker)

        # Image helper: wrap URL with lexia image markers
        def image(self, url: str) -> None:
            if not url:
                return
            payload = f"[lexia.image.start]{url}[lexia.image.end]"
            self._handler.stream(self._data, payload)

        # Alias for developer preference
        def pass_image(self, url: str) -> None:
            self.image(url)

    def begin(self, data) -> '_Session':
        """
        Start a streaming session bound to a single response.
        Returns a session with stream()/close()/error() methods.
        """
        return LexiaHandler._Session(self, data)
    
    def update_centrifugo_config(self, stream_url: str, stream_token: str):
        """
        Update Centrifugo configuration with dynamic values from request.
        Only applicable in production mode.
        
        Args:
            stream_url: Centrifugo server URL from request
            stream_token: Centrifugo API key from request
        """
        if self.dev_mode:
            logger.debug("Dev mode active - skipping Centrifugo config update")
            return
        
        if stream_url and stream_token:
            self.stream_client.update_config(stream_url, stream_token)
            logger.info(f"Updated Centrifugo config - URL: {stream_url}")
        else:
            logger.warning("Stream URL or token not provided, using default configuration")
    
    def stream_chunk(self, data, content: str):
        """
        Stream a chunk of AI response.
        Uses DevStreamClient in dev mode, Centrifugo in production.
        """
        logger.info(f"🟢 [3-HANDLER] stream_chunk() called with '{content}' ({len(content)} chars)")
        
        # Update config if dynamic values are provided (production only)
        if not self.dev_mode and hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        self.stream_client.send_delta(data.channel, data.response_uuid, data.thread_id, content)
        logger.info(f"🟢 [4-HANDLER] Chunk sent to stream_client.send_delta()")
    
    # New simplified streaming API: accumulate + stream
    def stream(self, data, content: str) -> None:
        """Stream a chunk and aggregate it internally for later completion."""
        # Normalize semantic commands to markers when possible
        if isinstance(content, str):
            key = content.strip().lower()
            content = self._marker_aliases.get(key, content)
        
        # Append to buffer (thread-safe)
        with self._buffers_lock:
            bucket = self._buffers.get(getattr(data, 'response_uuid', None))
            if bucket is None:
                bucket = []
                self._buffers[data.response_uuid] = bucket
            bucket.append(content)
        # Forward live chunk to clients
        self.stream_chunk(data, content)

    def _drain_buffer(self, response_uuid: str) -> str:
        """Join and clear the buffer for a response UUID (thread-safe)."""
        with self._buffers_lock:
            parts = self._buffers.pop(response_uuid, None)
        if not parts:
            return ""
        return "".join(parts)

    def complete_response(self, data, full_response: str, usage_info=None, file_url=None):
        """
        Complete AI response and send to Lexia.
        Uses DevStreamClient in dev mode, Centrifugo in production.
        """
        # Update config if dynamic values are provided (production only)
        if not self.dev_mode and hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        # Send completion via appropriate streaming client
        self.stream_client.send_completion(data.channel, data.response_uuid, data.thread_id, full_response)
        
        # Create complete response with all required fields
        backend_data = create_complete_response(data.response_uuid, data.thread_id, full_response, usage_info, file_url)
        backend_data['conversation_id'] = data.conversation_id
        
        # Ensure required fields have proper values even if usage_info is missing
        if not usage_info or usage_info.get('prompt_tokens', 0) == 0:
            # Provide default values when usage info is missing
            backend_data['usage'] = {
                'input_tokens': 1,  # Minimum token count
                'output_tokens': len(full_response.split()) if full_response else 1,  # Estimate from response length
                'total_tokens': 1 + (len(full_response.split()) if full_response else 1),
                'input_token_details': {
                    'tokens': [{"token": "default", "logprob": 0.0}]
                },
                'output_token_details': {
                    'tokens': [{"token": "default", "logprob": 0.0}]
                }
            }
        
        # In dev mode, skip backend API call if URL is not provided
        if self.dev_mode and (not hasattr(data, 'url') or not data.url):
            logger.info("🔧 Dev mode: Skipping backend API call (no URL provided)")
            return
        
        # Extract headers from request data
        request_headers = {}
        if hasattr(data, 'headers') and data.headers:
            request_headers.update(data.headers)
            logger.info(f"Extracted headers from request: {request_headers}")
        
        # Skip if no URL provided (optional in dev mode)
        if not hasattr(data, 'url') or not data.url:
            logger.warning("⚠️  No URL provided, skipping backend API call")
            return
        
        logger.info(f"=== SENDING TO LEXIA API ===")
        logger.info(f"URL: {data.url}")
        logger.info(f"Headers: {request_headers}")
        logger.info(f"Data: {backend_data}")
        
        # Send to Lexia backend with headers
        try:
            response = self.api.post(data.url, backend_data, headers=request_headers)
            
            logger.info(f"=== LEXIA API RESPONSE ===")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Content: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"LEXIA API ERROR: {response.status_code} - {response.text}")
            else:
                logger.info("✅ LEXIA API SUCCESS: Response accepted")
        except Exception as e:
            logger.error(f"Failed to send to Lexia API: {e}")
        
        # Update if different URL
        # if data.url_update and data.url_update != data.url:
        #     update_data = create_complete_response(data.response_uuid, data.thread_id, full_response, usage_info)
        #     update_data['conversation_id'] = data.conversation_id
            
        #     # Ensure update data also has proper usage values
        #     if not usage_info or usage_info.get('prompt_tokens', 0) == 0:
        #         update_data['usage'] = {
        #             'input_tokens': 1,
        #             'output_tokens': len(full_response.split()) if full_response else 1,
        #             'total_tokens': 1 + (len(full_response.split()) if full_response else 1),
        #             'input_token_details': {
        #                 'tokens': [{"token": "default", "logprob": 0.0}]
        #             },
        #             'output_token_details': {
        #                 'tokens': [{"token": "default", "logprob": 0.0}]
        #             }
        #         }
            
        #     logger.info(f"=== SENDING UPDATE TO LEXIA API ===")
        #     logger.info(f"Update URL: {data.url_update}")
        #     logger.info(f"Update Headers: {request_headers}")
        #     logger.info(f"Update Data: {update_data}")
            
        #     update_response = self.api.put(data.url_update, update_data, headers=request_headers)
            
        #     logger.info(f"=== LEXIA UPDATE API RESPONSE ===")
        #     logger.info(f"Update Status Code: {update_response.status_code}")
        #     logger.info(f"Update Response Content: {update_response.text}")
            
        #     if update_response.status_code != 200:
        #         logger.error(f"LEXIA UPDATE API ERROR: {update_response.status_code} - {update_response.text}")
        #     else:
        #         logger.info("✅ LEXIA UPDATE API SUCCESS: Update accepted")

    # New simplified close API: finalize using aggregated buffer
    def close(self, data, usage_info=None, file_url=None) -> str:
        """
        Finalize the response using the internally aggregated content.
        Returns the finalized full text for optional caller-side persistence.
        """
        full_response = self._drain_buffer(getattr(data, 'response_uuid', None))
        self.complete_response(data, full_response, usage_info, file_url)
        return full_response
    
    def send_error(self, data, error_message: str, trace: str = None, exception: Exception = None):
        """
        Send error message via streaming client and persist to backend API.
        Uses DevStreamClient in dev mode, Centrifugo in production.
        
        Args:
            data: Request data containing channel, UUID, thread_id, etc.
            error_message: Error message to send
            trace: Optional stack trace string
            exception: Optional exception object (will extract trace from it)
        """
        # Update config if dynamic values are provided (production only)
        if not self.dev_mode and hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        # Format error message for display
        error_display_message = f"❌ **Error:** {error_message}"
        
        # In DEV mode: Stream exactly like normal responses (chunk + complete)
        if self.dev_mode:
            # Clear any pending aggregation for this response
            self._drain_buffer(getattr(data, 'response_uuid', None))
            # Stream the error message as chunks (same as normal content)
            self.stream_client.send_delta(data.channel, data.response_uuid, data.thread_id, error_display_message)
            # Complete the stream (same as normal completion)
            self.stream_client.send_completion(data.channel, data.response_uuid, data.thread_id, error_display_message)
            logger.info("🔧 Dev mode: Error streamed to frontend (delta + complete), skipping backend API calls")
            return
        
        # PRODUCTION mode: Different flow for Centrifugo
        # First stream the error as visible content
        self.stream_client.send_delta(data.channel, data.response_uuid, data.thread_id, error_display_message)
        # Then send error signal via Centrifugo
        self.stream_client.send_error(data.channel, data.response_uuid, data.thread_id, error_message)
        # Clear any pending aggregation for this response
        self._drain_buffer(getattr(data, 'response_uuid', None))
        
        # Skip if no URL provided (production mode only)
        if not hasattr(data, 'url') or not data.url:
            logger.warning("⚠️  No URL provided, skipping error API call")
            return
        
        # Also persist error to backend API (like previous implementation)
        error_response = {
            'uuid': data.response_uuid,
            'conversation_id': data.conversation_id,
            'content': error_message,
            'role': 'developer',
            'status': 'FAILED',
            'usage': {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'input_token_details': {
                    'tokens': []
                },
                'output_token_details': {
                    'tokens': []
                }
            }
        }
        
        # Extract headers from request data
        request_headers = {}
        if hasattr(data, 'headers') and data.headers:
            request_headers.update(data.headers)
            logger.info(f"Extracted headers from request for error: {request_headers}")
        
        logger.info(f"=== SENDING ERROR TO LEXIA API ===")
        logger.info(f"URL: {data.url}")
        logger.info(f"Headers: {request_headers}")
        logger.info(f"Error Data: {error_response}")
        
        # Send error to Lexia backend with headers
        try:
            response = self.api.post(data.url, error_response, headers=request_headers)
            
            logger.info(f"=== LEXIA ERROR API RESPONSE ===")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Content: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"LEXIA ERROR API FAILED: {response.status_code} - {response.text}")
            else:
                logger.info("✅ LEXIA ERROR API SUCCESS: Error persisted to backend")
        except Exception as e:
            logger.error(f"Failed to persist error to backend API: {e}")
        
        # Also send error to logging endpoint (api/internal/v1/logs)
        try:
            # Extract base URL from data.url
            parsed_url = urlparse(data.url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            log_url = f"{base_url}/api/internal/v1/logs"
            
            # Get stack trace from various sources
            trace_info = ''
            if trace:
                # Use provided trace string
                trace_info = trace
            elif exception:
                # Extract trace from exception object
                trace_info = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            else:
                # Try to get current exception context
                exc_info = traceback.format_exc()
                if exc_info and exc_info != 'NoneType: None\n':
                    trace_info = exc_info
            
            # Prepare log payload according to Laravel API spec
            log_payload = {
                'message': error_message[:1000],  # Max 1000 chars as per validation
                'trace': trace_info[:5000] if trace_info else '',  # Max 5000 chars as per validation
                'level': 'error',  # error, warning, info, or critical
                'where': 'lexia-sdk',  # Where the error occurred
                'additional': {
                    'uuid': data.response_uuid,
                    'conversation_id': data.conversation_id,
                    'thread_id': data.thread_id,
                    'channel': data.channel
                }
            }
            
            logger.info(f"=== SENDING ERROR LOG TO LEXIA ===")
            logger.info(f"Log URL: {log_url}")
            logger.info(f"Log Payload: {log_payload}")
            
            # Send to logging endpoint
            log_response = self.api.post(log_url, log_payload, headers=request_headers)
            
            logger.info(f"=== LEXIA LOG API RESPONSE ===")
            logger.info(f"Status Code: {log_response.status_code}")
            logger.info(f"Response Content: {log_response.text}")
            
            if log_response.status_code != 200:
                logger.error(f"LEXIA LOG API FAILED: {log_response.status_code} - {log_response.text}")
            else:
                logger.info("✅ LEXIA LOG API SUCCESS: Error logged to backend")
        except Exception as e:
            logger.error(f"Failed to send error log to Lexia: {e}")
