import logging
import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena_common.commands import WorkingDirectory
from turingarena_impl.cli_server.git_manager import GitManager


@contextmanager
def enter_working_directory(working_directory: WorkingDirectory, *, local_execution):
    with create_working_directory(working_directory, local_execution=local_execution) as work_dir:
        old_cwd = os.curdir

        os.chdir(work_dir)
        os.chdir(working_directory.current_directory)

        yield

        os.chdir(old_cwd)


@contextmanager
def create_working_directory(working_directory: WorkingDirectory, *, local_execution):
    git = GitManager(local_execution.git_dir)
    git.init()

    with TemporaryDirectory() as temp_dir:
        logging.info(f"Created temporary git working dir {temp_dir}")

        for r in working_directory.pack.repositories:
            git.fetch_repository({
                "type": "git_clone",
                "url": r.url,
                "branch": r.branch,
                "depth": r.depth,
            })

        git.checkout_trees(working_directory.pack.parts, temp_dir)
        yield temp_dir