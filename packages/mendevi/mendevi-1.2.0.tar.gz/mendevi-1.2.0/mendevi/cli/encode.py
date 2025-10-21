#!/usr/bin/env python3

"""Perform encoding measures."""

import fractions
import hashlib
import itertools
import pathlib
import sqlite3

from context_verbose import Printer
import click
import numpy as np

from mendevi.database.complete import add_environment
from mendevi.encode import encode_and_store
from mendevi.utils import compute_video_hash, get_pix_fmt, get_rate_video, get_resolution
from .parse import PixelParamType, ResolutionParamType, parse_videos_database


ENCODERS = {"libx264", "libx265", "libvpx-vp9", "libsvtav1", "vvc"}


def _parse_args(prt: Printer, kwargs: dict):
    """Verification of the arguments."""
    # repeat
    assert "repeat" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["repeat"], int), kwargs["repeat"].__class__.__name__
    assert kwargs["repeat"] >= 1, kwargs["repeat"]
    prt.print(f"repeat    : {kwargs['repeat']}")

    # effort
    assert "effort" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["effort"], tuple), kwargs["effort"].__class__.__name__
    assert all(isinstance(p, str) for p in kwargs["effort"]), kwargs["effort"]
    assert all(p in {"fast", "medium", "slow"} for p in kwargs["effort"]), kwargs["effort"]
    prt.print(f"efforts   : {', '.join(kwargs['effort'])}")

    # encoder
    assert "encoder" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["encoder"], tuple), kwargs["encoder"].__class__.__name__
    assert all(isinstance(e, str) for e in kwargs["encoder"]), kwargs["encoder"]
    assert all(e in ENCODERS for e in kwargs["encoder"]), kwargs["encoder"]
    prt.print(f"encoders  : {', '.join(kwargs['encoder'])}")

    # points
    assert "points" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["points"], int), kwargs["points"].__class__.__name__
    assert kwargs["points"] >= 1, kwargs["points"]
    kwargs["quality"] = np.linspace(
        1.0/(kwargs["points"]+1),
        kwargs["points"]/(kwargs["points"]+1),
        kwargs["points"],
        dtype=np.float16,
    ).tolist()
    prt.print(f"qualities : k/{kwargs['points']+1}, k \u2208 [1, {kwargs['points']}]")

    # threads
    assert "threads" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["threads"], tuple), kwargs["threads"].__class__.__name__
    assert all(isinstance(t, int) for t in kwargs["threads"]), kwargs["threads"]
    assert all(t >= 1 for t in kwargs["threads"]), kwargs["threads"]
    prt.print(f"threads   : {', '.join(map(str, kwargs['threads']))}")

    # fps
    assert "fps" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["fps"], tuple), kwargs["fps"].__class__.__name__
    assert all(isinstance(f, fractions.Fraction) for f in kwargs["fps"]), kwargs["fps"]
    assert all(f > 0 for f in kwargs["fps"]), kwargs["fps"]
    if kwargs["fps"]:
        kwargs["fps"] = [f.limit_denominator(1001) for f in kwargs["fps"]]
        prt.print(f"fps       : {', '.join(map(str, kwargs['fps']))}")
    else:
        kwargs["fps"] = (None,)

    # resolution
    assert "resolution" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["resolution"], tuple), kwargs["resolution"].__class__.__name__
    assert all(
        isinstance(r, tuple) and len(r) == 2 and all(isinstance(s, int) and s > 0 for s in r)
        for r in kwargs["resolution"]
    ), kwargs["resolution"]
    if kwargs["resolution"]:
        prt.print(f"resolution: {', '.join(f'w={w}:h={h}' for h, w in kwargs['resolution'])}")
    else:
        kwargs["resolution"] = (None,)

    # pix_fmt
    assert "pix_fmt" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["pix_fmt"], tuple), kwargs["pix_fmt"].__class__.__name__
    assert all(isinstance(p, str) for p in kwargs["pix_fmt"]), kwargs["pix_fmt"]
    if kwargs["pix_fmt"]:
        prt.print(f"pix_fmt   : {', '.join(kwargs['pix_fmt'])}")
    else:
        kwargs["pix_fmt"] = (None,)

    # vbr
    assert "vbr" in kwargs, sorted(kwargs)
    assert isinstance(kwargs["vbr"], tuple), kwargs["vbr"].__class__.__name__
    assert all(
        vbr in {"1", "0", "yes", "no", "true", "false", 1, 0, True, False} for vbr in kwargs["vbr"]
    ), kwargs["vbr"]
    kwargs["vbr"] = sorted({
        {
            "1": True,
            "0": False,
            "yes": True,
            "no": False,
            "true": True,
            "false": False,
            1: True,
            0: False,
            True: True,
            False: False
        }[vbr]
        for vbr in kwargs["vbr"]
    })
    prt.print(
        "bitrate   : "
        f"{' and '.join({True: 'variable', False: 'constant'}[vbr] for vbr in kwargs['vbr'])}"
    )

    # filter
    kwargs["filter"] = kwargs.get("filter", ())
    assert isinstance(kwargs["filter"], tuple), kwargs["filter"].__class__.__name__
    assert all(isinstance(f, str) for f in kwargs["filter"]), kwargs["filter"]
    if kwargs["filter"]:
        prt.print(f"filters   : {', '.join(map(str, kwargs['filter']))}")
    else:
        kwargs["filter"] = (None,)


