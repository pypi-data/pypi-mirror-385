import os
import subprocess
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir


def get_config_dir() -> Path:
    return Path(user_config_dir("gptme"))


def get_readline_history_file() -> Path:
    # TODO: move to data dir
    return get_config_dir() / "history"


def get_pt_history_file() -> Path:
    return get_data_dir() / "history.pt"


def get_data_dir() -> Path:
    # used in testing, so must take precedence
    if "XDG_DATA_HOME" in os.environ:
        return Path(os.environ["XDG_DATA_HOME"]) / "gptme"

    # just a workaround for me personally
    old = Path("~/.local/share/gptme").expanduser()
    if old.exists():
        return old

    return Path(user_data_dir("gptme"))


def get_logs_dir() -> Path:
    """Get the path for **conversation logs** (not to be confused with the logger file)"""
    if "GPTME_LOGS_HOME" in os.environ:
        path = Path(os.environ["GPTME_LOGS_HOME"])
    else:
        path = get_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_gptme_dir() -> Path | None:
    """
    Walks up the directory tree from the working dir to find the project root,
    which is a directory containing a `gptme.toml` file.
    Or if none exists, the first parent directory with a git repo.

    Meant to be used in scripts/tools to detect a suitable location to store agent data/logs.
    """
    path = Path.cwd()
    while path != Path("/"):
        if (path / "gptme.toml").exists():
            return path
        path = path.parent

    # if no gptme.toml file was found, look for a git repo
    return _get_project_git_dir_walk()


def get_project_git_dir() -> Path | None:
    return _get_project_git_dir_walk()


def _get_project_git_dir_walk() -> Path | None:
    # if no gptme.toml file was found, look for a git repo
    path = Path.cwd()
    while path != Path("/"):
        if (path / ".git").exists():
            return path
        path = path.parent
    return None


def _get_project_git_dir_call() -> Path | None:
    try:
        projectdir = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return Path(projectdir)
    except subprocess.CalledProcessError:
        return None


def _init_paths():
    # create all paths
    for path in [get_config_dir(), get_data_dir(), get_logs_dir()]:
        path.mkdir(parents=True, exist_ok=True)


# run once on init
_init_paths()
