"""
A minimal set of utilities used by KodeAgent.
This module will be copied along with code for CodeAgent, so keep it minimum.
"""
import base64
import logging
import mimetypes
import os
from typing import Optional, Any, Type

import litellm
import pydantic as pyd
import requests
from tenacity import wait_random_exponential, AsyncRetrying, stop_after_attempt

# Get a logger for the current module
logger = logging.getLogger('KodeAgent')
logger.setLevel(logging.WARNING)

# Configure logging format
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def is_it_url(path: str) -> bool:
    """
    Check whether a given path is a URL.

    Args:
        path: The path.

    Returns:
        `True` if it's a URL; `False` otherwise.
    """
    return path.startswith(('http://', 'https://'))


def detect_file_type(url: str) -> str:
    """
    Identify the content/MIME type of file pointed by a URL.

    Args:
        url: The URL to the file.

    Returns:
        The detected MIME type or `Unknown file type`.
    """
    try:
        # Step 1: Try HEAD request to get Content-Disposition
        response = requests.head(url, allow_redirects=True, timeout=15)
        content_disposition = response.headers.get('Content-Disposition')

        if content_disposition and 'filename=' in content_disposition:
            file_name = content_disposition.split('filename=')[1].strip()
            file_extension = file_name.split('.')[-1]
            return file_extension  # If this works, return immediately

        # Step 2: If HEAD didn't give useful info, send GET request for more details
        response = requests.get(url, stream=True, timeout=20)
        content_type = response.headers.get('Content-Type')

        if content_type and content_type != 'application/json':  # Avoid false positives
            return content_type

        return 'Unknown file type'
    except requests.RequestException as e:
        logger.error('Error detecting file type: %s', str(e))
        return 'Unknown file type'


def is_image_file(file_type) -> bool:
    """
    Identify whether a given MIME type is an image.

    Args:
        file_type: The file/content type.

    Returns:
        `True` if an image file; `False` otherwise.
    """
    return file_type.startswith('image/')


async def call_llm(
        model_name: str,
        litellm_params: dict,
        messages: list[dict],
        response_format: Optional[Type[pyd.BaseModel]] = None,
        trace_id: Optional[str] = None,
) -> str | None:
    """
    Invoke the LLM to generate a response based on a given list of messages.

    Args:
        model_name: The name of the LLM to be used.
        litellm_params: Optional parameters for LiteLLM.
        messages: A list of messages (and optional images) to be sent to the LLM.
        response_format: Optional type of message the LLM should respond with.
        trace_id: (Optional) Langfuse trace ID.

    Returns:
        The LLM response as string.

    Raises:
        ValueError: If the LLM returns an empty or invalid response body.
    """
    params = {'model': model_name, 'messages': messages}

    if response_format:
        params['response_format'] = response_format

    # Add a timeout to prevent indefinite hangs
    if 'timeout' not in litellm_params:
        params['timeout'] = 30  # seconds

    params.update(litellm_params)

    try:
        # Use AsyncRetrying to handle retries in a non-blocking way
        async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_random_exponential(multiplier=1, max=10)
        ):
            with attempt:
                # Use the asynchronous litellm call
                response = await litellm.acompletion(
                    **params, metadata={'trace_id': str(trace_id)}
                )

                # Check for empty content
                response_content = response.choices[0].message.content
                if not response_content or not response_content.strip():
                    raise ValueError('LLM returned an empty or invalid response body.')

                token_usage = {
                    'cost': response._hidden_params.get('response_cost'),
                    'prompt_tokens': response.usage.get('prompt_tokens'),
                    'completion_tokens': response.usage.get('completion_tokens'),
                    'total_tokens': response.usage.get('total_tokens'),
                }
                logger.info(token_usage)
                return response_content

    except Exception as e:
        logger.exception(
            'LLM call failed after repeated attempts: %s',
            str(e), exc_info=True
        )
        print('\n\ncall_llm MESSAGES:\n', '\n'.join([str(msg) for msg in messages]), '\n\n')
        raise ValueError(
            'Failed to get a valid response from LLM after multiple retries.'
        ) from e


