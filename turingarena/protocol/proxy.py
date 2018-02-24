import threading
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.protocol.driver.client import DriverClient
from turingarena.sandbox.client import SandboxClient
from turingarena.sandbox.server import SandboxServer


class ProxiedAlgorithm:
    def __init__(self, *, algorithm_dir, interface):
        self.algorithm_dir = algorithm_dir
        self.interface = interface

    @contextmanager
    def run(self, **global_variables):
        with TemporaryDirectory("sandbox_server_") as server_dir:
            server = SandboxServer(server_dir)
            client = SandboxClient(server_dir)

            server_thread = threading.Thread(target=server.run)
            server_thread.start()

            with client.run(self.algorithm_dir) as process:
                with DriverClient().run(interface=self.interface, process=process) as engine:
                    engine.begin_main(**global_variables)
                    proxy = Proxy(engine=engine)
                    yield process, proxy
                    engine.end_main()
            server.stop()
            server_thread.join()


class Proxy:
    def __init__(self, engine):
        self._engine = engine

    def __getattr__(self, item):
        try:
            self._engine.interface_signature.functions[item]
        except KeyError:
            raise AttributeError

        def method(*args, **kwargs):
            return self._engine.call(item, args=args, callbacks_impl=kwargs)

        return method
