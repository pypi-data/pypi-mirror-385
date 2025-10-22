# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing
from pathlib import Path

from digitalhub.utils.exceptions import EntityError
from digitalhub.utils.generic_utils import encode_source, encode_string
from digitalhub.utils.uri_utils import has_git_scheme, has_local_scheme

if typing.TYPE_CHECKING:
    from digitalhub_runtime_flower.entities.function.flower_app.entity import FunctionFlowerApp


def source_check(**kwargs) -> dict:
    """
    Check source code.

    Parameters
    ----------
    **kwargs
        Keyword arguments.

    Returns
    -------
    dict
        Checked source.
    """
    fab_source: dict = kwargs.pop("fab_source", None)
    git_source: str = kwargs.pop("git_source", None)
    client_code: str = kwargs.pop("client_code", None)
    server_code: str = kwargs.pop("server_code", None)
    client_src: str = kwargs.pop("client_src", None)
    server_src: str = kwargs.pop("server_src", None)
    client_app: str = kwargs.pop("client_app", None)
    server_app: str = kwargs.pop("server_app", None)

    client_base64 = None
    server_base64 = None
    from_fab_source = False

    if fab_source is not None:
        from_fab_source = True
        git_source = fab_source.get("source")
        client_app = fab_source.get("clientapp")
        server_app = fab_source.get("serverapp")
        client_base64 = fab_source.get("clientbase64")
        server_base64 = fab_source.get("serverbase64")
        # No src in fab_source

    kwargs["fab_source"] = _check_params(
        from_fab_source=from_fab_source,
        git_source=git_source,
        client_src=client_src,
        server_src=server_src,
        client_code=client_code,
        server_code=server_code,
        client_app=client_app,
        server_app=server_app,
        client_base64=client_base64,
        server_base64=server_base64,
    )
    return kwargs


def _check_params(
    from_fab_source: bool = False,
    git_source: str | None = None,
    client_src: str | None = None,
    server_src: str | None = None,
    client_code: str | None = None,
    server_code: str | None = None,
    client_app: str | None = None,
    server_app: str | None = None,
    client_base64: str | None = None,
    server_base64: str | None = None,
) -> dict:
    """
    Check source code.

    Parameters
    ----------
    git_source : str | None
        Github repository URL.
    client_code : str | None
        Client application str source code.
    server_code : str | None
        Server application str source code.
    clientapp : str | None
        Local client application path.
    serverapp : str | None
        Local server application path.
    clientbase64 : str | None
        Client application base64.
    serverbase64 : str | None
        Server application base64.

    Returns
    -------
    dict
        Checked source.
    """

    # Validate inputs
    if git_source is not None:
        if not has_git_scheme(git_source):
            raise EntityError("git_source must be a valid git URL.")
    else:
        if client_app is None or server_app is None:
            raise EntityError("Either git_source or both client_app and server_app must be provided.")

        if client_code is None and client_src is None and client_base64 is None:
            if not from_fab_source:
                raise EntityError("Either client_code or client_src must be provided.")

        if server_code is None and server_src is None and server_base64 is None:
            if not from_fab_source:
                raise EntityError("Either server_code or server_src must be provided.")

    _valid_src(client_src, "client_src")
    _valid_src(server_src, "server_src")

    fab_source = {}

    if git_source is not None:
        fab_source["source"] = git_source

    if client_app is not None:
        fab_source["clientapp"] = client_app

    if server_app is not None:
        fab_source["serverapp"] = server_app

    fab_source["clientbase64"] = _encode_source(
        msg="client_src or client_code",
        src=client_src,
        code=client_code,
        base64=client_base64,
    )

    fab_source["serverbase64"] = _encode_source(
        msg="server_src or server_code",
        src=server_src,
        code=server_code,
        base64=server_base64,
    )

    return fab_source


def source_post_check(exec: FunctionFlowerApp) -> FunctionFlowerApp:
    """
    Post check source.

    Parameters
    ----------
    exec : FunctionFlowerApp
        Executable.

    Returns
    -------
    FunctionFlowerApp
        Updated executable.
    """
    return exec


def _valid_src(src: str | None, src_type: str) -> None:
    """
    Validate source.

    Parameters
    ----------
    src : str
        Source.
    """
    if src is None:
        return
    if not isinstance(src, str):
        raise EntityError(f"{src_type} must be a string.")
    if not has_local_scheme(src):
        raise EntityError(f"{src_type} must have a valid local path.")
    if not Path(src).is_file():
        raise EntityError(f"{src_type} must point to a valid file.")


def _encode_source(
    msg: str,
    src: str | None = None,
    code: str | None = None,
    base64: str | None = None,
) -> str:
    """
    Encode source.

    Parameters
    ----------
    msg : str
        Error message.
    src : str
        Source path.
    code : str | None
        Source code.
    base64 : str | None
        Base64 encoded source.

    Returns
    -------
    str
        Encoded source.
    """
    # Precedence code > src > base64
    if src is not None:
        return encode_source(src)
    if code is not None:
        return encode_string(code)
    if base64 is not None:
        return base64
    raise EntityError(f"Either {msg} must be provided.")
