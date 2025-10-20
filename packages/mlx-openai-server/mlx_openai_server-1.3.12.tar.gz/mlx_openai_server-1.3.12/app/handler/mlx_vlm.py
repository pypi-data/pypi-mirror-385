import asyncio
import base64
import time
import uuid
import gc

from loguru import logger
from http import HTTPStatus
from fastapi import HTTPException
from typing import Any, Dict, List, Optional, Tuple

from app.core.queue import RequestQueue
from app.models.mlx_vlm import MLX_VLM
from app.handler.parser import (
    Qwen3ToolParser, Glm4MoEThinkingParser, Glm4MoEToolParser   
)
from app.core import ImageProcessor, AudioProcessor, VideoProcessor
from app.utils.errors import create_error_response
from app.schemas.openai import ChatCompletionRequest, EmbeddingRequest, ChatCompletionContentPart, ChatCompletionContentPartText, ChatCompletionContentPartImage, ChatCompletionContentPartInputAudio, ChatCompletionContentPartVideo

class MLXVLMHandler:
    """
    Handler class for making requests to the underlying MLX multimodal model service.
    Provides caching, concurrent image processing, audio processing, and robust error handling.
    """

    def __init__(self, model_path: str, context_length: int = None, max_workers: int = 4, max_concurrency: int = 1, disable_auto_resize: bool = False):
        """
        Initialize the handler with the specified model path.
        
        Args:
            model_path (str): Path to the model directory.
            max_workers (int): Maximum number of worker threads for image processing.
            max_concurrency (int): Maximum number of concurrent model inference tasks.
            disable_auto_resize (bool): Whether to disable automatic image resizing.
        """
        self.model_path = model_path
        self.model = MLX_VLM(model_path)
        self.image_processor = ImageProcessor(max_workers)
        self.audio_processor = AudioProcessor(max_workers)
        self.video_processor = VideoProcessor(max_workers)
        self.disable_auto_resize = disable_auto_resize
        self.model_created = int(time.time())  # Store creation time when model is loaded
        self.model_type = self.model.get_model_type()

        # Initialize request queue for multimodal and text tasks
        # We use the same queue for both multimodal and text tasks for simplicity
        # and to ensure we don't overload the model with too many concurrent requests
        self.request_queue = RequestQueue(max_concurrency=max_concurrency)
        
        logger.info(f"Initialized MLXHandler with model path: {model_path}")
        if disable_auto_resize:
            logger.info("Auto-resize is disabled for image processing")

    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models with their metadata.
        """
        try:
            return [{
                "id": self.model_path,
                "object": "model",
                "created": self.model_created,
                "owned_by": "local"
            }]
        except Exception as e:
            logger.error(f"Error getting models: {str(e)}")
            return []
    
    def _create_parsers(self, chat_template_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Any], Optional[Any]]:
        """
        Create appropriate parsers based on model type and available tools.
        
        Returns:
            Tuple of (thinking_parser, tool_parser)
        """
        tools = chat_template_kwargs.get("tools", None)
        enable_thinking = chat_template_kwargs.get("enable_thinking", True)

        thinking_parser = None
        tool_parser = None
        
        if self.model_type in ["qwen3_vl", "qwen3_vl_moe"]:
            tool_parser = Qwen3ToolParser() if tools else None
        elif self.model_type == "glm4v_moe":
            thinking_parser = Glm4MoEThinkingParser() if enable_thinking else None
            tool_parser = Glm4MoEToolParser() if tools else None
            
        return thinking_parser, tool_parser
    
    async def initialize(self, queue_config: Optional[Dict[str, Any]] = None):
        """Initialize the handler and start the request queue."""
        
        if not queue_config:
            queue_config = {
                "max_concurrency": 1,
                "timeout": 300,
                "queue_size": 100
            }
        self.request_queue = RequestQueue(
            max_concurrency=queue_config.get("max_concurrency"),
            timeout=queue_config.get("timeout"),
            queue_size=queue_config.get("queue_size")
        )
        await self.request_queue.start(self._process_request)
        logger.info("Initialized MLXHandler and started request queue")

    async def generate_multimodal_stream(self, request: ChatCompletionRequest):
        """
        Generate a streaming response for multimodal chat completion requests.
        
        Args:
            request: ChatCompletionRequest object containing the messages.
        
        Returns:
            AsyncGenerator: Yields response chunks.
        """
        
        # Create a unique request ID
        request_id = f"multimodal-{uuid.uuid4()}"
        
        try:
            request_dict = await self._prepare_multimodal_request(request)
            
            # Submit to the multimodal queue and get the generator
            response_generator = await self.request_queue.submit(request_id, request_dict)      
            
            # Create appropriate parsers for this model type
            thinking_parser, tool_parser = self._create_parsers(request_dict.get("chat_template_kwargs", {}))
            
            # Process and yield each chunk asynchronously
            for chunk in response_generator:
                if not chunk or not chunk.text:
                    continue
                    
                text = chunk.text

                if thinking_parser:
                    parsed_content, is_complete = thinking_parser.parse_stream(text)
                    if parsed_content:
                        yield parsed_content
                    if is_complete:
                        thinking_parser = None
                    continue
                    
                if tool_parser:
                    parsed_content, _ = tool_parser.parse_stream(text)
                    if parsed_content:
                        yield parsed_content
                    continue

                yield text
        
        except asyncio.QueueFull:
            logger.error("Too many requests. Service is at capacity.")
            content = create_error_response("Too many requests. Service is at capacity.", "rate_limit_exceeded", HTTPStatus.TOO_MANY_REQUESTS)
            raise HTTPException(status_code=429, detail=content)

        except Exception as e:
            logger.error(f"Error in multimodal stream generation for request {request_id}: {str(e)}")
            content = create_error_response(f"Failed to generate multimodal stream: {str(e)}", "server_error", HTTPStatus.INTERNAL_SERVER_ERROR)
            raise HTTPException(status_code=500, detail=content)

    async def generate_multimodal_response(self, request: ChatCompletionRequest):
        """
        Generate a complete response for multimodal chat completion requests.
        Uses the request queue for handling concurrent requests.
        
        Args:
            request: ChatCompletionRequest object containing the messages.
        
        Returns:
            str: Complete response.
        """
        try:
            # Create a unique request ID
            request_id = f"multimodal-{uuid.uuid4()}"
            
            request_dict = await self._prepare_multimodal_request(request)
        
            response = await self.request_queue.submit(request_id, request_dict)
                        
            # Create appropriate parsers for this model type
            thinking_parser, tool_parser = self._create_parsers(request_dict.get("chat_template_kwargs", {}))
            
            if not thinking_parser and not tool_parser:
                return response.text
            
            parsed_response = {
                "reasoning_content": None,
                "tool_calls": None,
                "content": None
            }
            response_text = response.text

            if thinking_parser:
                thinking_response, response_text = thinking_parser.parse(response_text)
                parsed_response["reasoning_content"] = thinking_response
            if tool_parser:
                tool_response, response_text = tool_parser.parse(response_text)
                parsed_response["tool_calls"] = tool_response
            parsed_response["content"] = response_text
            
            return parsed_response
                        
        except asyncio.QueueFull:
            logger.error("Too many requests. Service is at capacity.")
            content = create_error_response("Too many requests. Service is at capacity.", "rate_limit_exceeded", HTTPStatus.TOO_MANY_REQUESTS)
            raise HTTPException(status_code=429, detail=content)
        except Exception as e:
            logger.error(f"Error in multimodal response generation: {str(e)}")
            content = create_error_response(f"Failed to generate multimodal response: {str(e)}", "server_error", HTTPStatus.INTERNAL_SERVER_ERROR)
            raise HTTPException(status_code=500, detail=content)
        
    async def generate_embeddings_response(self, request: EmbeddingRequest):
        """
        Generate embeddings for a given text input.
        
        Args:
            request: EmbeddingRequest object containing the text input.
        
        Returns:
            List[float]: Embeddings for the input text or images
        """
        try:
            # Create a unique request ID
            image_url = request.image_url
            # Process the image URL to get a local file path
            images = []
            if request.image_url:
                image_result = await self.image_processor.process_image_url(image_url, resize=not self.disable_auto_resize)
                images.append(image_result["path"])
            request_id = f"embeddings-{uuid.uuid4()}"
            if isinstance(request.input, str):
                request.input = [request.input]
            request_data = {
                "type": "embeddings",
                "input": request.input,
                "model": request.model,
                "images": images
            }

            # Submit to the request queue
            response = await self.request_queue.submit(request_id, request_data)

            return response

        except Exception as e:
            logger.error(f"Error in embeddings generation: {str(e)}")
            content = create_error_response(f"Failed to generate embeddings: {str(e)}", "server_error", HTTPStatus.INTERNAL_SERVER_ERROR)
            raise HTTPException(status_code=500, detail=content)


    def __del__(self):
        """Cleanup resources on deletion."""
        # Removed async cleanup from __del__; use close() instead
        pass

    async def close(self):
        """Explicitly cleanup resources asynchronously."""
        if hasattr(self, 'image_processor'):
            await self.image_processor.cleanup()
        if hasattr(self, 'audio_processor'):
            await self.audio_processor.cleanup()
        if hasattr(self, 'video_processor'):
            await self.video_processor.cleanup()

    async def cleanup(self):
        """
        Cleanup resources and stop the request queue before shutdown.
        
        This method ensures all pending requests are properly cancelled
        and resources are released, including the image processor.
        """
        try:
            logger.info("Cleaning up MLXVLMHandler resources")
            if hasattr(self, 'request_queue'):
                await self.request_queue.stop()
            if hasattr(self, 'image_processor'):
                await self.image_processor.cleanup()
            if hasattr(self, 'audio_processor'):
                await self.audio_processor.cleanup()
            if hasattr(self, 'video_processor'):
                await self.video_processor.cleanup()

            # Force garbage collection after cleanup
            gc.collect()
            logger.info("MLXVLMHandler cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error during MLXVLMHandler cleanup: {str(e)}")
            raise

    async def _process_request(self, request_data: Dict[str, Any]) -> str:
        """
        Process a multimodal request. This is the worker function for the request queue.
        
        Args:
            request_data: Dictionary containing the request data.
            
        Returns:
            str: The model's response.
        """
        try:
            
            # Extract request parameters
            images = request_data.get("images", [])
            audios = request_data.get("audios", [])
            videos = request_data.get("videos", [])
            messages = request_data.get("messages", [])
            stream = request_data.get("stream", False)
         
            # Remove these keys from model_params
            model_params = request_data.copy()
            model_params.pop("images", None)
            model_params.pop("audios", None)
            model_params.pop("videos", None)
            model_params.pop("messages", None)
            model_params.pop("stream", None)
            
            # Call the model
            response = self.model(
                images=images,
                audios=audios,
                videos=videos,
                messages=messages,
                stream=stream,
                **model_params
            )
            # Force garbage collection after model inference
            gc.collect()
            return response
            
        except Exception as e:
            logger.error(f"Error processing multimodal request: {str(e)}")
            # Clean up on error
            gc.collect()
            raise

    async def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get statistics from the request queue and performance metrics.
        
        Returns:
            Dict with queue and performance statistics.
        """
        queue_stats = self.request_queue.get_queue_stats()
        
        return {
            "queue_stats": queue_stats,
        }

    async def _reformat_multimodal_content_part(self, content_part: ChatCompletionContentPart) -> Tuple[Dict[str, Any], bool]:
        """
        Reformat a multimodal message content part into a dictionary.
        """
        if isinstance(content_part, ChatCompletionContentPartImage):
            image_url = content_part.image_url.url
            image_path = await self.image_processor.process_image_url(image_url, resize=not self.disable_auto_resize)
            return {
                "content_part": {
                    "type": "image",
                    "image": image_path
                },
                "path": image_path
            }

        if isinstance(content_part, ChatCompletionContentPartInputAudio):
            audio_url = content_part.input_audio.data
            audio_path = await self.audio_processor.process_audio_url(audio_url)
            return {
                "content_part": {
                    "type": "audio",
                    "audio": audio_path
                },
                "path": audio_path
            }

        if isinstance(content_part, ChatCompletionContentPartVideo):
            video_url = content_part.video_url.url
            video_path = await self.video_processor.process_video_url(video_url)
            return {
                "content_part": {
                    "type": "video",
                    "video": video_path,
                },
                "path": video_path
            }

        return {
            "content_part": {
                "type": "text",
                "text": content_part.text
            }
        }


    async def _prepare_multimodal_request(self, request: ChatCompletionRequest) -> Tuple[List[Dict[str, Any]], List[str], List[str], Dict[str, Any]]:
        """
        Prepare the multimodal request by processing messages with text, images, and audio.
        
        This method:
        1. Extracts text messages, image URLs, and audio data from the request
        2. Processes image URLs and audio data to get local file paths
        3. Prepares model parameters
        4. Returns processed data ready for model inference
        
        Args:
            request (ChatCompletionRequest): The incoming request containing messages and parameters.
            
        Returns:
            Tuple[List[Dict[str, Any]], List[str], List[str], Dict[str, Any]]: A tuple containing:
                - List of processed chat messages
                - List of processed image paths
                - List of processed audio paths
                - List of processed video paths
                - Dictionary of model parameters
        """
        chat_messages = []
        images = []
        audios = []
        videos = []

        try:
            # Process each message in the request
            for message in request.messages:
                # Handle system and assistant messages (simple text content)
                if message.role in ["system", "assistant"]:
                    chat_messages.append({"role": message.role, "content": message.content})
                    continue

                # Handle user messages
                if message.role == "user":
                    # Case 1: Simple string content
                    if isinstance(message.content, str):
                        chat_messages.append({"role": "user", "content": message.content})
                        continue
                        
                    # Case 2: Content is a list of dictionaries or objects
                    if isinstance(message.content, list):
                        formatted_content_parts = []

                        for content_part in message.content:
                            formatted_content_part = await self._reformat_multimodal_content_part(content_part)
                            if isinstance(content_part, ChatCompletionContentPartImage):
                                images.append(formatted_content_part["path"])
                            elif isinstance(content_part, ChatCompletionContentPartInputAudio):
                                audios.append(formatted_content_part["path"])
                            elif isinstance(content_part, ChatCompletionContentPartVideo):
                                videos.append(formatted_content_part["path"])

                            formatted_content_parts.append(formatted_content_part["content_part"])
                        chat_messages.append({"role": "user", "content": formatted_content_parts})
                    else:
                        content = create_error_response("Invalid message content format", "invalid_request_error", HTTPStatus.BAD_REQUEST)
                        raise HTTPException(status_code=400, detail=content)

            request_dict = {
                "messages": chat_messages,
                "images": images,
                "audios": audios,
                "videos": videos,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "frequency_penalty": request.frequency_penalty,
                "presence_penalty": request.presence_penalty,
                "max_tokens": request.max_tokens,
                "chat_template_kwargs": request.chat_template_kwargs.model_dump(),
                "stream": request.stream
            }

            tools = request.tools or None
            tool_choice = request.tool_choice or None

            if tools:
                if tool_choice:
                    logger.warning("Tool choice has not supported yet, will be ignored.")
                request_dict["chat_template_kwargs"]["tools"] = tools
            return request_dict

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to prepare multimodal request: {str(e)}")
            content = create_error_response(f"Failed to process request: {str(e)}", "bad_request", HTTPStatus.BAD_REQUEST)
            raise HTTPException(status_code=400, detail=content)
            
    def _validate_image_url(self, url: str) -> None:
        """
        Validate image URL format.
        
        Args:
            url: The image URL to validate
            
        Raises:
            HTTPException: If URL is invalid
        """
        if not url:
            content = create_error_response("Empty image URL provided", "invalid_request_error", HTTPStatus.BAD_REQUEST)
            raise HTTPException(status_code=400, detail=content)
            
        # Validate base64 images
        if url.startswith("data:"):
            try:
                header, encoded = url.split(",", 1)
                if not header.startswith("data:image/"):
                    raise ValueError("Invalid image format")
                base64.b64decode(encoded)
            except Exception as e:
                content = create_error_response(f"Invalid base64 image: {str(e)}", "invalid_request_error", HTTPStatus.BAD_REQUEST)
                raise HTTPException(status_code=400, detail=content)
                
    def _validate_audio_data(self, url: str) -> None:
        """
        Validate audio data URL format.
        
        Args:
            url: The audio data URL to validate
            
        Raises:
            HTTPException: If audio data is invalid
        """
        if not url:
            content = create_error_response("Empty audio data provided", "invalid_request_error", HTTPStatus.BAD_REQUEST)
            raise HTTPException(status_code=400, detail=content)
            
        # Validate base64 audio
        if url.startswith("data:"):
            try:
                header, encoded = url.split(",", 1)
                if not header.startswith("data:audio/"):
                    raise ValueError("Invalid audio format")
                base64.b64decode(encoded)
            except Exception as e:
                content = create_error_response(f"Invalid base64 audio: {str(e)}", "invalid_request_error", HTTPStatus.BAD_REQUEST)
                raise HTTPException(status_code=400, detail=content)