def make_user_message(
        text_content: str,
        files: Optional[list[str]] = None
) -> list[dict[str, Any]]:
    """
    Create a single user message to be sent to LiteLLM.

    Args:
        text_content: The text content of the message.
        files: An optional list of file paths or URLs, which can include images
               or other file types.

    Returns:
        A list of dict items representing the messages.
    """
    content: list[dict[str, Any]] = [{'type': 'text', 'text': str(text_content)}]
    message: list[dict[str, Any]] = [{'role': 'user'}]

    if files:
        for item in files:
            is_image = False
            if is_it_url(item):
                if any(
                        ext in item.lower() for ext in [
                            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'
                        ]
                ) or is_image_file(detect_file_type(item)):
                    is_image = True
            elif os.path.isfile(item):
                try:
                    mime_type, _ = mimetypes.guess_type(item)
                    if mime_type and 'image' in mime_type:
                        is_image = True
                except Exception:
                    logger.error(
                        'Error guessing MIME type for local file %s...will ignore it',
                        item,
                        exc_info=True
                    )
                    # If an error occurs, treat it as not an image to continue processing
                    is_image = False

            if is_image:
                if is_it_url(item):
                    content.append({'type': 'image_url', 'image_url': {'url': item}})
                elif os.path.isfile(item):
                    try:
                        with open(item, 'rb') as img_file:
                            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

                        try:
                            mime_type, _ = mimetypes.guess_type(item)
                        except Exception:
                            logger.warning(
                                'Could not guess MIME type, defaulting to octet-stream',
                                exc_info=True
                            )
                            mime_type = 'application/octet-stream'

                        mime_type = mime_type if mime_type else 'application/octet-stream'
                        content.append({
                            'type': 'image_url',
                            'image_url': {'url': f'data:{mime_type};base64,{encoded_image}'}
                        })
                    except FileNotFoundError:
                        logger.error('Image file not found: %s...will ignore it', item)
                    except Exception as e:
                        logger.error(
                            'Error processing local image %s: %s...will ignore it',
                            item, e
                        )
                else:
                    logger.error('Invalid image file path or URL: %s...will ignore it', item)
            else:  # Handle as a general file or URL (not an image)
                if is_it_url(item):
                    content.append({'type': 'text', 'text': f'File URL: {item}'})
                elif os.path.isfile(item):
                    try:
                        mime_type, _ = mimetypes.guess_type(item)
                        if mime_type and (
                                'text' in mime_type
                                or mime_type in ('application/json', 'application/xml')
                        ):
                            try:
                                with open(item, 'r', encoding='utf-8') as f:
                                    file_content = f.read()
                                content.append(
                                    {
                                        'type': 'text',
                                        'text': f'File {item} content:\n{file_content}'
                                    }
                                )
                            except Exception:
                                logger.error(
                                    'Error reading text file `%s`...will fallback to path only'
                                    , item
                                )
                                content.append({'type': 'text', 'text': f'Input file: {item}'})
                        else:
                            # Non-text or unknown types: include only the path reference
                            content.append({'type': 'text', 'text': f'Input file: {item}'})
                    except Exception:
                        logger.error(
                            'Error guessing MIME type for local file %s...will ignore it',
                            item,
                            exc_info=True
                        )
                        # content.append({'type': 'text', 'text': f'Input file: {item}'})
                else:
                    logger.error('Invalid file path or URL: %s...will ignore it', item)

    message[0]['content'] = content
    return message


def combine_user_messages(messages: list) -> list:
    """
    Combines consecutive user messages into a single message with a list of content items.

    Returns:
        A new list of messages with combined user messages.
    """
    combined = []
    for msg in messages:
        if msg.get('role') == 'user':
            if combined and combined[-1].get('role') == 'user':
                # Merge content lists
                prev_content = combined[-1]['content']
                curr_content = msg.get('content', [])
                if not isinstance(prev_content, list):
                    prev_content = [prev_content]
                if not isinstance(curr_content, list):
                    curr_content = [curr_content]
                combined[-1]['content'] = prev_content + curr_content
            else:
                # Ensure content is a list
                content = msg.get('content', [])
                if not isinstance(content, list):
                    content = [content]
                combined.append({'role': 'user', 'content': content})
        else:
            combined.append(msg)
    return combined
