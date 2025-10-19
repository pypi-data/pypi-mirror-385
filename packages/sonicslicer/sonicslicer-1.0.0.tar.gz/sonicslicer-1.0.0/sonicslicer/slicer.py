from pathlib import Path
from typing import Union, Optional, Tuple, List
from pydub import AudioSegment
from pydub.utils import make_chunks
from .slicer_exceptions import SlicerException
from .formarts import AudioFormarts
from .utils.log.loger import get_logger

logger = get_logger()


class AudioProcessor:
    """
    A class for splitting and trimming audio files with various optimization options.
    Supports multiple audio formats through pydub.
    """

    def __init__(self, output_format: str = "wav", bitrate: str = "192k"):
        """
        Initialize the AudioProcessor.

        Args:
            output_format (str): Output audio format (wav, mp3, etc.)
            bitrate (str): Bitrate for compressed formats
        """
        self.output_format = output_format.lower()
        self.bitrate = bitrate
        self.supported_formats = AudioFormarts().surpoted

        if self.output_format not in self.supported_formats:
            raise SlicerException(
                f"Unsupported format: {output_format}. Supported: {self.supported_formats}"
            )

    def _validate_file(self, file_path: Union[str, Path]) -> Path:
        """Validate and return Path object for the input file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise SlicerException(f"File not found: {file_path}")
        if not file_path.is_file():
            raise SlicerException(f"Path is not a file: {file_path}")
        return file_path

    def _get_output_path(
        self, input_path: Path, suffix: str, index: Optional[int] = None
    ) -> Path:
        """Generate output file path with proper naming."""
        stem = input_path.stem
        ext = f".{self.output_format}"

        if index is not None:
            filename = f"{stem}-part-{index:03d}{ext}"
        else:
            filename = f"{stem}{suffix}{ext}"

        return input_path.parent / filename

    def _load_audio(self, file_path: Path) -> AudioSegment:
        """Load audio file with optimized settings."""
        try:
            return AudioSegment.from_file(str(file_path))
        except Exception as e:
            raise SlicerException(f"Failed to load audio file: {e}")

    def _save_audio(self, audio: AudioSegment, output_path: Path) -> None:
        """Save audio with optimized settings."""
        try:
            output_path.absolute().parent.mkdir(parents=True, exist_ok=True)
            if self.output_format == "wav":
                audio.export(str(output_path), format=self.output_format)
            else:
                audio.export(
                    str(output_path), format=self.output_format, bitrate=self.bitrate
                )
        except Exception as e:
            raise SlicerException(f"Failed to save audio file: {e}")

    def split_by_time(
        self,
        file_path: Union[str, Path],
        chunk_duration_ms: int,
        sections: str = "max",
        strict: bool = False,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> List[Path]:
        """
        Split audio file by time duration.

        Args:
            file_path: Path to audio file
            chunk_duration_ms: Duration of each chunk in milliseconds
            sections: "max" for maximum chunks or "1" for single split
            strict: If True, discard last chunk if smaller than specified duration
            output_dir: Optional directory for output files

        Returns:
            List of paths to created audio chunks
        """
        file_path = self._validate_file(file_path)
        audio = self._load_audio(file_path)

        if chunk_duration_ms <= 0:
            raise SlicerException("Chunk duration must be positive")

        total_duration = len(audio)

        if sections == 1:
            # Single split at specified time
            if chunk_duration_ms >= total_duration:
                raise SlicerException(
                    f"Split time {chunk_duration_ms} exceeds audio duration {total_duration}"
                )

            chunk1 = audio[:chunk_duration_ms]
            chunk2 = audio[chunk_duration_ms:]

            output_paths = [
                self._get_output_path(file_path, "-part-1", 1),
                self._get_output_path(file_path, "-part-2", 2),
            ]

            if output_dir:
                output_paths = [Path(output_dir) / path.name for path in output_paths]

            self._save_audio(chunk1, output_paths[0])
            self._save_audio(chunk2, output_paths[1])

            return output_paths

        else:  # sections == "max"
            # Create maximum chunks of specified duration
            chunks = make_chunks(audio, chunk_duration_ms)

            if strict and chunks and len(chunks[-1]) < chunk_duration_ms:
                chunks = chunks[:-1]  # Remove last chunk if too small

            if not chunks:
                try:
                    raise SlicerException(
                        "No chunks created - check duration parameters"
                    )
                except SlicerException as e:
                    logger.warn(e)

            _sections = 0 if sections == "max" else int(sections)

            chunks = chunks[:_sections] if _sections != 0 else chunks

            output_paths = []
            for i, chunk in enumerate(chunks, 1):
                output_path = self._get_output_path(file_path, "", i)
                if output_dir:
                    output_path = Path(output_dir) / output_path.name
                self._save_audio(chunk, output_path)
                output_paths.append(output_path)

            return output_paths

    def split_by_size(
        self,
        file_path: Union[str, Path],
        max_size_bytes: int,
        sections: str = "max",
        strict: bool = False,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> List[Path]:
        """
        Split audio file by approximate file size.

        Args:
            file_path: Path to audio file
            max_size_bytes: Maximum size of each chunk in bytes
            strict: If True, discard last chunk if smaller than specified size
            output_dir: Optional directory for output files

        Returns:
            List of paths to created audio chunks
        """
        file_path = self._validate_file(file_path)
        audio = self._load_audio(file_path)

        if max_size_bytes <= 0:
            raise SlicerException(f"Max size {max_size_bytes} must be positive")

        # Estimate bytes per millisecond for the audio format
        if self.output_format == "wav":
            # WAV: sample_width * channels * sample_rate / 1000
            bytes_per_ms = (
                audio.sample_width * audio.channels * audio.frame_rate
            ) / 1000
        else:
            # Compressed formats: use bitrate approximation
            kbps = int(self.bitrate[:-1])  # Remove 'k' from '192k'
            bytes_per_ms = (kbps * 1000) / (8 * 1000)  # kbps to bytes/ms

        chunk_duration_ms = int(max_size_bytes / bytes_per_ms)

        return self.split_by_time(
            file_path, chunk_duration_ms, sections, strict, output_dir
        )

    def trim(
        self,
        file_path: Union[str, Path],
        trim_start: Optional[float] = None,
        trim_end: Optional[float] = None,
        trim_range: Optional[Tuple[float, float]] = None,
        output_suffix: str = "-trimmed",
    ) -> Path:
        """
        Trim audio file from start, end, or specific range.

        Args:
            file_path: Path to audio file
            trim_start: Seconds to trim from start
            trim_end: Seconds to trim from end
            trim_range: Tuple of (start_sec, end_sec) to keep
            output_suffix: Suffix for output filename

        Returns:
            Path to trimmed audio file
        """

        trim_start = None if trim_start == 0 else trim_start
        trim_end = None if trim_end == -1 else trim_end

        if sum(x is not None for x in [trim_start, trim_end, trim_range]) != 1:
            raise SlicerException(
                "Specify exactly one of: trim_start, trim_end, or trim_range"
            )

        file_path = self._validate_file(file_path)
        audio = self._load_audio(file_path)
        total_duration_ms = len(audio)

        if trim_start is not None:
            if trim_start <= 0:
                raise SlicerException("Trim start must be positive")
            start_ms = int(trim_start * 1000)
            if start_ms >= total_duration_ms:
                raise SlicerException(
                    f"Trim start {start_ms} exceeds audio duration {total_duration_ms}"
                )
            trimmed_audio = audio[start_ms:]

        elif trim_end is not None:
            if trim_end <= 0:
                raise SlicerException(f"Trim end {trim_end} must be positive")
            end_ms = int(trim_end * 1000)
            if end_ms > total_duration_ms:
                raise SlicerException(
                    f"Trim end {end_ms} exceeds audio duration {total_duration_ms}"
                )
            # From beginning to end 0--> end_ms
            trimmed_audio = audio[:end_ms]

        else:  # trim_range
            start_sec, end_sec = trim_range
            """
                If both start and end are  provided means that this
            is a range so, end can be smaller than start since it will be measure
            from the end of file towards start
            """
            if start_sec < 0:  # or end_sec <= start_sec:
                raise SlicerException("Invalid time range")

            start_ms = int(start_sec * 1000)
            end_ms = int(end_sec * 1000)

            if end_ms > total_duration_ms:
                raise SlicerException(
                    f"Trim {end_ms} range exceeds audio duration {total_duration_ms}"
                )

            trimmed_audio = audio[start_ms:-end_ms]

        output_path = self._get_output_path(file_path, output_suffix)
        self._save_audio(trimmed_audio, output_path)

        return output_path

    def get_audio_info(self, file_path: Union[str, Path]) -> dict:
        """
        Get information about the audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with audio information
        """
        file_path = self._validate_file(file_path)
        audio = self._load_audio(file_path)

        return {
            "duration_seconds": len(audio) / 1000,
            "duration_minutes": len(audio) / 60000,
            "channels": audio.channels,
            "sample_width": audio.sample_width,
            "frame_rate": audio.frame_rate,
            "file_size_bytes": file_path.stat().st_size,
        }
