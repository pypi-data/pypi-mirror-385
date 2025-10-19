import requests
import json
import os
import aiohttp
import asyncio
from typing import List, Optional, Any
from tqdm import tqdm
from dataclasses import dataclass


__all__ = [
    'TextToSpeechRequest',
    'VoiceVoxError',
    'VoiceVoxSyncClient',
    'VoiceVoxAsyncClient',
    'VoiceVoxClient'
]


@dataclass
class TextToSpeechRequest:
    text: str
    speaker_id: int
    enable_katakana_english: bool = True
    enable_interrogative_upspeak: bool = True
    core_version: Optional[str] = None
    speed_scale: float = 1.0
    pitch_scale: float = 0.0
    intonation_scale: float = 1.0
    volume_scale: float = 1.0
    pre_phoneme_length: float = 0.1
    post_phoneme_length: float = 0.1
    pause_length: Optional[float] = None
    pause_length_scale: float = 1.0


class VoiceVoxError(Exception):
    pass


class VoiceVoxSyncClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv('VOICEVOX_API_KEY')
        self.base_url = base_url or os.getenv('VOICEVOX_URL')
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        })

    def text_to_speech(self, request: TextToSpeechRequest) -> bytes:
        query_params = {
            'text': request.text,
            'speaker': request.speaker_id,
            'enable_katakana_english': request.enable_katakana_english
        }
        if request.core_version:
            query_params['core_version'] = request.core_version

        try:
            url = f"{self.base_url}/audio_query"
            response = self.session.post(url, params=query_params, timeout=600)

            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                except json.JSONDecodeError:
                    error_detail = response.text
                raise VoiceVoxError(f"API Error {response.status_code}: {error_detail}")

            audio_query = response.json()

            audio_query['speedScale'] = request.speed_scale
            audio_query['pitchScale'] = request.pitch_scale
            audio_query['intonationScale'] = request.intonation_scale
            audio_query['volumeScale'] = request.volume_scale
            audio_query['prePhonemeLength'] = request.pre_phoneme_length
            audio_query['postPhonemeLength'] = request.post_phoneme_length
            if request.pause_length is not None:
                audio_query['pauseLength'] = request.pause_length
            audio_query['pauseLengthScale'] = request.pause_length_scale

            synth_params = {
                'speaker': request.speaker_id,
                'enable_interrogative_upspeak': request.enable_interrogative_upspeak
            }
            if request.core_version:
                synth_params['core_version'] = request.core_version

            url = f"{self.base_url}/synthesis"
            response = self.session.post(url, params=synth_params, json=audio_query, timeout=600)

            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                except json.JSONDecodeError:
                    error_detail = response.text
                raise VoiceVoxError(f"API Error {response.status_code}: {error_detail}")

            return response.content

        except requests.RequestException as e:
            raise VoiceVoxError(f"Request failed: {str(e)}")


class VoiceVoxAsyncClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv('VOICEVOX_API_KEY')
        self.base_url = base_url or os.getenv('VOICEVOX_URL')
        self._async_session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> 'VoiceVoxAsyncClient':
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        timeout = aiohttp.ClientTimeout(total=600)
        self._async_session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._async_session:
            await self._async_session.close()
            self._async_session = None

    async def text_to_speech(self, request: TextToSpeechRequest) -> bytes:
        if not self._async_session:
            raise VoiceVoxError("Async session not initialized. Use 'async with VoiceVoxAsyncClient()' context manager.")

        query_params = {
            'text': request.text,
            'speaker': str(request.speaker_id),
            'enable_katakana_english': 'true' if request.enable_katakana_english else 'false'
        }
        if request.core_version:
            query_params['core_version'] = request.core_version

        try:
            url = f"{self.base_url}/audio_query"
            async with self._async_session.post(url, params=query_params) as response:
                if response.status >= 400:
                    try:
                        error_detail = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        error_detail = await response.text()
                    raise VoiceVoxError(f"API Error {response.status}: {error_detail}")

                audio_query = await response.json()

            audio_query['speedScale'] = request.speed_scale
            audio_query['pitchScale'] = request.pitch_scale
            audio_query['intonationScale'] = request.intonation_scale
            audio_query['volumeScale'] = request.volume_scale
            audio_query['prePhonemeLength'] = request.pre_phoneme_length
            audio_query['postPhonemeLength'] = request.post_phoneme_length
            if request.pause_length is not None:
                audio_query['pauseLength'] = request.pause_length
            audio_query['pauseLengthScale'] = request.pause_length_scale

            synth_params = {
                'speaker': str(request.speaker_id),
                'enable_interrogative_upspeak': 'true' if request.enable_interrogative_upspeak else 'false'
            }
            if request.core_version:
                synth_params['core_version'] = request.core_version

            url = f"{self.base_url}/synthesis"
            async with self._async_session.post(url, params=synth_params, json=audio_query) as response:
                if response.status >= 400:
                    try:
                        error_detail = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        error_detail = await response.text()
                    raise VoiceVoxError(f"API Error {response.status}: {error_detail}")

                return await response.read()

        except aiohttp.ClientError as e:
            raise VoiceVoxError(f"Request failed: {str(e)}")

    async def _create_audio_query(self, request: TextToSpeechRequest) -> dict:
        if not self._async_session:
            raise VoiceVoxError("Async session not initialized. Use 'async with VoiceVoxAsyncClient()' context manager.")

        query_params = {
            'text': request.text,
            'speaker': str(request.speaker_id),
            'enable_katakana_english': 'true' if request.enable_katakana_english else 'false'
        }
        if request.core_version:
            query_params['core_version'] = request.core_version

        try:
            url = f"{self.base_url}/audio_query"
            async with self._async_session.post(url, params=query_params) as response:
                if response.status >= 400:
                    try:
                        error_detail = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        error_detail = await response.text()
                    raise VoiceVoxError(f"API Error {response.status}: {error_detail}")

                audio_query = await response.json()

            audio_query['speedScale'] = request.speed_scale
            audio_query['pitchScale'] = request.pitch_scale
            audio_query['intonationScale'] = request.intonation_scale
            audio_query['volumeScale'] = request.volume_scale
            audio_query['prePhonemeLength'] = request.pre_phoneme_length
            audio_query['postPhonemeLength'] = request.post_phoneme_length
            if request.pause_length is not None:
                audio_query['pauseLength'] = request.pause_length
            audio_query['pauseLengthScale'] = request.pause_length_scale

            return audio_query

        except aiohttp.ClientError as e:
            raise VoiceVoxError(f"Request failed: {str(e)}")

    async def _synthesize_audio(self, audio_query: dict, request: TextToSpeechRequest) -> bytes:
        if not self._async_session:
            raise VoiceVoxError("Async session not initialized. Use 'async with VoiceVoxAsyncClient()' context manager.")

        synth_params = {
            'speaker': str(request.speaker_id),
            'enable_interrogative_upspeak': 'true' if request.enable_interrogative_upspeak else 'false'
        }
        if request.core_version:
            synth_params['core_version'] = request.core_version

        try:
            url = f"{self.base_url}/synthesis"
            async with self._async_session.post(url, params=synth_params, json=audio_query) as response:
                if response.status >= 400:
                    try:
                        error_detail = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        error_detail = await response.text()
                    raise VoiceVoxError(f"API Error {response.status}: {error_detail}")

                return await response.read()

        except aiohttp.ClientError as e:
            raise VoiceVoxError(f"Request failed: {str(e)}")

    async def concurrent_text_to_speech(self, requests: List[TextToSpeechRequest], progress: bool = False) -> List[bytes]:
        if not requests:
            return []

        progress_bar = None
        if progress:
            progress_bar = tqdm(total=len(requests) * 2, desc="Processing", unit="step")

        audio_queries = []
        for request in requests:
            query = await self._create_audio_query(request)
            audio_queries.append(query)
            if progress_bar:
                progress_bar.update(1)

        synthesis_coroutines = [
            self._synthesize_audio(audio_query, request)
            for audio_query, request in zip(audio_queries, requests)
        ]

        if progress_bar:
            async def track_progress(coro):
                result = await coro
                progress_bar.update(1)
                return result

            tracked_coroutines = [track_progress(coro) for coro in synthesis_coroutines]
            results = await asyncio.gather(*tracked_coroutines)
        else:
            results = await asyncio.gather(*synthesis_coroutines)

        if progress_bar:
            progress_bar.close()

        return results

    def concurrent_text_to_speech_sync(self, requests: List[TextToSpeechRequest], progress: bool = False) -> List[bytes]:
        async def _run():
            async with self.__class__(api_key=self.api_key, base_url=self.base_url) as client:
                return await client.concurrent_text_to_speech(requests, progress=progress)

        return asyncio.run(_run())


VoiceVoxClient = VoiceVoxSyncClient