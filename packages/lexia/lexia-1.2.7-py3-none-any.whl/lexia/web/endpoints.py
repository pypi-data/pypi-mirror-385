"""
Lexia Standard Endpoints
========================

Standard endpoint patterns for Lexia applications.
These can be added to any FastAPI app using add_standard_endpoints().
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
import logging
import asyncio
import json
import time
import threading

logger = logging.getLogger(__name__)

def add_standard_endpoints(app, conversation_manager=None, lexia_handler=None, process_message_func=None):
    """
    Add standard Lexia endpoints to a FastAPI application.
    
    Args:
        app: FastAPI application instance
        conversation_manager: Optional conversation manager for history endpoints
        lexia_handler: Optional LexiaHandler instance for communication
        process_message_func: Optional function to process messages (custom AI logic)
    """
    
    # Create router for standard endpoints
    router = APIRouter(prefix="/api/v1", tags=["standard"])
    
    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy", 
            "service": "Lexia AI Agent",
            "version": "1.1.0"
        }
    
    @router.get("/test_stream")
    async def test_stream():
        """Test streaming endpoint to verify browser streaming works."""
        async def generate():
            for i in range(10):
                chunk = f"Chunk {i+1} "
                yield chunk.encode('utf-8')
                yield b''  # Force flush
                await asyncio.sleep(0.3)  # 300ms delay between chunks
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )
    
    @router.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "message": "Lexia AI Agent - Ready",
            "endpoints": [
                "/api/v1/health",
                "/api/v1/send_message",
                "/api/v1/stream/{channel}",
                "/docs"
            ]
        }
    
    @router.get("/stream/{channel}")
    async def stream_updates(channel: str):
        """
        SSE (Server-Sent Events) endpoint for dev mode streaming.
        Frontend can connect to this to receive real-time updates.
        """
        from ..dev_stream_client import DevStreamClient
        
        async def event_generator():
            """Generate SSE events from DevStreamClient."""
            last_chunk_count = 0
            
            # Send initial connection event
            yield f"data: {json.dumps({'event': 'connected', 'channel': channel})}\n\n"
            
            # Poll for updates (in real app, use proper async notifications)
            for _ in range(300):  # 5 minutes max (300 * 1 second)
                stream_data = DevStreamClient.get_stream(channel)
                
                # Send new chunks
                current_chunk_count = len(stream_data['chunks'])
                if current_chunk_count > last_chunk_count:
                    new_chunks = stream_data['chunks'][last_chunk_count:]
                    for chunk in new_chunks:
                        yield f"data: {json.dumps({'event': 'delta', 'content': chunk})}\n\n"
                    last_chunk_count = current_chunk_count
                
                # Check if finished
                if stream_data['finished']:
                    if stream_data['error']:
                        yield f"data: {json.dumps({'event': 'error', 'content': stream_data['error']})}\n\n"
                    else:
                        yield f"data: {json.dumps({'event': 'complete', 'content': stream_data['full_response']})}\n\n"
                    break
                
                await asyncio.sleep(0.1)  # Check every 100ms
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    @router.get("/poll/{channel}")
    async def poll_stream(channel: str):
        """
        Simple polling endpoint for dev mode (alternative to SSE).
        Returns current stream state.
        """
        from ..dev_stream_client import DevStreamClient
        
        stream_data = DevStreamClient.get_stream(channel)
        return {
            "channel": channel,
            "chunks_count": len(stream_data['chunks']),
            "full_response": stream_data['full_response'],
            "finished": stream_data['finished'],
            "error": stream_data['error']
        }
    
    # Add the main send_message endpoint if lexia_handler is provided
    if lexia_handler and process_message_func:
        from ..models import ChatMessage, ChatResponse
        from ..response_handler import create_success_response
        
        @router.post("/send_message")
        async def send_message(data: ChatMessage):
            """Main chat endpoint - inherited from Lexia package."""
            if not data.message.strip() or not data.channel or not data.variables:
                raise HTTPException(status_code=400, detail="Missing required fields")
            
            # DEV MODE: Return streaming response directly
            if lexia_handler.dev_mode:
                logger.info("🔧 Dev mode: Streaming response directly")
                
                async def stream_generator():
                    """Generate streaming response directly from processing using async queue."""
                    from ..dev_stream_client import DevStreamClient
                    
                    # Clear any existing stream data for this channel
                    DevStreamClient.clear_stream(data.channel)
                    logger.info(f"🔴 [INIT] Cleared stream for channel: {data.channel}")
                    
                    # CRITICAL: Create queue BEFORE starting background task
                    queue = DevStreamClient.get_or_create_queue(data.channel)
                    logger.info(f"🔴 [INIT] Queue created/retrieved: {id(queue)}")
                    
                    # CRITICAL: Send initial SSE comment to establish streaming connection
                    # This forces browsers/proxies to start streaming immediately
                    yield ": connected\n\n".encode('utf-8')
                    logger.info(f"🔴 [INIT] Sent initial SSE comment to establish connection")
                    
                    # Small delay to ensure the connection is established
                    await asyncio.sleep(0.01)
                    
                    # Start processing in a background THREAD to avoid blocking event loop in dev mode
                    logger.info(f"🔴 [INIT] Starting background thread for channel: {data.channel}")
                    def _run_in_thread():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(process_message_func(data))
                        except Exception as e:
                            logger.error(f"Background thread error: {e}")
                        finally:
                            try:
                                loop.close()
                            except Exception:
                                pass
                    bg_thread = threading.Thread(target=_run_in_thread, daemon=True)
                    bg_thread.start()
                    logger.info(f"🔴 [INIT] Background thread started: {bg_thread.name}")
                    
                    # Wait for chunks from the queue (TRUE REAL-TIME!)
                    chunk_buffer = ""
                    chunk_count = 0
                    try:
                        logger.info(f"🔴 [10-ENDPOINT] Starting to wait for queue items...")
                        while True:
                            # Wait for next item from queue with timeout
                            try:
                                logger.info(f"🔴 [11-ENDPOINT] Waiting for queue.get()...")
                                event_type, content = await asyncio.wait_for(queue.get(), timeout=30.0)
                                chunk_count += 1
                                logger.info(f"🔴 [12-ENDPOINT] Got from queue! Type: {event_type}, Content: '{content}' ({len(content)} chars) - Chunk #{chunk_count}")
                                
                                if event_type == 'delta':
                                    # Add to buffer
                                    chunk_buffer += content
                                    
                                    # Send as SSE format with explicit data: prefix and double newline
                                    # SSE format forces browsers to process immediately
                                    sse_chunk = f"data: {content}\n\n"
                                    chunk_data = sse_chunk.encode('utf-8')
                                    logger.info(f"🔴 [13-ENDPOINT] About to yield SSE chunk: {len(chunk_data)} bytes")
                                    yield chunk_data
                                    logger.info(f"🔴 [14-ENDPOINT] Yielded SSE chunk to HTTP response!")
                                    
                                elif event_type == 'complete':
                                    # Streaming finished
                                    break
                                elif event_type == 'error':
                                    # Error occurred
                                    error_msg = f"\n\n❌ Error: {content}"
                                    yield error_msg.encode('utf-8')
                                    break
                                    
                            except asyncio.TimeoutError:
                                # No data yet; continue waiting
                                pass
                    finally:
                        # Clean up
                        DevStreamClient.clear_stream(data.channel)
                
                # Use SSE format for better browser streaming support
                return StreamingResponse(
                    stream_generator(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0",
                        "X-Accel-Buffering": "no",
                        "Connection": "keep-alive"
                    }
                )
            
            # PRODUCTION MODE: Return immediate response, process in background
            else:
                logger.info("🚀 Production mode: Processing in background")
                # Start processing in background
                asyncio.create_task(process_message_func(data))
                
                # Return immediate success response
                return create_success_response(
                    response_uuid=data.response_uuid,
                    thread_id=data.thread_id
                )
    
    # Add conversation history endpoints if conversation manager is provided
    if conversation_manager:
        @router.get("/conversation/{thread_id}/history")
        async def get_history(thread_id: str):
            """Get conversation history for a thread."""
            try:
                history = conversation_manager.get_history(thread_id)
                return {
                    "thread_id": thread_id, 
                    "history": history, 
                    "count": len(history)
                }
            except Exception as e:
                logger.error(f"Error getting history for thread {thread_id}: {e}")
                raise HTTPException(status_code=500, detail="Failed to get conversation history")
        
        @router.delete("/conversation/{thread_id}/history")
        async def clear_history(thread_id: str):
            """Clear conversation history for a thread."""
            try:
                conversation_manager.clear_history(thread_id)
                return {
                    "status": "success", 
                    "thread_id": thread_id,
                    "message": "Conversation history cleared"
                }
            except Exception as e:
                logger.error(f"Error clearing history for thread {thread_id}: {e}")
                raise HTTPException(status_code=500, detail="Failed to clear conversation history")
    
    # Include the router in the app
    app.include_router(router)
    
    return app