@click.command()
@click.argument("videos", type=click.Path(), nargs=-1)
@click.option("-d", "--database", type=click.Path(), help="The database path.")
@click.option(
    "-r", "--repeat",
    type=int,
    default=2,
    help="The number of times the encoding is repeated on this machine.",
)
@click.option(
    "-e", "--effort",
    type=click.Choice(["fast", "medium", "slow"]),
    default=["medium"],
    multiple=True,
    help="The compression effort (default = medium).",
)
@click.option(
    "-c", "--encoder",
    type=click.Choice(sorted(ENCODERS)),
    default=sorted(ENCODERS),
    multiple=True,
    help="The encoder name.",
)
@click.option(
    "-n", "--points",
    type=int,
    default=24,
    help="The number of quality point per encoder.",
)
@click.option(
    "-t", "--threads",
    type=int,
    default=[8],
    multiple=True,
    help="The number of threads used by encoders.",
)
@click.option(
    "-f", "--fps",
    type=fractions.Fraction,
    multiple=True,
    help="The optional framerate conversion during encoding.",
)
@click.option(
    "--resolution",
    type=ResolutionParamType(),
    multiple=True,
    help="The optional video shape conversion during encoding.",
)
@click.option(
    "--pix_fmt",
    type=PixelParamType(),
    multiple=True,
    help="The optional pixel format conversion during encoding.",
)
@click.option(
    "-v", "--vbr",
    type=click.Choice(["1", "0", "yes", "no", "true", "false"]),
    default=["1"],
    multiple=True,
    help="The optional variable bit rate rule.",
)
@click.option(
    "--filter",
    type=str,
    multiple=True,
    help="The ffmpeg filter to apply before encoding.",
)
def main(videos: tuple, database: str = None, **kwargs):
    """Measures activity during encoding.

    \b
    Parameters
    ----------
    videos : tuple[pathlike]
        The source videos to be transcoded.
        It can be a glob expression, a directory or a file path.
    database : pathlike, optional
        The path to the database where all measurements are stored.
        If a folder is provided, the database is created inside this folder.
        By default, it is created right next to the video.
    repeat : int, default=2
        The number of times the experiment is repeated on this environment.
        This allows us to estimate the variance of measurements.
    effort : tuple[str], default=("medium",)
        The effort made to compress, `fast`, `medium` or `slow`.
    encoder : tuple[str], default=("libsvtav1", "libvpx-vp9", "libx264", "libx265", "vvc")
        The encoders and therefore the codecs to use.
    points : int, default=24
        The number of different qualities to use.
        It is an indirect way to determine the CRF or the QP.
        The quality values are distributed evenly over ]0, 1[,
        for example, points=3 => qualities=[0.25, 0.5, 0.75].
    threads : int, default=8
        The theoretical number of threads used by the encoder.
        This roughly reflects the number of logical cores used.
    fps : fractions.Fraction, optional
        If provided, the reference video will be resampled on fly just before being encoded.
        This is therefore the frame rate of the transcoded video.
        If this argument is not provided, the frame rate remains unchanged.
    resolution : tuple[int, int], optional
        If provided, the reference video will be reshaped on fly just before being encoded.
        This is therefore the resolution of the transcoded video.
        If this argument is not provided, the resolution remains unchanged.
    pix_fmt : str, optional
        If provided, A pixel conversion is performed during encoding.
    vbr : tuple[bool]
        Boolean that is ``true`` if the bit rate is variable (crf mode),
        or ``false`` if it is constant (cbr mode).
    filter : str, optional
        A video ffmpeg filter (after -vf) which applies at the time of transcoding,
        more precisely between decoding and conversion. It is a kind of pre-conversion.
    """
    with Printer("Parse configuration...") as prt:
        videos, database = parse_videos_database(prt, videos, database)
        assert videos, "at least one video is required"
        _parse_args(prt, kwargs)

    # preparation of context
    env_id = add_environment(database)
    kwargs["src_vid_id"]: dict[pathlib.Path, bytes] = compute_video_hash(videos)

    keys = [
        "effort", "encoder", "filter", "fps", "pix_fmt", "quality", "resolution", "threads", "vbr"
    ]

    # retrieves the settings for videos that have already been transcoded
    with sqlite3.connect(database) as sql_database, Printer("Search already done...") as prt:
        sql_database.row_factory = sqlite3.Row
        done: dict[tuple, int] = {}
        for values in sql_database.execute(
            "SELECT * FROM t_enc_encode WHERE enc_env_id=?", (env_id,)
        ):
            values = {
                "effort": values["enc_effort"],
                "encoder": values["enc_encoder"],
                "filter": values["enc_filter"] or None,
                "fps": fractions.Fraction(values["enc_fps"]).limit_denominator(1001),
                "pix_fmt": values["enc_pix_fmt"],
                "quality": float(values["enc_quality"]),
                "resolution": (values["enc_height"], values["enc_width"]),
                "src_vid_id": values["enc_src_vid_id"],
                "threads": values["enc_threads"],
                "vbr": bool(values["enc_vbr"]),
            }
            values = tuple(values[k] for k in ["src_vid_id", *keys])
            done[values] = done.get(values, 0) + 1
        prt.print(f"{sum(done.values())} video already encoded under these environment")

    # iterate on all parameters
    loops = sorted(
        itertools.product(videos, *(kwargs[k] for k in keys)),
        key=lambda t: hashlib.md5(str(t).encode("utf-8")).hexdigest(),  # repetable shuffle
    )
    for i, (repeat, values) in enumerate(itertools.product(range(kwargs["repeat"]), loops)):
        values = dict(zip(["video", *keys], values, strict=True), repeat=values[0])
        values["repeat"] = repeat
        values["fps"] = values["fps"] or get_rate_video(values["video"])
        values["pix_fmt"] = values["pix_fmt"] or get_pix_fmt(values["video"])
        values["resolution"] = values["resolution"] or get_resolution(values["video"])
        values["src_vid_id"] = kwargs["src_vid_id"][values["video"]]
        key = (values["src_vid_id"],) + tuple(values[k] for k in keys)
        if done.get(key, 0) > values["repeat"]:
            continue
        with Printer(f"Encode {i+1}/{kwargs["repeat"]*len(loops)}...", color="cyan") as prt:
            encode_and_store(database, env_id, values.pop("video"), **values)
            done[key] = done.get(key, 0) + 1
            prt.print_time()
