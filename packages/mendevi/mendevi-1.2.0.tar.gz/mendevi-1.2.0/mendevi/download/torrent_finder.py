#!/usr/bin/env python3

"""Search for available torrent files."""

import pathlib

from context_verbose import Printer
import requests

from mendevi.utils import get_project_root


def get_torrent(name: str) -> pathlib.Path:
    """Retrieve a torrent from its full name.

    Parameters
    ----------
    name : str
        The full torrent name, for example "multithread.db.xz.torrent".

    Returns
    -------
    path : pathlib.Path
        The full path of the torrent.

    Raises
    ------
    KeyError
        If the requested torrent is not included in the list of possible torrents.
    """
    assert isinstance(name, str), name.__class__.__name__

    # look localy first
    local = {p.name: p for p in probe_local_torrent()}
    if name in local:
        return local[name]

    # look in cachedir
    cachedir = pathlib.Path.home() / ".cache" / "mendevi"
    cachedir.mkdir(parents=True, exist_ok=True)
    if (file := cachedir / name).exists():
        return file

    # download online
    with Printer(f"Download {name!r}...", color="green") as prt:
        # look avalable list
        prt.print("get url")
        online = probe_online_torrent()
        if name not in online:
            raise KeyError(f"{name!r} not in {', '.join(sorted(set(local) | set(online)))}")

        # download torrent file
        prt.print(f"download {online[name]}")
        req = requests.get(online[name], stream=True, timeout=60)
        req.raise_for_status()
        torrent_data = req.raw.data
        prt.print(f"{len(torrent_data)} bytes retrieved")
        assert torrent_data

    # write the file
    with open(file, "wb") as raw:
        raw.write(torrent_data)
    return file


def probe_online_torrent() -> dict[str, str]:
    """Search on GitLab online for the names of available torrents.

    Returns
    -------
    torrents : dict
        For each torrent name, provide the URL for downloading it.

    Examples
    --------
    >>> from mendevi.download.torrent_finder import probe_online_torrent
    >>> sorted(probe_online_torrent())
    ['multithread.db.xz.torrent']
    >>>
    """
    url = "https://gitlab.inria.fr/api/v4/projects/rrichard%2Fmendevi/repository/tree?path=dataset"
    req = requests.get(url, timeout=60)
    req.raise_for_status()
    all_files = req.json()
    torrents = {
        f["name"]: f"https://gitlab.inria.fr/rrichard/mendevi/-/raw/main/{f['path']}"
        for f in all_files if f["name"].endswith(".torrent")
    }
    return torrents


def probe_local_torrent() -> set[pathlib.Path]:
    """Search for the names of locally accessible torrents (if the mendevi repository is cloned).

    Returns
    -------
    torrents : set[pathlib.Path]
        Provide all the local torrent files.

    Examples
    --------
    >>> from mendevi.download.torrent_finder import probe_local_torrent
    >>> sorted(t.name for t in probe_local_torrent())
    ['multithread.db.xz.torrent']
    >>>
    """
    return set((get_project_root().parent / "dataset").glob("*.torrent"))
