import typer
import uvicorn
from typing import Annotated, Union
from fastapi_cli.utils.cli import get_uvicorn_log_config

cli = typer.Typer(rich_markup_mode="rich")


@cli.command()
def serve_api(
    host: Annotated[
        str,
        typer.Option(
            help="The host to serve on. For local development in localhost use [blue]127.0.0.1[/blue]. To enable public access, e.g. in a container, use all the IP addresses available with [blue]0.0.0.0[/blue]."
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(
            help="The port to serve on. You would normally have a termination proxy on top (another program) handling HTTPS on port [blue]443[/blue] and HTTP on port [blue]80[/blue], transferring the communication to your app.",
            envvar="PORT",
        ),
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option(
            help="Enable auto-reload of the server when (code) files change. This is [bold]resource intensive[/bold], use it only during development."
        ),
    ] = False,
    root_path: Annotated[
        str,
        typer.Option(
            help="The root path is used to tell your app that it is being served to the outside world with some [bold]path prefix[/bold] set up in some termination proxy or similar."
        ),
    ] = "",
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info."
        ),
    ] = True,
    forwarded_allow_ips: Annotated[
        Union[str, None],
        typer.Option(
            help="Comma separated list of IP Addresses to trust with proxy headers. The literal '*' means trust everything."
        ),
    ] = None,
    workers: Annotated[
        Union[int, None],
        typer.Option(help="Count of worker threads to use for serving."),
    ] = None,
):
    uvicorn.run(
        app="pyskat.api:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        root_path=root_path,
        proxy_headers=proxy_headers,
        forwarded_allow_ips=forwarded_allow_ips,
        log_config=get_uvicorn_log_config(),
    )


@cli.command()
def serve_wui(
    host: Annotated[
        str,
        typer.Option(
            help="The host to serve on. For local development in localhost use [blue]127.0.0.1[/blue]. To enable public access, e.g. in a container, use all the IP addresses available with [blue]0.0.0.0[/blue]."
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(
            help="The port to serve on. You would normally have a termination proxy on top (another program) handling HTTPS on port [blue]443[/blue] and HTTP on port [blue]80[/blue], transferring the communication to your app.",
            envvar="PORT",
        ),
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option(
            help="Enable auto-reload of the server when (code) files change. This is [bold]resource intensive[/bold], use it only during development."
        ),
    ] = False,
    root_path: Annotated[
        str,
        typer.Option(
            help="The root path is used to tell your app that it is being served to the outside world with some [bold]path prefix[/bold] set up in some termination proxy or similar."
        ),
    ] = "",
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info."
        ),
    ] = True,
    forwarded_allow_ips: Annotated[
        Union[str, None],
        typer.Option(
            help="Comma separated list of IP Addresses to trust with proxy headers. The literal '*' means trust everything."
        ),
    ] = None,
    workers: Annotated[
        Union[int, None],
        typer.Option(help="Count of worker threads to use for serving."),
    ] = None,
):
    uvicorn.run(
        app="pyskat.wui:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        root_path=root_path,
        proxy_headers=proxy_headers,
        forwarded_allow_ips=forwarded_allow_ips,
        log_config=get_uvicorn_log_config(),
    )


@cli.command()
def init():
    pass
