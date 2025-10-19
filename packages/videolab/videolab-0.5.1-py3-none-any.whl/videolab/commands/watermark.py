import argparse
import logging
from typing import Any, cast, Tuple

import av
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from tqdm import tqdm

from videolab.utils import generate_output_filename


def _create_watermark_image(
    text: str,
    frame_width: int,
    frame_height: int,
    font_size_arg: int | None,
    font_color_str: str,
    position_str: str,
    margin: int,
) -> tuple[np.ndarray, tuple[int, int]]:
    """Creates a transparent watermark image with text."""
    font_size = font_size_arg if font_size_arg is not None else int(frame_height * 0.05)
    font = ImageFont.load_default(size=font_size)

    # Parse font color
    try:
        r, g, b, a = map(int, font_color_str.split(","))
        font_color = (r, g, b, a)
    except ValueError:
        logging.warning(f"Invalid font color format '{font_color_str}'. Using default.")
        font_color = (255, 255, 255, 128)

    # use a dummy image to calculate text size
    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = int(right - left)
    text_height = int(bottom - top)

    # create the watermark image
    img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((-left, -top), text, font=font, fill=font_color)

    # Convert Pillow Image to NumPy array
    watermark_array = np.array(img)

    # calculate position
    if position_str == "top-left":
        x = margin
        y = margin
    elif position_str == "bottom-left":
        x = margin
        y = frame_height - text_height - margin
    elif position_str == "bottom-right":
        x = frame_width - text_width - margin
        y = frame_height - text_height - margin
    elif position_str == "center":
        x = (frame_width - text_width) // 2
        y = (frame_height - text_height) // 2
    else:  # top-right is the default
        x = frame_width - text_width - margin
        y = margin
    position = (x, y)

    return watermark_array, position


def _add_watermark(
    frame: av.VideoFrame, watermark_img: np.ndarray, position: tuple[int, int]
) -> av.VideoFrame:
    """Overlays a watermark image (NumPy array) onto a video frame."""
    frame_array = frame.to_ndarray(format="rgba")
    x, y = position
    h, w, _ = watermark_img.shape

    # extract the alpha channel from the watermark
    alpha_watermark = watermark_img[:, :, 3] / 255.0
    alpha_frame = 1.0 - alpha_watermark

    # apply the watermark using alpha blending (vectorized)
    frame_region = frame_array[y : y + h, x : x + w, 0:3]
    watermark_rgb = watermark_img[:, :, 0:3]

    # The alpha arrays (2D) are broadcasted to the 3rd dimension (color channels)
    frame_region[:] = (
        alpha_frame[:, :, np.newaxis] * frame_region
        + alpha_watermark[:, :, np.newaxis] * watermark_rgb
    )

    # ensure the alpha channel of the frame is opaque where watermark is applied
    frame_array[y : y + h, x : x + w, 3] = (255)

    new_frame = cast(av.VideoFrame, av.VideoFrame.from_ndarray(frame_array, format="rgba"))
    new_frame.pts = frame.pts
    new_frame.time_base = frame.time_base
    return new_frame


def watermark_command(args: argparse.Namespace) -> None:
    """Adds a text watermark to a video."""
    output_file = generate_output_filename(
        args.input_file, args.output_file, "watermarked"
    )

    try:
        with av.open(args.input_file, mode="r") as in_container:
            in_video_stream = next(
                (s for s in in_container.streams if s.type == "video"), None
            )
            if not in_video_stream:
                logging.error(f"No video stream found in '{args.input_file}'.")
                return

            watermark_img, position = _create_watermark_image(
                args.text,
                in_video_stream.width,
                in_video_stream.height,
                args.font_size,
                args.font_color,
                args.position,
                args.margin,
            )

            with av.open(output_file, mode="w") as out_container:
                out_video_stream = out_container.add_stream_from_template(
                    in_video_stream
                )

                total_frames = in_container.streams.video[0].frames
                with tqdm(total=total_frames, unit="frame", desc="Watermarking") as pbar:
                    for packet in in_container.demux(in_video_stream):
                        for frame in packet.decode():
                            new_frame = _add_watermark(frame, watermark_img, position)
                            for new_packet in out_video_stream.encode(new_frame):
                                out_container.mux(new_packet)
                            pbar.update(1)

                # flush the encoder
                for new_packet in out_video_stream.encode():
                    out_container.mux(new_packet)
    except av.AVError as e:
        logging.error(f"Error processing video file: {e}")
    except FileNotFoundError:
        logging.error(f"Input file '{args.input_file}' not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def register_subcommand(subparsers: Any) -> None:
    """Register the 'watermark' subcommand."""
    parser = subparsers.add_parser(
        "watermark",
        help="Add a watermark to a video.",
        description="Adds a watermark to a video file.",
    )
    parser.add_argument("input_file", type=str, help="Path to the input video file")
    parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        default=None,
        help=(
            "Path to save the watermarked video file, "
            "defaults: '<input_file>_watermarked.<ext>'"
        ),
    )
    parser.add_argument(
        "--text", type=str, required=True, help="The text for the watermark"
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=None,
        help="Font size for the watermark text. Defaults to 5%% of video height.",
    )
    parser.add_argument(
        "--font-color",
        type=str,
        default="255,255,255,128",
        help="Font color in RGBA format (e.g., '255,255,255,128').",
    )
    parser.add_argument(
        "--position",
        type=str,
        default="top-right",
        choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
        help="Position of the watermark.",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=20,
        help="Margin from the edges of the video in pixels.",
    )
    parser.set_defaults(func=watermark_command)
