#!/usr/bin/env python
import sys
import argparse
from pathlib import Path
from .slicer import AudioProcessor
from .slicer_exceptions import SlicerArgumentException
from .validators import (
    validate_size,
    validate_duration,
    validate_time_range,
    validate_bitrate,
)
from .colors import foreground as fg
from .colors import background as bg
from .formarts import AudioFormarts
from .utils.log.loger import get_logger
from .utils.docs.doc import prep_doc
from .bulk import DirBuster
from .decorators import for_loop_decorator as loop
from .decorators import threaded_for_loop

logger = get_logger()

RESET = fg.RESET


def duration_check(time):
    return isinstance(time, (int, str))


def main():
    parser = argparse.ArgumentParser(
        description="Slice/Trim, Split audio files.", add_help=False
    )

    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this help message and exit."
    )

    # Split Arguments
    parser.add_argument("--file", help="File to be operated on.")

    parser.add_argument(
        "--split", action="store_true", help="Split file by duration or time."
    )

    parser.add_argument("--size", help="Size in MBs for each part/chunk to split")

    parser.add_argument("--duration", help="Split by duration (eg 5sec/5min)")

    # Trim Arguments
    parser.add_argument("--trim", action="store_true", help="Clip/slice by range.")

    parser.add_argument(
        "--trim_start", default=0, help="Start time for the slicing range"
    )
    parser.add_argument("--trim_end", default=-1, help="End time for the slicing range")

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Discard last chunk if it fails to satisfy size/duration requirement",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=-1,
        help="Number of sections to be splitted.",
    )

    parser.add_argument("-O", "--output", help="Where to save the resulting files.")

    parser.add_argument(
        "--format",
        choices=AudioFormarts().surpoted,
        default="mp3",
        help="Formart of resulting files",
    )

    parser.add_argument(
        "--bitrate",
        default="192k",
        help="Bitrate of resulting audio",
    )
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        prep_doc()
        sys.exit(0)

    if not args.file:
        parser.print_usage()
        print(
            f"slicer: {fg.RED_FG}error{RESET}: argument {fg.FCYAN_FG}--file{RESET}: is required"
        )
        sys.exit()

    sections = "max" if args.count == -1 else args.count

    output = args.output if args.output else Path(args.file).parent / "slicer"
    bitrate = validate_bitrate(args.bitrate)

    processor = AudioProcessor(output_format=args.format, bitrate=bitrate)

    input_file = Path(args.file)

    """ SPLIT OPERATION """
    if args.split:
        # Split by size
        if args.size:
            try:
                size, units = validate_size(args.size)
                size_bytes = size * 1024 if units == "kb" else size * 1024 * 1024
                logger.debug(input_file.is_dir())
                if input_file.is_dir():
                    buster = DirBuster(args.file)
                    file_targets = buster.get_dir_files()
                    workers = 4 if len(file_targets) > 3 else len(file_targets)

                    def action(file):
                        logger.info(
                            f"Splitting {fg.BLUE_FG}{file}{RESET} time-based chunks"
                        )
                        chunks = processor.split_by_size(
                            file, size_bytes, sections, args.strict, output
                        )

                        logger.info(
                            f"Created {fg.BLUE_FG}{len(chunks)}{RESET} size-based chunks"
                        )
                        return chunks

                    action()
                    # logger.info(f"Total chunks: {fg.CYAN}{total_chunks}{RESET}")

                else:
                    chunks = processor.split_by_size(
                        args.file, size_bytes, sections, args.strict, output
                    )

                    print(f"Created {fg.BLUE_FG}{len(chunks)}{RESET} size-based chunks")
            except Exception as e:
                print(f"Size split error: {fg.BRED_FG}{e}{RESET}")

        # Split by duration/time
        elif args.duration:
            try:
                duration, units = validate_duration(args.duration)
                duration_ms = (
                    int(duration) * 1000 if units == "sec" else duration * 1000 * 60
                )
                if input_file.is_dir():
                    buster = DirBuster(args.file)
                    file_targets = buster.get_dir_files()
                    workers = 4 if len(file_targets) > 3 else len(file_targets)

                    @threaded_for_loop(file_targets, max_workers=workers)
                    def action(file):
                        logger.info(
                            f"Splitting {fg.BLUE_FG}{file}{RESET} time-based chunks"
                        )
                        chunks = processor.split_by_time(
                            file, duration_ms, sections, args.strict, output
                        )
                        logger.info(
                            f"Created {fg.BLUE_FG}{len(chunks)}{RESET} time-based chunks"
                        )

                        return chunks

                    action()
                    # logger.info(f"Total chunks: {fg.CYAN}{total_chunks}{RESET}")

                else:
                    chunks = processor.split_by_time(
                        args.file, duration_ms, sections, args.strict, output
                    )
                    print(f"Created {fg.BLUE_FG}{len(chunks)}{RESET} time-based chunks")

            except Exception as e:
                print(f"Time split error: {fg.BRED_FG}{e}{RESET}")

        else:
            try:
                raise SlicerArgumentException(
                    f"You must specify one of ({bg.BLUE_BG}{fg.WHITE_FG}duration, size{bg.RESET}){fg.BRED_FG} arguments.{RESET}"
                )
            except Exception as e:
                print(f"{fg.BRED_FG}{e}{RESET}")

    # Clip/Trim Operation
    elif args.trim:
        if not args.trim_start and not args.trim_end:
            raise SlicerArgumentException(
                "Missing --trim_start and --trim_end for trim duration parameters."
            )
        try:
            start, end, is_range = validate_time_range(args.trim_start, args.trim_end)
            if start == 0 and end == -1:
                info = processor.get_audio_info(args.file)

                # trim_end always starts from beginning 0 when trim_start is not provided
                end = info.get("duration_seconds", -1)

            trimmed = (
                processor.trim(args.file, trim_range=(start, end))
                if is_range
                else processor.trim(args.file, trim_start=start, trim_end=end)
            )
            print(f"Trimmed: {fg.GREEN_FG}{trimmed}{RESET}")
        except Exception as e:
            print(f"Trim error: {fg.BRED_FG}{e}{RESET}")

    else:
        try:
            raise SlicerArgumentException("You must use either --trim or --split")
        except Exception as e:
            print(f"{fg.BRED_FG}{e}{RESET}")


if __name__ == "__main__":
    main()
