
"""
Voice filtering utilities for SpeakUB TTS voices.
"""

from typing import Dict, List, Any, Optional


def filter_female_chinese_voices(
    voices: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter voices to include only female Chinese voices (zh-CN or zh-TW locale).

    Args:
        voices: List of voice dictionaries from TTS providers

    Returns:
        Filtered list of female Chinese voices
    """
    return [
        voice
        for voice in voices
        if voice.get("gender", "").lower() == "female"
        and voice.get("locale", "").startswith(("zh-CN", "zh-TW"))
    ]


def filter_voices_by_criteria(
    voices: List[Dict[str, Any]],
    gender: Optional[str] = None,
    locale_prefix: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter voices by specified criteria.

    Args:
        voices: List of voice dictionaries from TTS providers
        gender: Filter by gender (case-insensitive), None to skip
        locale_prefix: Filter by locale prefix (e.g., "zh-CN"), None to skip

    Returns:
        Filtered list of voices matching criteria
    """
    filtered_voices = voices

    if gender:
        filtered_voices = [
            voice for voice in filtered_voices
            if voice.get("gender", "").lower() == gender.lower()
        ]

    if locale_prefix:
        filtered_voices = [
            voice for voice in filtered_voices
            if voice.get("locale", "").startswith(locale_prefix)
        ]

    return filtered_voices
