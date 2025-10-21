import re
import subprocess
from pathlib import Path
from typing import Literal, Optional

try:
    import click
except ImportError:
    cmd = ["uv", "add", "click", "--dev"]
    input(f"即将执行: {cmd}, 确认工作目录, 按回车继续...")
    subprocess.run(cmd)

try:
    from rich import print
except ImportError:
    cmd = ["uv", "add", "rich", "--dev"]
    input(f"即将执行: {cmd}, 确认工作目录, 按回车继续...")
    subprocess.run(cmd)

new_version = ""


def main():
    step = {
        "检查git更改": check_git_changes,
        "暂存更改": stage_all_changes,
        "增加版本号": increase_version,
        "暂存版本号更改": stage_version_changes,
        "提交所有更改": commit_changes,
        "添加tag": add_tag,
        "推送更改": push_changes,
        "推送tag": push_tags,
    }
    print(f"[cyan]以下工作将执行:[/]")
    for i, name in enumerate(step.keys()):
        print(f"{i + 1}. {name}")
    if not click.confirm("是否继续?"):
        print("[red]已取消[/]")
        exit()

    print(f"[cyan]开始执行:[/]")
    for name, func in step.items():
        print(f"[yellow]===={name}====:[/]")
        func()


def find_root_dir() -> Path:
    depth = 0
    MAX_DEPTH = 10
    parent = Path(__file__).parent
    while depth < MAX_DEPTH:
        if (parent / "pyproject.toml").exists():
            return parent
        parent = parent.parent
        depth += 1
    raise ValueError(
        "pyproject.toml not found, please run this script in the sub directory of the project"
    )


root_dir = find_root_dir()
pyproject_path = root_dir / "pyproject.toml"


def run_command(
    cmd: Optional[list[str] | str] = None, cwd: Optional[str] = None
) -> str:
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    try:
        print(f"[cyan]执行命令: {cmd}[/]")
        result = subprocess.run(cmd, cwd=cwd, check=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Git命令错误: {e}")
        print(f"错误输出: {e.stderr}")
        raise


def get_git_changes():
    try:
        # 检查暂存区
        staged = run_command(["git", "diff", "--staged", "--name-only"])
        # 检查工作区
        unstaged = run_command(["git", "diff", "--name-only"])
        # 检查未跟踪文件
        untracked = run_command(["git", "ls-files", "--others", "--exclude-standard"])
        return {
            "staged": staged.split("\n") if staged else [],
            "unstaged": unstaged.split("\n") if unstaged else [],
            "untracked": untracked.split("\n") if untracked else [],
        }
    except Exception as e:
        print(f"检查失败: {e}")
        return {"staged": [], "unstaged": [], "untracked": []}


def check_git_changes():
    changes = get_git_changes()
    if changes["staged"] or changes["unstaged"] or changes["untracked"]:
        print("Git 仓库中有未提交的更改。")
        return False
    return True


def stage_all_changes():
    result = run_command(["git", "add", "."])
    print(f"[green]已暂存所有更改[/]")
    return result


def stage_version_changes():
    result = run_command(["git", "add", "pyproject.toml"])
    print(f"[green]已暂存版本号更改[/]")
    return result


def get_version(content: str):
    return re.search(r'version\s*=\s*"([^"]*)"', content).group(1)


def increase_version(v_type: Optional[Literal["major", "minor", "patch"]] = None):
    global new_version
    if not v_type:
        v_type = input("请输入版本类型(major, minor, patch): ")

    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    changes = [
        1 if v_type == "major" else 0,
        1 if v_type == "minor" else 0,
        1 if v_type == "patch" else 0,
    ]
    old_version_lst = get_version(content).split(".")

    new_version = ".".join(
        str(int(old_v) + change) for old_v, change in zip(old_version_lst, changes)
    )

    content = re.sub(r'version\s*=\s*"[^"]*"', f'version = "{new_version}"', content)

    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[green]已增加版本号: {new_version}[/]")
    return new_version


def commit_changes(msg: Optional[str] = None):
    if not msg:
        msg = input("请输入提交信息: ")
    return run_command(["git", "commit", "-m", msg])


def add_tag(tag: Optional[str] = None):
    if not tag:
        tag = f"v{new_version}"
        input(f"即将添加tag: {tag}, 是否继续?")
    result = run_command(["git", "tag", tag])
    print(f"[green]已添加tag: {tag}[/]")
    return result


def push_changes():
    result = run_command(["git", "push"])
    print(f"[green]已推送更改[/]")
    return result


def push_tags():
    result = run_command(["git", "push", "--tags"])
    print(f"[green]已推送tag[/]")
    return result


if __name__ == "__main__":
    main()
