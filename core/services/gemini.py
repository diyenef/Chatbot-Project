"""Gemini service adapter.

This module provides a single function `call_gemini(prompt)` which will make a
POST request to the configured Gemini-like API endpoint and return a plain text
response. The implementation is intentionally forgiving about the exact JSON
shape of the response so it can be adapted to the real Gemini API format.

Security: the API key is read from Django settings (`GEMINI_API_KEY`) which in
turn should come from an environment variable in production. Do NOT store API
keys in source control.
"""
from typing import Any, Dict
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def _extract_text_from_response(resp_json: Dict[str, Any]) -> str:
    """Try several common response shapes and return a best-effort text reply.

    Supports formats like:
      - {"reply": "..."}
      - {"output": "..."}
      - {"text": "..."}
      - {"choices": [{"text": "..."}, ...]}
      - {"result": {"content": "..."}}
    """
    if not isinstance(resp_json, dict):
        return str(resp_json)

    # Common top-level keys
    for key in ('reply', 'output', 'text'):
        if key in resp_json and isinstance(resp_json[key], str):
            return resp_json[key]

    # OpenAI-like choices
    choices = resp_json.get('choices')
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            for k in ('text', 'message', 'content'):
                if k in first and isinstance(first[k], str):
                    return first[k]

    # nested result.content
    result = resp_json.get('result')
    if isinstance(result, dict) and isinstance(result.get('content'), str):
        return result.get('content')

    # Fallback: stringify response
    return str(resp_json)


def call_gemini(prompt: str, timeout: float = 10.0) -> str:
    """Call the configured Gemini API and return a text reply.

    Raises RuntimeError for configuration errors or for unexpected HTTP problems.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    api_url = getattr(settings, 'GEMINI_API_URL', '')

    if not api_key:
        raise RuntimeError('Gemini API key is not configured. Set GEMINI_API_KEY in the environment.')
    if not api_url:
        raise RuntimeError('Gemini API URL is not configured. Set GEMINI_API_URL in settings.')

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    payload = {
        'prompt': prompt,
        # optional: allow server-side defaults for model params
        'max_tokens': getattr(settings, 'GEMINI_MAX_TOKENS', 512),
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        logger.exception('Network error when calling Gemini API')
        raise RuntimeError('Network error when calling Gemini API') from e

    if resp.status_code >= 400:
        logger.error('Gemini API returned HTTP %s: %s', resp.status_code, resp.text[:200])
        raise RuntimeError(f'Gemini API returned HTTP {resp.status_code}')

    try:
        data = resp.json()
    except ValueError:
        # Non-JSON response — return raw text
        return resp.text

    return _extract_text_from_response(data)

