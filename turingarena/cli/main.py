from turingarena.cli import docopt_cli
from turingarena.cli.loggerinit import init_logger
from turingarena.container.cli import container_cli
from turingarena.interface.cli import generate_metadata_cli, generate_template_cli, generate_skeleton_cli
from turingarena.problem.cli import evaluate_cli
from turingarena.tests.cli import test_cli


@docopt_cli
def main(args):
    """TuringArena command line interface.

    Usage:
      turingarena [options] <cmd> [<args>]...

    Options:
      --log-level=<level>  Set logging level.
    """
    init_logger(args)

    commands = {
        "container": container_cli,
        "evaluate": evaluate_cli,
        "template": generate_template_cli,
        "skeleton": generate_skeleton_cli,
        "metadata": generate_metadata_cli,
        "test": test_cli,
    }
    argv2 = args["<args>"]
    commands[args["<cmd>"]](argv2)


if __name__ == '__main__':
    main()
