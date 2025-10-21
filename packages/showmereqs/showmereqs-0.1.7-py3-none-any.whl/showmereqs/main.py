import sys
from pathlib import Path

import click

from showmereqs.analyze import get_third_party_imports
from showmereqs.generate import generate_reqs
from showmereqs.package_info import PackageInfo

logo = (
    "\033[92m"
    + r"""
 ____  _                    __  __       ____                
/ ___|| |__   _____  __  _ |  \/  | ___ |  _ \ ___  __ _ ___ 
\___ \| '_ \ / _ \ \/  \/ || |\/| |/ _ \| |_) / _ \/ _` / __|
 ___) | | | | (_) \  /\  / | |  | |  __/|  _ <  __/ (_| \__ \
|____/|_| |_|\___/ \/  \/  |_|  |_|\___||_| \_\___|\__, |___/
                                                      \_|     
"""
    + "\033[0m"
)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "analyse_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    default=".",
)
@click.option(
    "--outdir",
    "-o",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    default=".",
    help="path to output directory, default is current path",
)
@click.option(
    "--pypi-server",
    "-p",
    type=str,
    default="https://pypi.org/pypi",
    help="the custom PyPI server URL",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="whether to force overwrite output file",
)
@click.option(
    "--no-detail",
    "-nd",
    is_flag=True,
    default=False,
    help="detailed information in requirements.txt",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="show verbose information",
)
def main(
    analyse_dir: str,
    outdir: str,
    pypi_server: str,
    force: bool,
    no_detail: bool,
    verbose: bool,
) -> None:
    """Analyze Python project dependencies and generate requirements.txt"""
    print(logo)

    check_outdir(outdir, force)

    print(f"analyzing {analyse_dir}...")

    print(f"getting third party imports...")
    third_party_imports = get_third_party_imports(analyse_dir)
    print(f"third party imports: {list(third_party_imports)}")

    print(f"getting package infos...")
    third_party_package_infos = [
        PackageInfo(import_name, pypi_server) for import_name in third_party_imports
    ]

    print(f"generating requirements.txt...")
    generate_reqs(third_party_package_infos, outdir, pypi_server, no_detail)

    print(f"\033[92mgenerate {outdir}\\requirements.txt successfully\033[0m")


def check_outdir(outdir: str, force: bool):
    _outdir = Path(outdir)
    req_file = _outdir / "requirements.txt"
    if _outdir.exists():
        if not force and req_file.exists():
            print(
                f"\033[93mfile {req_file} already exists, do you want to overwrite it?\033[0m"
            )
            _input = input("y/n: ")
            if _input != "y":
                print("canceled")
                sys.exit(1)
    else:
        print(f"create directory {outdir}")
        _outdir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
