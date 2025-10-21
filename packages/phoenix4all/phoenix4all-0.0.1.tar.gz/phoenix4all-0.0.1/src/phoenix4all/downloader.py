"""Command line interface for downloading Phoenix models."""

import logging
import pathlib
from typing import Any, Optional

import click

from phoenix4all.log import logger
from phoenix4all.sources import find_source, list_sources
import functools
# Creat groups from source registry

sources = list_sources()


@click.group()
def main():
    """Download Phoenix model files from various sources."""
    pass

for source_name in sources:
    source_klass = find_source(source_name)
    available_models = source_klass.available_models()

    def download_command(
        path: click.Path,
        mkdir: bool,
        progress: bool,
        teff: float,
        logg: float,
        feh: float,
        alpha: float,
        teff_range: Optional[tuple[float, float]],
        logg_range: Optional[tuple[float, float]],
        feh_range: Optional[tuple[float, float]],
        alpha_range: Optional[tuple[float, float]],
        model: str,
        base_url: str,
        source_klass=source_klass,
    ):
        logging.basicConfig(level=logging.INFO)
        logging.getLogger("phoenix4all").setLevel(logging.INFO)
        output_path = pathlib.Path(path)

        if mkdir:
            pathlib.Path(output_path).mkdir(parents=False, exist_ok=True)

        teff = teff_range or teff
        logg = logg_range or logg
        feh = feh_range or feh
        alpha = alpha_range or alpha

        logger.info(f"Downloading Phoenix models from source '{source_name}' to '{output_path}'")

        source_klass.download_model(
            output_dir=output_path,
            teff=teff,
            logg=logg,
            feh=feh,
            alpha=alpha,
            mkdir=mkdir,
            model_name=model,
            progress=progress,
            base_url=base_url,
        )
    
    download_command.__doc__ = f"""Download Phoenix model files to PATH from source '{source_name}'.
    
    If an existing directory is given, it will check which files are already present/complete
    and only download missing/incomplete files.
    """ 



    @main.command(name=source_name)
    @click.argument(
        "path",
        type=click.Path(
            exists=False, file_okay=False, dir_okay=True, path_type=pathlib.Path
        ),
    )
    @click.option(
        "--mkdir/--no-mkdir",
        default=False,
        help="Create the output directory if it does not exist.",
    )
    @click.option("--progress/--no-progress", default=False, help="Show download progress bar.")
    @click.option("--teff", type=float, default="all")
    @click.option("--logg", type=float, default=0.0)
    @click.option("--feh", type=float, default=0.0)
    @click.option("--alpha", type=float, default=0.0)
    @click.option("--teff-range", type=(float, float), default=None, help="Range of Teff values to download (min max).")
    @click.option("--logg-range", type=(float, float), default=None, help="Range of logg values to download (min max).")
    @click.option("--feh-range", type=(float, float), default=None, help="Range of [Fe/H] values to download (min max).")
    @click.option(
        "--alpha-range", type=(float, float), default=None, help="Range of [alpha/Fe] values to download (min max)."
    )
    @click.option(
        "--model",
        type=click.Choice(available_models),
        default=None,
        help="Optional model name to download (if supported by source).",
    )
    @click.option("--base-url", type=str, default=None, help="Optional base URL to download from (if supported by source).")
    @functools.wraps(download_command)
    def command_wrapper(
                path: click.Path,
        mkdir: bool,
        progress: bool,
        teff: float,
        logg: float,
        feh: float,
        alpha: float,
        teff_range: Optional[tuple[float, float]],
        logg_range: Optional[tuple[float, float]],
        feh_range: Optional[tuple[float, float]],
        alpha_range: Optional[tuple[float, float]],
        model: str,
        base_url: str,
        source_klass=source_klass,
    ):
        return download_command(
            path,
            mkdir,
            progress,
            teff,
            logg,
            feh,
            alpha,
            teff_range,
            logg_range,
            feh_range,
            alpha_range,
            model,
            base_url,
            source_klass,
        )




# @click.command()
# @click.argument("path", type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=pathlib.Path))
# @click.argument("source", type=click.Choice(list_sources()))
# @click.option("--mkdir/--no-mkdir", default=False, help="Create the output directory if it does not exist.")
# @click.option("--progress/--no-progress", default=False, help="Show download progress bar.")
# @click.option("--teff", type=float, default="all")
# @click.option("--logg", type=float, default=0.0)
# @click.option("--feh", type=float, default=0.0)
# @click.option("--alpha", type=float, default=0.0)
# @click.option("--teff-range", type=(float, float), default=None, help="Range of Teff values to download (min max).")
# @click.option("--logg-range", type=(float, float), default=None, help="Range of logg values to download (min max).")
# @click.option("--feh-range", type=(float, float), default=None, help="Range of [Fe/H] values to download (min max).")
# @click.option(
#     "--alpha-range", type=(float, float), default=None, help="Range of [alpha/Fe] values to download (min max)."
# )
# @click.option("--model", type=str, default=None, help="Optional model name to download (if supported by source).")
# @click.option("--base-url", type=str, default=None, help="Optional base URL to download from (if supported by source).")
# def main(
#     path: click.Path,
#     source: str,
#     mkdir: bool,
#     progress: bool,
#     teff: float,
#     logg: float,
#     feh: float,
#     alpha: float,
#     teff_range: Optional[tuple[float, float]],
#     logg_range: Optional[tuple[float, float]],
#     feh_range: Optional[tuple[float, float]],
#     alpha_range: Optional[tuple[float, float]],
#     model: str,
#     base_url: str,
# ):
#     """Download Phoenix model files to PATH from SOURCE.

#     If an existing directory is given, it will check which files are already present/complete
#     and only download missing/incomplete files.

#     Example usage:

#     \b

#         python -m phoenix4all.downloader  /path/to/output synphot --progress --teff-range 3500 8000 --logg-range 0.0 5.0 --feh-range -2.0 1.0 --alpha-range 0.0 0.4

#     This will download all Synphot Phoenix models with:

#         - Teff between 3500 and 8000 K\n
#         - logg between 0.0 and 5.0\n
#         - [Fe/H] between -2.0 and +1.0\n
#         - [alpha/Fe] between 0.0 and +0.4\n

#     You can also specify single values for logg, feh, and alpha, e.g.:
#     \b

#         python -m phoenix4all.downloader /path/to/output synphot --teff 3500 --logg 4.5 --feh 0.0 --alpha 0.0 --progress
#     """
#     logging.basicConfig(level=logging.INFO)
#     logging.getLogger("phoenix4all").setLevel(logging.INFO)
#     output_path = pathlib.Path(path)

#     if mkdir:
#         pathlib.Path(output_path).mkdir(parents=False, exist_ok=True)

#     teff = teff_range or teff
#     logg = logg_range or logg
#     feh = feh_range or feh
#     alpha = alpha_range or alpha

#     source_klass = find_source(source)
#     logger.info(f"Downloading Phoenix models from source '{source}' to '{output_path}'")

#     source_klass.download_model(
#         output_dir=output_path,
#         teff=teff,
#         logg=logg,
#         feh=feh,
#         alpha=alpha,
#         mkdir=mkdir,
#         model_name=model,
#         progress=progress,
#         base_url=base_url,
#     )


if __name__ == "__main__":
    main()
