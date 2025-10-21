import contextlib
import shutil
import socket
import zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer, test
from pathlib import Path

import httpx
from minicli import cli, run

from . import VERSION
from .generator import generate_feed, generate_html
from .models import collect_authors, collect_keywords, configure_numero
from .utils import each_file_from, each_folder_from


@cli
def version():
    """Return the current version."""
    print(f"Crieur version: {VERSION}")


@cli
def generate(
    title: str = "Crieur",
    base_url: str = "/",
    extra_vars: str = "",
    target_path: Path = Path() / "public",
    source_path: Path = Path() / "sources",
    statics_path: Path = Path(__file__).parent / "statics",
    templates_path: Path = Path(__file__).parent / "templates",
    without_statics: bool = False,
    feed_limit: int = 10,
):
    """Generate a new revue website.

    :title: Title of the website (default: Crieur).
    :base_url: Base URL of the website, ending with / (default: /).
    :extra_vars: stringified JSON extra vars passed to the templates.
    :target_path: Path where site is built (default: /public/).
    :source_path: Path where stylo source were downloaded (default: /sources/).
    :statics_path: Path where statics are located (default: @crieur/statics/).
    :template_path: Path where templates are located (default: @crieur/templates/).
    :without_statics: Do not copy statics if True (default: False).
    :feed_limit: Number of max items in the feed (default: 10).
    """
    numeros = []
    for numero in each_folder_from(source_path):
        for corpus_yaml in each_file_from(numero, pattern="*.yaml"):
            numero = configure_numero(corpus_yaml, base_url)
            numeros.append(numero)

    keywords = collect_keywords(numeros)
    authors = collect_authors(numeros)
    generate_html(
        title,
        base_url,
        numeros,
        keywords,
        authors,
        extra_vars,
        target_path,
        templates_path,
    )
    generate_feed(title, base_url, numeros, extra_vars, target_path, number=feed_limit)

    if not without_statics:
        shutil.copytree(statics_path, target_path / "statics", dirs_exist_ok=True)


@cli
def stylo(
    *stylo_ids: str,
    stylo_instance: str = "stylo.huma-num.fr",
    stylo_export: str = "https://export.stylo.huma-num.fr",
    force_download: bool = False,
):
    """Initialize a new revue to current directory from Stylo.

    :stylo_ids: Corpus ids from Stylo, separated by commas.
    :stylo_instance: Instance of Stylo (default: stylo.huma-num.fr).
    :stylo_export: Stylo export URL (default: https://export.stylo.huma-num.fr).
    :force_download: Force download of sources from Stylo (default: False).
    """
    print(
        f"Initializing a new revue: `{stylo_ids}` from `{stylo_instance}` "
        f"through export service `{stylo_export}`."
    )

    sources_path = Path() / "sources"
    if not sources_path.exists():
        Path.mkdir(sources_path)

    for i, stylo_id in enumerate(stylo_ids):
        zip_path = Path() / f"export-{i + 1}-{stylo_id}.zip"
        if force_download or not zip_path.exists():
            url = (
                f"{stylo_export}/generique/corpus/export/"
                f"{stylo_instance}/{stylo_id}/Extract-corpus/"
                "?with_toc=0&with_ascii=0&with_link_citations=0&with_nocite=0"
                "&version=&bibliography_style=chicagomodified&formats=originals"
            )
            print(f"Downloading data from {url} to {zip_path}")
            with Path.open(zip_path, "wb") as fd:
                with httpx.stream("GET", url, timeout=None) as r:
                    for data in r.iter_bytes():
                        fd.write(data)
        else:
            print(
                f"Source already exists: `{zip_path}` (no download). "
                "Use the `--force` option to download it again"
            )

        target_path = sources_path / f"{i + 1}-{stylo_id}"
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(target_path)
            print(f"Data extracted to {target_path}")
        except zipfile.BadZipFile:
            zip_problematic_path = Path() / f"problematic-export-{i + 1}-{stylo_id}.zip"
            zip_path.rename(zip_problematic_path)
            print(f"Unable to find corpus with id {stylo_id}!")
            print(
                f"Check out the content of {zip_problematic_path} to try to understand."
            )
            print(
                "Either you use a wrong corpus id or there is an issue with the export."
            )
            return


@cli
def serve(repository_path: Path = Path(), port: int = 8000):
    """Serve an HTML book from `repository_path`/public or current directory/public.

    :repository_path: Absolute or relative path to book’s sources (default: current).
    :port: Port to serve the book from (default=8000)
    """
    print(
        f"Serving HTML book from `{repository_path}/public` to http://127.0.0.1:{port}"
    )

    # From https://github.com/python/cpython/blob/main/Lib/http/server.py#L1307-L1326
    class DirectoryServer(ThreadingHTTPServer):
        def server_bind(self):
            # suppress exception when protocol is IPv4
            with contextlib.suppress(Exception):
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            return super().server_bind()

        def finish_request(self, request, client_address):
            self.RequestHandlerClass(
                request, client_address, self, directory=str(repository_path / "public")
            )

    test(HandlerClass=SimpleHTTPRequestHandler, ServerClass=DirectoryServer, port=port)


def main():
    run()
