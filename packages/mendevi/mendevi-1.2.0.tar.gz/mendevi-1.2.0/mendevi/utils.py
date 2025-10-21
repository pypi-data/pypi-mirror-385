#!/usr/bin/env python3

"""Provide simple tools."""

import base64
import functools
import hashlib
import logging
import math
import multiprocessing.pool
import numbers
import pathlib
import re
import typing

from cutcutcodec.core.io import VIDEO_SUFFIXES
import cutcutcodec
import tqdm

from mendevi.cst.profiles import PROFILES


PATHLIKE = str | bytes | pathlib.Path


@functools.cache
def best_profile(height: numbers.Integral, width: numbers.Integral) -> str:
    """Return the closest profile name."""
    assert isinstance(height, numbers.Integral), height.__class__.__name__
    assert isinstance(width, numbers.Integral), width.__class__.__name__
    size = math.sqrt(float(height * width))
    dist_to_profile = {
        abs(math.sqrt(float(v["resolution"][0]*v["resolution"][1])) - size): p
        for p, v in PROFILES.items()
    }
    return dist_to_profile[min(dist_to_profile)]


def compute_video_hash(
    videos: PATHLIKE | typing.Iterable[PATHLIKE]
) -> bytes | dict[pathlib.Path, bytes]:
    r"""Compute the checksum of the video.

    For :math:`n` hash of :math:`b` bits, the proba of the colision :math:`C` is
    :math:`p(C) = 1 - \left(\frac{2^k-1}{2^k}\right)^{\frac{n(n-1)}{2}}`.

    The md5 hash uses :math:`b = 128` bits. If we add one video per second durring 10 years,
    the proba of colision is about :math:`p(C) \approx 1.46*10^{-22}`.

    That's why the md5 hash is used to identify the video files.

    Parameters
    ----------
    videos : pathlike or list[pathlike]
        The single or set of video you want to compute the signature.

    Returns
    -------
    signatures
        The md5 checksum of the video file. In the case of a multiple file,
        a dictionary containing the file and the hash is returned rather a single hash.
        If the file does not exists, return None.
    """
    def _hash(video: PATHLIKE) -> pathlib.Path:
        video = pathlib.Path(video)
        if match := re.search(r"[2-7a-z]{26}", video.stem):
            return video, signature_to_hash(match.group())
        if not (video := video.expanduser()).is_file():
            return video, None
        with open(video, "rb") as raw:
            return video, hashlib.file_digest(raw, "md5").digest()

    if isinstance(videos, list | tuple | set | frozenset):
        with multiprocessing.pool.ThreadPool() as pool:
            return dict(tqdm.tqdm(
                pool.imap_unordered(_hash, videos),
                desc="compute videos checksum",
                dynamic_ncols=True,
                leave=False,
                smoothing=1e-6,
                total=len(videos),
                unit="video",
            ))
    return _hash(videos)[1]


@functools.cache
def get_pix_fmt(*args):
    """Alias to cutcutcodec func."""
    return cutcutcodec.get_pix_fmt(*args)


def get_project_root() -> pathlib.Path:
    """Return the absolute project root folder.

    Examples
    --------
    >>> from mendevi.utils import get_project_root
    >>> root = get_project_root()
    >>> root.is_dir()
    True
    >>> root.name
    'mendevi'
    >>> sorted(p.name for p in root.iterdir())  # doctest: +ELLIPSIS
    ['__init__.py', '__main__.py', ...]
    >>>
    """
    return pathlib.Path(__file__).resolve().parent


@functools.cache
def get_rate_video(*args):
    """Alias to cutcutcodec func."""
    return cutcutcodec.get_rate_video(*args)


@functools.cache
def get_resolution(*args):
    """Alias to cutcutcodec func."""
    return cutcutcodec.get_resolution(*args)


def hash_to_signature(checksum: bytes) -> str:
    r"""Convert the md5 binary hash value into an urlsafe string.

    Bijection of :py:func:`signature_to_hash`.

    Parameters
    ----------
    checksum : bytes
        The 128 bit binary hash value.

    Returns
    -------
    signature : str
        The 26 ascii [2-7a-z] symbols string of the converted checksum.

    Examples
    --------
    >>> from mendevi.utils import hash_to_signature
    >>> hash_to_signature(b"\xd4\x1d\x8c\xd9\x8f\x00\xb2\x04\xe9\x80\t\x98\xec\xf8B~")
    '2qoyzwmpaczaj2mabgmoz6ccpy'
    >>>
    """
    assert isinstance(checksum, bytes), checksum.__class__.__name__
    assert len(checksum) == 16, len(checksum)
    return base64.b32encode(checksum)[:26].decode().lower()


def signature_to_hash(signature: str) -> bytes:
    r"""Convert the string signature into the md5 checksum.

    Bijection of :py:func:`hash_to_signature`.

    Parameters
    ----------
    signature : str
        The 26 ascii [2-7a-z] symbols string of the converted checksum.

    Returns
    -------
    checksum : bytes
        The 128 bit binary hash value.

    Examples
    --------
    >>> from mendevi.utils import signature_to_hash
    >>> signature_to_hash("2qoyzwmpaczaj2mabgmoz6ccpy")
    b'\xd4\x1d\x8c\xd9\x8f\x00\xb2\x04\xe9\x80\t\x98\xec\xf8B~'
    >>>
    """
    assert isinstance(signature, str), signature.__class__.__name__
    assert re.fullmatch(r"[2-7a-z]{26}", signature), signature
    return base64.b32decode(f"{signature.upper()}======".encode())


def unfold_video_files(
    paths: typing.Iterable[PATHLIKE]
) -> typing.Iterable[pathlib.Path]:
    """Explore recursively the folders to find the video path.

    Parameters
    ----------
    paths : list[pathlike]
        All the folders, files, glob or recursive glob expression.

    Yields
    ------
    filename : pathlib.Path
        The path of the video.
    """
    assert hasattr(paths, "__iter__"), paths.__class__.__name__
    for path in paths:
        path = pathlib.Path(path).expanduser()
        if path.is_file():
            yield path
        elif path.is_dir():
            for root, _, files in path.walk():
                for file in files:
                    file = root / file
                    if file.suffix.lower() in VIDEO_SUFFIXES:
                        yield file
        elif "*" in path.name and path.parent.is_dir():
            yield from unfold_video_files(path.parent.glob(path.name))
        elif "**" in (parts := path.parts):
            idx = parts.index("**")
            yield from unfold_video_files(
                pathlib.Path(*parts[:idx]).glob(pathlib.Path(*parts[idx:]))
            )
        else:
            logging.warning("the path %s is not correct", path)
