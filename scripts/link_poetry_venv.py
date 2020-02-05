#!/usr/bin/env python3
# -*- codeing: utf8 -*-

"""Poetry creates and manages virtual environments very nicely.

To see the poetry envs you need to run 'poetry env list --full-path'.
"""

import re
import shlex
import subprocess
import argparse
import pathlib
import shutil
import textwrap

VENV_SYMLINK = "venv"
ENV_CLI_ARG = "--env"
AUTOMATIC_DISCOVERY = "automatic"
MINIMUM_POETRY_VERSION = "1.0.0b2"


class ScriptArgParser(object):
    def __init__(self):
        description = """
    EXAMPLE USAGE
    $ %(prog)s {cli_arg} /absolute/path/to/poetry/environment
    or
    $ %(prog)s {cli_arg} {discover}
    ------
    DESCRIPTION
    Poetry handles virtual environments well, negating the need to make your own
    virtual env. However the feature requires Poetry version {poetry_version}.

    Clears any virtual environments in the CWD and creates a symbolic link called
    to the Poetry maintained virtual environment. The symbolic link will be called
    '{name}' and will reside in the CWD.

    The environment can be automatically discovered.

    The absolute path of the Poetry maintained active environment can queried with:
    $ poetry env list --full-path
    ------

    """
        description = description.format(
            name=VENV_SYMLINK,
            discover=AUTOMATIC_DISCOVERY,
            cli_arg=ENV_CLI_ARG,
            poetry_version=MINIMUM_POETRY_VERSION,
        )
        self.description = textwrap.dedent(description)

    @classmethod
    def is_ok_arg(cls, filename):
        """Validate that the filename exits."""
        filepath = pathlib.Path(filename)

        if filename == AUTOMATIC_DISCOVERY:
            return_obj = filename
        elif filepath.exists() and filepath.is_dir():
            return_obj = filepath
        else:
            msg = f"The location '{str(filepath)}' does not exist!"
            return_obj = argparse.ArgumentTypeError(msg)

        if isinstance(return_obj, Exception):
            raise return_obj
        else:
            return return_obj

    def _make_parser(self):
        desc = self.description
        parser = argparse.ArgumentParser(
            description=desc, formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument(
            ENV_CLI_ARG,
            metavar="POETRYENV",
            required=True,
            default=AUTOMATIC_DISCOVERY,
            dest="poetry_env",
            type=lambda x: self.is_ok_arg(x),
            help=(
                f"The environment that Poetry sets up. Can be "
                f"discovered automatically with '{ENV_CLI_ARG} {AUTOMATIC_DISCOVERY}'"
            ),
        )
        return parser

    def get_args(self):
        parser = self._make_parser()
        args = parser.parse_args()
        return vars(args)


class PoetryEnvTool:
    def __init__(self):
        self.cmd = shlex.split("poetry env list --full-path")
        self.version_cmd = shlex.split("poetry --version")
        self.version_rgx = re.compile(r"(\d.*)")
        self.ok_version = self._version_str2tup(MINIMUM_POETRY_VERSION)
        self.active_token = "(Activated)"
        self._error_msg = "Auto did not work: {}"

    @staticmethod
    def _version_str2tup(version_str):
        version_tup = []
        for e_raw in (e for e in version_str.strip().replace(".", "")):
            try:
                e_ok = int(e_raw)
            except ValueError:
                e_ok = str(e_raw)
            version_tup.append(e_ok)
        return tuple(version_tup)

    @staticmethod
    def _version_tup2str(version_tup):
        version_list = []
        dot_count = 0
        dot_threshold = 2
        for e in version_tup:
            e = str(e)
            if e.isdigit() and dot_count < dot_threshold:
                version_list.append(f"{e}.")
                dot_count += 1
            elif e.isdigit() and dot_count >= dot_threshold:
                version_list.append(e)
                dot_count += 1
            else:
                version_list.append(e)
        return "".join(version_list)

    def _get_version(self):
        completed_process = subprocess.run(
            self.version_cmd, capture_output=True, encoding="utf8"
        )
        match = self.version_rgx.search(completed_process.stdout)
        if match:
            return self._version_str2tup(match.group(1))
        else:
            msg = (
                "could not identify Poetry version "
                f"from stdout {completed_process.stdout!r}."
            )
            self._raise_err(msg)

    def assert_poetry_version(self):
        current_version = self._get_version()
        if current_version >= self.ok_version:
            return
        else:
            current_version_str = self._version_tup2str(current_version)
            ok_version_str = self._version_tup2str(self.ok_version)
            msg = (
                f"Poetry is the wrong version: you have {current_version_str} but "
                f"need {ok_version_str} or newer."
            )
            self._raise_err(msg)

    def get_envs(self):
        self.assert_poetry_version()
        completed_process = subprocess.run(
            self.cmd, capture_output=True, encoding="utf8"
        )
        envs = completed_process.stdout.splitlines()
        return envs

    def get_active_env(self):
        envs = self.get_envs()
        for env in envs:
            if self.active_token in env:
                active_env = env
                break
        else:
            msg = "Poetry has no active env."
            self._raise_err(msg)
        active_env = active_env.replace(self.active_token, "").strip()
        active_env = pathlib.Path(active_env)
        if not active_env.exists():
            msg = f"could not find path to active env {str(active_env)!r}."
            self._raise_err(msg)
        return active_env

    def _raise_err(self, msg):
        formatted = self._error_msg.format(msg)
        raise RuntimeError(formatted)


def clear_env_directories():
    patterns = [VENV_SYMLINK, "virtualenv"]
    cwd = pathlib.Path.cwd()
    matches = (match for pat in patterns for match in cwd.glob(pat))
    for match in matches:
        if match.is_dir():
            if match.is_symlink():
                match.unlink()
            else:
                shutil.rmtree(match)
        else:
            match.unlink()
    return


def generate_link_path():
    cwd = pathlib.Path.cwd()
    return cwd.joinpath(VENV_SYMLINK)


def create_link_to_poetry_env(env):
    cwd = pathlib.Path.cwd()
    link = cwd.joinpath(VENV_SYMLINK)
    link.symlink_to(env)
    return


def validate_symlink(expected_target):
    link = generate_link_path()
    base = [
        f"Base directory: {str(link.parent)!r}",
        f"Symlink name: {link.name!r}",
        f"Target directory: {str(expected_target)!r}",
    ]
    flag_exist = link.exists()
    flag_is_dir = link.is_dir()
    flag_is_sym = link.is_symlink()
    resolved_target = link.resolve()
    flag_resolved_target = (resolved_target.name == expected_target.name) and (
        resolved_target.parent.name == expected_target.parent.name
    )
    if all([flag_exist, flag_is_dir, flag_is_sym, flag_resolved_target]):
        detail = ["OK!"]
    else:
        detail = [
            "NOT OK!",
            f"Exists? {flag_exist}",
            f"Is a symlink? {flag_is_sym}",
            f"Is a directory? {flag_is_dir}",
            f"Good target? {flag_resolved_target}",
        ]
    msg = "\n".join(base + detail)
    return msg


def main(poetry_env):
    if poetry_env == AUTOMATIC_DISCOVERY:
        pet = PoetryEnvTool()
        poetry_env = pet.get_active_env()
    clear_env_directories()
    create_link_to_poetry_env(poetry_env)
    msg = validate_symlink(poetry_env)
    print(msg)
    return


if __name__ == "__main__":
    argparser = ScriptArgParser()
    kwargs = argparser.get_args()
    main(**kwargs)
