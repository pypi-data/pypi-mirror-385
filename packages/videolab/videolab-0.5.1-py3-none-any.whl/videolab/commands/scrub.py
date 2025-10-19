# Copyright (C) 2025 Kian-Meng, Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import logging

import av
from videolab.utils import generate_output_filename


def scrub_command(args: argparse.Namespace) -> None:
    """Removes all metadata from a video file."""
    output_file = generate_output_filename(
        args.input_file, args.output_file, "scrubbed"
    )

    try:
        with av.open(args.input_file, mode="r") as in_container:
            with av.open(output_file, mode="w") as out_container:
                out_container.metadata.clear()

                stream_map = {}

                for in_stream in in_container.streams:
                    if args.no_audio and in_stream.type == "audio":
                        continue

                    out_stream = out_container.add_stream_from_template(
                        template=in_stream
                    )
                    out_stream.metadata.clear()
                    stream_map[in_stream.index] = out_stream

                if not stream_map:
                    logging.error(f"No streams to process in '{args.input_file}'.")
                    return

                # remuxing is the process of changing the container format of a
                # media file without re-encoding its audio or video streams
                for packet in in_container.demux():
                    # some stream within a video, especially data or subtitle
                    # streams, can contain packets without a decoding timestamp
                    if packet.dts is None:
                        continue
                    if packet.stream.index in stream_map:
                        packet.stream = stream_map[packet.stream.index]
                        out_container.mux(packet)
    except av.AVError as e:
        logging.error(f"Error processing video file: {e}")
    except FileNotFoundError:
        logging.error(f"Input file '{args.input_file}' not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Registers the "scrub" subcommand."""
    parser = subparsers.add_parser(
        "scrub",
        help="Remove all metadata",
        description=(
            "Removes all container-level and stream-level metadata "
            "from a video file by remuxing it"
        ),
    )
    parser.add_argument("input_file", type=str, help="Path to the input video file")
    parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        default=None,
        help=(
            "Path to save the scrubbed video file, "
            "defaults: '<input_file>_scrubbed.<ext>'"
        ),
    )
    parser.add_argument(
        "--no-audio", action="store_true", help="Remove the audio from the video file"
    )
    parser.set_defaults(func=scrub_command)
