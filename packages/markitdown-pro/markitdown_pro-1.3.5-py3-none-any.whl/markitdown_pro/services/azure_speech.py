from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import azure.cognitiveservices.speech as speechsdk

from ..common.logger import logger
from ..common.utils import detect_extension


def _format_ts_hrs_mins_secs(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _ticks_to_seconds(ticks: int) -> float:
    return ticks / 10_000_000.0


@dataclass
class TranscriptionResult:
    text: str
    detected_language: Optional[str] = None
    segments: Optional[List[Tuple[float, str]]] = None


class AzureSpeechService:
    """Transcribes audio files to Markdown using Azure Speech with optional quick language sniff."""

    SUPPORTED_EXTENSIONS = frozenset(
        {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".wma", ".webm", ".opus"}
    )
    _COMPRESSED_CONTAINER_MAP = {
        ".mp3": speechsdk.AudioStreamContainerFormat.MP3,
        ".flac": speechsdk.AudioStreamContainerFormat.FLAC,
        ".opus": speechsdk.AudioStreamContainerFormat.OGG_OPUS,
        ".ogg": speechsdk.AudioStreamContainerFormat.OGG_OPUS,
    }

    def __init__(
        self,
        *,
        enable_language_sniff: bool = True,
        sniff_seconds: int = 25,
        candidate_languages: Optional[List[str]] = None,
    ) -> None:
        key = os.getenv("AZURE_SPEECH_KEY", "")
        region = os.getenv("AZURE_SPEECH_REGION", "")
        if not key or not region:
            logger.error("AzureSpeechService: missing AZURE_SPEECH_KEY or AZURE_SPEECH_REGION.")
            self._configured = False
            return
        use_v2_raw = os.getenv("AZURE_SPEECH_USE_V2", "1")
        self._use_v2_default = str(use_v2_raw).strip().lower() in {"1", "true", "yes", "on"}
        self._key, self._region = key, region
        self._endpoint_v2 = f"wss://{region}.stt.speech.microsoft.com/speech/universal/v2"
        self.enable_language_sniff = enable_language_sniff
        self.sniff_seconds = max(5, int(sniff_seconds))
        # Top 10 worldwide-ish locales (tune for your org/tenants)
        self.candidate_languages = candidate_languages or [
            "en-US",
            "es-ES",
            "pt-BR",
            "fr-FR",
            "de-DE",
            "it-IT",
            "ja-JP",
            "ko-KR",
            "zh-CN",
            "ar-EG",
        ]
        try:
            # Base config (not used directly for runs; we build per-run configs)
            if self._use_v2_default:
                self._speech_config = speechsdk.SpeechConfig(
                    endpoint=self._endpoint_v2, subscription=self._key
                )
            else:
                self._speech_config = speechsdk.SpeechConfig(
                    subscription=self._key, region=self._region
                )
            self._configured = True
        except Exception as e:
            logger.error(f"AzureSpeechService: failed to create SpeechConfig: {e}")
            self._speech_config = None
            self._configured = False

    async def convert_to_md(
        self,
        file_path: str | Path,
        *,
        languages: Optional[List[str]] = None,
        include_timestamps: bool = False,
        timeout_s: float = 900.0,
        min_chars: int = 6,
    ) -> Optional[str]:
        if not self._configured:
            logger.error("AzureSpeechService: service not configured.")
            return None
        file_path = Path(file_path)
        ext = (detect_extension(str(file_path)) or file_path.suffix).lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            logger.warning(f"AzureSpeechService: Unsupported file format: {ext}")
            return None
        # Decide language strategy
        final_languages: Optional[List[str]] = languages
        detected_lang: Optional[str] = None
        if final_languages is None and self.enable_language_sniff:
            try:
                detected_lang = await asyncio.wait_for(
                    asyncio.to_thread(self._detect_language_quick, file_path),
                    timeout=min(timeout_s, 60.0),
                )
                if detected_lang:
                    final_languages = [detected_lang]
            except Exception as e:
                logger.debug(f"AzureSpeechService: quick language sniff failed: {e}")
        try:
            result: TranscriptionResult = await asyncio.wait_for(
                asyncio.to_thread(self._transcribe_sync, file_path, final_languages, detected_lang),
                timeout=timeout_s,
            )
        except asyncio.TimeoutError:
            logger.error(f"AzureSpeechService: timed out after {timeout_s}s for {file_path.name}")
            return None
        except Exception as e:
            logger.error(f"AzureSpeechService: transcription failed for '{file_path.name}': {e}")
            return None
        text = (result.text or "").strip()
        if len(text) < min_chars:
            logger.info("AzureSpeechService: transcription produced insufficient content.")
            return None
        lines: List[str] = [f"# Transcript: {file_path.name}"]
        if result.detected_language:
            lines.append(f"*Detected language:* `{result.detected_language}`")
        lines.append("")
        if include_timestamps and result.segments:
            for start_sec, seg_text in result.segments:
                lines.append(f"- **{_format_ts_hrs_mins_secs(start_sec)}** {seg_text}")
        else:
            lines.append(text)
        return "\n".join(lines)

    # -------------------- internal --------------------
    def _build_speech_config_for_run(self, languages: Optional[List[str]]) -> tuple[
        speechsdk.SpeechConfig,
        Optional[speechsdk.languageconfig.AutoDetectSourceLanguageConfig],
        bool,
    ]:
        need_continuous = bool(languages and len(languages) > 1)
        use_v2 = self._use_v2_default or need_continuous
        cfg = (
            speechsdk.SpeechConfig(endpoint=self._endpoint_v2, subscription=self._key)
            if use_v2
            else speechsdk.SpeechConfig(subscription=self._key, region=self._region)
        )
        auto_lang_cfg = None
        if languages:
            if len(languages) == 1:
                cfg.speech_recognition_language = languages[0]
                cfg.set_property(
                    speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, "AtStart"
                )
            else:
                cfg.set_property(
                    speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, "Continuous"
                )
                try:
                    auto_lang_cfg = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                        languages=languages
                    )
                except Exception as e:
                    logger.warning(f"AzureSpeechService: invalid languages {languages}: {e}")
        else:
            cfg.set_property(speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, "AtStart")
        return cfg, auto_lang_cfg, need_continuous

    def _detect_language_quick(self, path: Path) -> Optional[str]:
        """Sniff language from the first N seconds using Continuous LID across up to 10 candidates."""
        if not self._configured:
            return None
        # Build v2 + Continuous LID with candidate_languages
        cfg = speechsdk.SpeechConfig(endpoint=self._endpoint_v2, subscription=self._key)
        cfg.set_property(speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, "Continuous")
        try:
            auto_cfg = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                languages=self.candidate_languages[:10]
            )
        except Exception as e:
            logger.debug(f"AzureSpeechService: AutoDetect config failed: {e}")
            return None
        # Make a short preview WAV and run RecognizeOnce on it
        preview = self._make_preview_wav(path, self.sniff_seconds)
        if not preview:
            return None
        try:
            audio = speechsdk.AudioConfig(filename=str(preview))
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=cfg, audio_config=audio, auto_detect_source_language_config=auto_cfg
            )
            res = recognizer.recognize_once_async().get()
            if res and res.reason == speechsdk.ResultReason.RecognizedSpeech:
                try:
                    auto = speechsdk.AutoDetectSourceLanguageResult(res)
                    lang = getattr(auto, "language", None)
                    if lang:
                        logger.info(f"AzureSpeechService: quick language sniff → {lang}")
                        return lang
                except Exception:
                    pass
            return None
        except Exception as e:
            logger.debug(f"AzureSpeechService: quick sniff recognize failed: {e}")
            return None
        finally:
            try:
                preview.unlink(missing_ok=True)
            except Exception:
                pass

    def _transcribe_sync(
        self, path: Path, languages: Optional[List[str]], sniff_lang: Optional[str]
    ) -> TranscriptionResult:
        # If sniff failed and no languages provided, use Continuous LID across the candidate list for the full run.
        run_languages = (
            languages
            if languages
            else (self.candidate_languages[:10] if self.enable_language_sniff else None)
        )
        speech_config, auto_lang_cfg, _ = self._build_speech_config_for_run(run_languages)
        # Strategy 1: direct file
        try:
            audio_config = speechsdk.AudioConfig(filename=str(path))
            return self._run_recognition(speech_config, audio_config, auto_lang_cfg)
        except Exception as e:
            logger.debug(f"AzureSpeechService: direct file recognition failed: {e}")
        # Strategy 2: compressed push (requires GStreamer)
        ext = path.suffix.lower()
        if ext in self._COMPRESSED_CONTAINER_MAP and self._has_gstreamer():
            try:
                container = self._COMPRESSED_CONTAINER_MAP[ext]
                stream_format = speechsdk.audio.AudioStreamFormat(
                    compressed_stream_format=container
                )
                push_stream = speechsdk.audio.PushAudioInputStream(stream_format=stream_format)
                audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
                stop_event = threading.Event()

                def _feeder():
                    try:
                        with open(path, "rb") as f:
                            while not stop_event.is_set():
                                data = f.read(4096)
                                if not data:
                                    break
                                push_stream.write(data)
                    finally:
                        try:
                            push_stream.close()
                        except Exception:
                            pass

                feeder_thread = threading.Thread(
                    target=_feeder, name="azure_audio_feeder", daemon=True
                )

                def _stop_feeder():
                    stop_event.set()

                return self._run_recognition(
                    speech_config,
                    audio_config,
                    auto_lang_cfg,
                    start_feeder=feeder_thread.start,
                    stop_feeder=_stop_feeder,
                )
            except Exception as e:
                logger.debug(f"AzureSpeechService: compressed stream path failed: {e}")
        elif ext in self._COMPRESSED_CONTAINER_MAP:
            logger.debug(
                "AzureSpeechService: skipping compressed stream (GStreamer not found); using WAV fallback."
            )
        # Strategy 3: ffmpeg→WAV fallback
        if self._has_ffmpeg():
            logger.info("AzureSpeechService: using ffmpeg → WAV fallback for robust decoding.")
            wav_path = self._transcode_to_wav(path)
            if wav_path:
                try:
                    audio_config = speechsdk.AudioConfig(filename=str(wav_path))
                    return self._run_recognition(speech_config, audio_config, auto_lang_cfg)
                finally:
                    try:
                        wav_path.unlink(missing_ok=True)
                    except Exception:
                        pass
        raise RuntimeError("All audio input strategies failed.")

    def _run_recognition(
        self,
        speech_config: speechsdk.SpeechConfig,
        audio_config: speechsdk.AudioConfig,
        auto_lang_cfg: Optional[speechsdk.languageconfig.AutoDetectSourceLanguageConfig] = None,
        *,
        start_feeder: Optional[Callable[[], None]] = None,
        stop_feeder: Optional[Callable[[], None]] = None,
    ) -> TranscriptionResult:
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config,
            auto_detect_source_language_config=auto_lang_cfg,
        )
        detected_language: Optional[str] = None
        segments: List[Tuple[float, str]] = []
        full_text_parts: List[str] = []
        done = threading.Event()
        stopped_by_session = False

        def _on_recognized(evt: speechsdk.SpeechRecognitionEventArgs):  # type: ignore[override]
            nonlocal detected_language
            res = getattr(evt, "result", None)
            if not res:
                return
            if res.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = (res.text or "").strip()
                if not text:
                    return
                try:
                    auto = speechsdk.AutoDetectSourceLanguageResult(res)
                    if getattr(auto, "language", None):
                        detected_language = auto.language
                except Exception:
                    pass
                start_sec = _ticks_to_seconds(getattr(res, "offset", 0))
                segments.append((start_sec, text))
                full_text_parts.append(text)

        def _on_canceled(evt: speechsdk.SpeechRecognitionCanceledEventArgs):
            reason = getattr(evt, "reason", None)
            details = getattr(evt, "error_details", None)
            reason_name = None
            try:
                if isinstance(reason, speechsdk.CancellationReason):
                    reason_name = reason.name
                elif reason is not None:
                    reason_name = speechsdk.CancellationReason(reason).name
            except Exception:
                reason_name = str(reason)
            if reason_name in ("EndOfStream", "NoError") and not details:
                logger.debug(f"AzureSpeechService: recognition canceled (benign): {reason_name}")
            else:
                logger.warning(
                    f"AzureSpeechService: recognition canceled: {reason_name} ({details})"
                )
            done.set()

        def _on_session_stopped(_):
            nonlocal stopped_by_session
            stopped_by_session = True
            done.set()

        recognizer.recognized.connect(_on_recognized)  # type: ignore[attr-defined]
        recognizer.canceled.connect(_on_canceled)  # type: ignore[attr-defined]
        recognizer.session_stopped.connect(_on_session_stopped)  # type: ignore[attr-defined]
        try:
            recognizer.start_continuous_recognition_async().get()
            if start_feeder:
                start_feeder()
            done.wait()
            if not stopped_by_session:
                try:
                    recognizer.stop_continuous_recognition_async().get()
                except Exception:
                    pass
        finally:
            try:
                if stop_feeder:
                    stop_feeder()
            except Exception:
                pass
            try:
                recognizer.session_stopped.disconnect(_on_session_stopped)  # type: ignore[attr-defined]
                recognizer.canceled.disconnect(_on_canceled)  # type: ignore[attr-defined]
                recognizer.recognized.disconnect(_on_recognized)  # type: ignore[attr-defined]
            except Exception:
                pass
        text = " ".join(full_text_parts).strip()
        return TranscriptionResult(
            text=text, detected_language=detected_language, segments=segments
        )

    # -------------------- utilities --------------------
    @staticmethod
    def _has_ffmpeg() -> bool:
        return shutil.which("ffmpeg") is not None

    @staticmethod
    def _has_gstreamer() -> bool:
        if shutil.which("gst-launch-1.0"):
            return True
        for var in ("GSTREAMER_1_0_ROOT_X86_64", "GSTREAMER_1_0_ROOT_X86"):
            val = os.getenv(var)
            if val and Path(val).exists():
                return True
        return False

    @staticmethod
    def _transcode_to_wav(src: Path) -> Optional[Path]:
        if shutil.which("ffmpeg") is None:
            return None
        tmp_dir = Path(tempfile.gettempdir())
        out = tmp_dir / f"azspx_{src.stem}_16k_mono.wav"
        try:
            cmd = [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(src),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-acodec",
                "pcm_s16le",
                str(out),
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            return out
        except Exception as e:
            logger.error(f"AzureSpeechService: ffmpeg transcode failed: {e}")
            return None

    @staticmethod
    def _make_preview_wav(src: Path, seconds: int) -> Optional[Path]:
        """Extract the first N seconds to WAV for quick language sniff."""
        if shutil.which("ffmpeg") is None:
            return None
        tmp_dir = Path(tempfile.gettempdir())
        out = tmp_dir / f"azspx_preview_{src.stem}_{seconds}s.wav"
        try:
            cmd = [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(src),
                "-t",
                str(int(seconds)),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-acodec",
                "pcm_s16le",
                str(out),
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            return out
        except Exception as e:
            logger.debug(f"AzureSpeechService: ffmpeg preview failed: {e}")
            return None
