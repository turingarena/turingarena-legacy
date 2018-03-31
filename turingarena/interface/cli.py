import json
import sys

from turingarena.cli import docopt_cli
from turingarena.common import write_to_file
from turingarena.interface.interface import InterfaceDefinition
from turingarena.interface.skeleton.common import CodeGen
from turingarena.problem.problem import load_problem


@docopt_cli
def generate_template_cli(args):
    """Generate interface template code.

    Usage:
        template [options]

    Options:
        -x --language=<lang>  Source language [default: c++].
        -I --interface=<file>  Interface definition file [default: interface.txt].
    """

    with open(args["--interface"]) as f:
        interface_text = f.read()

    interface = InterfaceDefinition.compile(interface_text)
    generator = CodeGen.get_template_generator(args["--language"])(interface)
    write_to_file(generator.generate(), sys.stdout)


@docopt_cli
def generate_skeleton_cli(args):
    """Generate interface skeleton code (for debugging).

    Usage:
        skeleton [options]

    Options:
        -x --language=<lang>  Source language [default: c++].
        -I --interface=<file>  Interface definition file [default: interface.txt].
    """

    with open(args["--interface"]) as f:
        interface_text = f.read()

    interface = InterfaceDefinition.compile(interface_text)
    generator = CodeGen.get_skeleton_generator(args["--language"])(interface)
    write_to_file(generator.generate(), sys.stdout)


@docopt_cli
def validate_interface_cli(args):
    """Validate interface file

    Usage:
        validate [options]

    Options:
        -I --interface=<file>  Interface definition file [default: interface.txt].
    """

    with open(args["--interface"]) as f:
        interface_text = f.read()

    interface = InterfaceDefinition.compile(interface_text)

    for message in interface.validate():
        print(message)


@docopt_cli
def generate_metadata_cli(args):
    """Generate interface metadata.

    Usage:
        metadata [options]

    Options:
        -p --problem=<problem>  Problem [default: .].
    """

    problem = load_problem(args["--problem"])
    print(json.dumps(problem.metadata, indent=4))
