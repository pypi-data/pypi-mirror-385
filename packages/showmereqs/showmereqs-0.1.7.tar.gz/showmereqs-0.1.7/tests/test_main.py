# tests/test_main.py
import os
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from showmereqs.main import main


@pytest.fixture
def runner():
    """create a cli test runner"""
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """create a temp project, copy all_kinds_imports to it"""
    template_dir = Path(__file__).parent / "all_kinds_imports"
    shutil.copytree(template_dir, tmp_path / template_dir.name)
    return tmp_path


def exist(path: Path):
    return os.path.exists(path)


def success_in(output: str) -> bool:
    return "requirements.txt successfully" in output


def test_basic_usage(runner: CliRunner, temp_project: Path):
    """test basic usage"""

    result = runner.invoke(main, [str(temp_project)])
    assert result.exit_code == 0
    assert success_in(result.output)
    assert exist(temp_project / "requirements.txt")


def test_force_overwrite(runner: CliRunner, temp_project: Path):
    """test --force -f option"""

    # create a file
    req_txt = temp_project / "requirements.txt"
    req_txt.write_text("old content")

    # not use -f, should fail
    result = runner.invoke(main, [str(temp_project)])
    assert result.exit_code != 0
    assert req_txt.read_text() == "old content"

    # use -f, should success
    result = runner.invoke(main, [str(temp_project), "-f"])
    assert result.exit_code == 0
    assert req_txt.read_text() != "old content"


def test_custom_outdir(runner: CliRunner, temp_project: Path):
    """test --outdir -o option"""

    custom_dir = temp_project / "custom_dir"
    result = runner.invoke(main, [str(temp_project), "-o", str(custom_dir)])
    assert result.exit_code == 0
    assert exist(custom_dir / "requirements.txt")


def test_invalid_path(runner: CliRunner):
    """test invalid path"""
    result = runner.invoke(main, ["non_existent_path"])
    assert result.exit_code != 0


def test_no_detail_option(runner: CliRunner, temp_project: Path):
    """test --no-detail -nd option"""
    req_txt = temp_project / "requirements.txt"
    result = runner.invoke(main, [str(temp_project), "--no-detail"])

    assert result.exit_code == 0
    assert success_in(result.output)
    assert exist(req_txt)
    txt = req_txt.read_text()

    assert "# package with version\n # [package]" not in txt
