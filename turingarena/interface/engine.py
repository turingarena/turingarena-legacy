import itertools
import logging

from turingarena.interface.driver.commands import ProxyRequest
from turingarena.interface.driver.connection import DRIVER_PROCESS_QUEUE
from turingarena.interface.frames import Frame
from turingarena.pipeboundary import PipeBoundary

logger = logging.getLogger(__name__)


def drive_interface(*, interface, driver_boundary: PipeBoundary, sandbox_connection):
    global_frame = Frame(
        global_frame=None,  # FIXME: use a different class for global frame ?
        scope=interface.body.scope,
        parent=None,
        record=None,
        interface=interface,
    )

    # maintain two "instruction pointers" in the form of paraller iterators
    # over the same sequence of instructions (see itertools.tee).
    # driver_iterator is for handling driver requests (main begin/end, function call, callback return and exit)
    # sandbox_iterator is for communicating with sandbox (input/output)
    driver_iterator, sandbox_iterator = itertools.tee(
        interface.unroll(frame=global_frame)
    )

    # a generator that executes the instructions in sandbox_iterator
    # and yields exactly once per communication block
    # (once for each yield instruction, and once at the end)
    run_sandbox_iterator = run_sandbox(sandbox_iterator, sandbox_connection=sandbox_connection)

    # a generator that receives driver requests
    # and yields responses
    run_driver_iterator = run_driver(driver_iterator, run_sandbox_iterator=run_sandbox_iterator)

    def handler(request):
        logger.debug(f"handling driver request {request!s:.50}")
        current_request = ProxyRequest.deserialize(
            iter(request.splitlines()),
            interface_signature=interface.signature,
        )

        response = run_driver_iterator.send(current_request)

        logger.debug(f"handling driver request {request!s:.10} with response {response!s:.50}")

        assert all(isinstance(x, int) for x in response)
        return {
            "response": "\n".join(str(x) for x in response)
        }

    assert next(run_driver_iterator) is None
    while True:
        logger.debug(f"waiting for driver request...")
        driver_boundary.handle_request(DRIVER_PROCESS_QUEUE, handler)
        try:
            assert next(run_driver_iterator) is None
        except StopIteration:
            break


def run_driver(driver_iterator, *, run_sandbox_iterator):
    current_request = None
    input_sent = False

    for instruction in driver_iterator:
        logger.debug(f"about to execute with driver {instruction!r:.50}")

        if current_request is None:
            current_request = yield
            assert current_request is not None

        logger.debug(f"executing with driver {instruction!r:.50}")

        instruction.run_driver_pre(current_request)
        if instruction.should_send_input() and not input_sent:
            # advance fully the current communication block
            next(run_sandbox_iterator)
            input_sent = True

        response = instruction.run_driver_post()
        if response is not None:
            assert (yield response) is None
            current_request = None

        if instruction.is_flush():
            assert input_sent
            input_sent = False

    assert input_sent


def send_response(driver_connection, response):
    for item in response:
        assert isinstance(item, (int, bool))
        print(int(item), file=driver_connection.response)
    driver_connection.response.flush()


def run_sandbox(instructions, *, sandbox_connection):
    for instruction in instructions:
        logger.debug(f"executing with SANDBOX {instruction!r:.200}")
        instruction.run_sandbox(sandbox_connection)
        if instruction.is_flush():
            yield
    yield