# neuro_simulator/services/audio.py
import asyncio
import base64
import html
import logging
import re

import azure.cognitiveservices.speech as speechsdk  # type: ignore

from ..core.config import config_manager

logger = logging.getLogger(__name__)


def _remove_emoji(text: str) -> str:
    """Removes emoji characters from a string."""
    if not text:
        return ""
    # This regex pattern covers a wide range of Unicode emoji characters.
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f700-\U0001f77f"  # alchemical symbols
        "\U0001f780-\U0001f7ff"  # Geometric Shapes Extended
        "\U0001f800-\U0001f8ff"  # Supplemental Arrows-C
        "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
        "\U0001fa00-\U0001fa6f"  # Chess Symbols
        "\U0001fa70-\U0001faff"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027b0"  # Dingbats
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text).strip()


async def synthesize_audio_segment(
    text: str, tts_provider_id: str
) -> tuple[str, float]:
    """
    Synthesizes audio using a configured TTS provider.
    Returns a Base64 encoded audio string and the audio duration in seconds.
    """
    assert config_manager.settings is not None
    # Clean emojis from the text before synthesis
    text = _remove_emoji(text)
    if not text:
        return "", 0.0

    # Find the specified TTS provider in the configuration
    provider_config = next(
        (
            p
            for p in config_manager.settings.tts_providers
            if p.provider_id == tts_provider_id
        ),
        None,
    )

    if not provider_config:
        raise ValueError(
            f"TTS Provider with ID '{tts_provider_id}' not found in configuration."
        )

    # --- Dispatch based on provider type ---
    # Currently, only Azure is supported.
    if provider_config.provider_type == "azure":
        if not provider_config.api_key or not provider_config.region:
            raise ValueError(
                f"Azure TTS provider '{provider_config.display_name}' is missing API key or region."
            )

        # Hardcoded voice and pitch as per design
        voice_name = "en-US-AshleyNeural"
        pitch = 1.25

        speech_config = speechsdk.SpeechConfig(
            subscription=provider_config.api_key, region=provider_config.region
        )
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        pitch_percent = int((pitch - 1.0) * 100)
        pitch_ssml_value = (
            f"+{pitch_percent}%" if pitch_percent >= 0 else f"{pitch_percent}%"
        )

        escaped_text = html.escape(text)

        ssml_string = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{voice_name}">
                <prosody pitch="{pitch_ssml_value}">
                    {escaped_text}
                </prosody>
            </voice>
        </speak>
        """

        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=None
        )

        def _perform_synthesis_sync():
            # This function is fully blocking, as intended for to_thread
            return synthesizer.speak_ssml_async(ssml_string).get()

        try:
            timeout_sec = provider_config.tts_timeout
            # Use asyncio.wait_for to apply a timeout to the threaded blocking call
            result = await asyncio.wait_for(
                asyncio.to_thread(_perform_synthesis_sync), timeout=timeout_sec
            )

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                encoded_audio = base64.b64encode(audio_data).decode("utf-8")
                audio_duration_sec = result.audio_duration.total_seconds()
                logger.debug(
                    f"TTS synthesis completed: '{text[:30]}...' (Duration: {audio_duration_sec:.2f}s)"
                )
                return encoded_audio, audio_duration_sec
            else:
                cancellation_details = result.cancellation_details
                error_message = f"TTS synthesis failed (Reason: {cancellation_details.reason}). Text: '{text}'"
                if cancellation_details.error_details:
                    error_message += f" | Details: {cancellation_details.error_details}"
                logger.error(error_message)
                raise Exception(error_message)
        except asyncio.TimeoutError:
            logger.error(
                f"TTS synthesis timed out after {timeout_sec} seconds for text: '{text[:30]}...'"
            )
            return "timeout", 0.0
        except Exception as e:
            logger.error(
                f"An exception occurred during the Azure TTS SDK call: {e}",
                exc_info=True,
            )
            raise
    else:
        raise NotImplementedError(
            f"TTS provider type '{provider_config.provider_type}' is not supported."
        )
