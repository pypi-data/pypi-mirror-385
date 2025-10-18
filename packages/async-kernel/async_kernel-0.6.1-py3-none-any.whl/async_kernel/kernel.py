from __future__ import annotations

import asyncio
import atexit
import builtins
import contextlib
import errno
import functools
import getpass
import importlib.util
import json
import logging
import math
import os
import pathlib
import signal
import sys
import threading
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from logging import Logger, LoggerAdapter
from pathlib import Path
from types import CoroutineType
from typing import TYPE_CHECKING, Any, Literal, Self

import anyio
import IPython.core.completer
import sniffio
import traitlets
import zmq
from IPython.core.error import StdinNotImplementedError
from IPython.utils.tokenutil import token_at_cursor
from jupyter_client import write_connection_file
from jupyter_client.localinterfaces import localhost
from jupyter_client.session import Session
from jupyter_core.paths import jupyter_runtime_dir
from traitlets import CaselessStrEnum, Dict, HasTraits, Instance, Set, Tuple, Unicode, UseEnum
from typing_extensions import override
from zmq import Context, Flag, PollEvent, Socket, SocketOption, SocketType, ZMQError

import async_kernel
from async_kernel import AsyncEvent, Caller, utils
from async_kernel.asyncshell import AsyncInteractiveShell
from async_kernel.debugger import Debugger
from async_kernel.iostream import OutStream
from async_kernel.kernelspec import Backend, KernelName
from async_kernel.typing import (
    Content,
    ExecuteContent,
    HandlerType,
    Job,
    KernelConcurrencyMode,
    Message,
    MsgType,
    NoValue,
    RunMode,
    SocketID,
    Tags,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Generator, Iterable
    from types import CoroutineType, FrameType

    from IPython.core.interactiveshell import ExecutionResult

    from async_kernel.comm import CommManager


__all__ = ["Kernel", "KernelInterruptError"]


def error_to_content(error: BaseException, /) -> Content:
    """
    Convert the error to a dict.

    ref: https://jupyter-client.readthedocs.io/en/stable/messaging.html#request-reply
    """
    return {
        "status": "error",
        "ename": type(error).__name__,
        "evalue": str(error),
        "traceback": traceback.format_exception(error),
    }


def bind_socket(
    socket: Socket[SocketType],
    transport: Literal["tcp", "ipc"],
    ip: str,
    port: int = 0,
    max_attempts: int | NoValue = NoValue,  # pyright: ignore[reportInvalidTypeForm]
) -> int:
    """
    Bind the socket to a port using the settings.

    max_attempts: The maximum number of attempts to bind the socket. If un-specified,
    defaults to 100 if port missing, else 2 attempts.
    """
    if socket.TYPE == SocketType.ROUTER:
        # ref: https://github.com/ipython/ipykernel/issues/270
        socket.router_handover = 1
    if transport == "ipc":
        ip = Path(ip).as_posix()
    if max_attempts is NoValue:
        max_attempts = 2 if port else 100
    for attempt in range(max_attempts):
        try:
            if transport == "tcp":
                if not port:
                    port = socket.bind_to_random_port(f"tcp://{ip}")
                else:
                    socket.bind(f"tcp://{ip}:{port}")
            elif transport == "ipc":
                if not port:
                    port = 1
                    while Path(f"{ip}-{port}").exists():
                        port += 1
                socket.bind(f"ipc://{ip}-{port}")
            else:
                msg = f"Invalid transport: {transport}"  # pyright: ignore[reportUnreachable]
                raise ValueError(msg)
        except ZMQError as e:
            if e.errno not in {errno.EADDRINUSE, 98, 10048, 135}:
                raise
            if port and attempt < max_attempts - 1:
                time.sleep(0.1)
        else:
            return port
    msg = f"Failed to bind {socket} for {transport=} after {max_attempts} attempts."
    raise RuntimeError(msg)


@functools.cache
def _wrap_handler(
    runner: Callable[[HandlerType, Job]], handler: HandlerType
) -> Callable[[Job], CoroutineType[Any, Any, None]]:
    """
    A cache of run handlers.

    Args:
        runner: The function that calls and awaits the handler
        handler: The handler to which the runner is associated.

    Used by:
        - call[async_kernel.Kernel.handle_message_request][]
    """

    @functools.wraps(handler)
    async def wrap_handler(job: Job) -> None:
        await runner(handler, job)

    return wrap_handler


class KernelInterruptError(InterruptedError):
    "Raised to interrupt the kernel."

    # We subclass from InterruptedError so if the backend is a SelectorEventLoop it can catch the exception.
    # Other event loops don't appear to have this issue.


class Kernel(HasTraits):
    """
    An asynchronous kernel with an anyio backend providing an IPython AsyncInteractiveShell with zmq sockets.

    Only one instance will be created/run at a time. The instance can be obtained with `Kernel()` or [async_kernel.utils.get_kernel].

    To start the kernel:


    === "Shell"

        At the command prompt.

        ``` shell
        async-kernel -f .
        ```

        See also:

        -

    === "Normal"

        ```python
        from async_kernel.__main__ import main

        main()
        ```

    === "start (`classmethod`)"

        ```python
        Kernel.start()
        ```

    === "Asynchronously inside anyio event loop"

        ```python
        kernel = Kernel()
        async with kernel:
            await anyio.sleep_forever()
        ```

        ???+ tip

            This is a convenient way to start a kernel for debugging.

    Origins: [IPyKernel Kernel][ipykernel.kernelbase.Kernel], [IPyKernel IPKernelApp][ipykernel.kernelapp.IPKernelApp] &  [IPyKernel IPythonKernel][ipykernel.ipkernel.IPythonKernel]
    """

    _instance: Self | None = None
    _initialised = False
    _interrupt_requested = False
    _last_interrupt_frame = None
    _stop_on_error_time: float = 0
    _interrupts: traitlets.Container[set[Callable[[], object]]] = Set()
    _settings: Dict[str, Any] = Dict()
    _sockets: Dict[SocketID, zmq.Socket] = Dict()
    _ports: Dict[SocketID, int] = Dict()
    _execution_count = traitlets.Int(0)
    anyio_backend = UseEnum(Backend)
    ""
    anyio_backend_options: Dict[Backend, dict[str, Any] | None] = Dict(allow_none=True)
    "Default options to use with [anyio.run][]. See also: `Kernel.handle_message_request`"

    concurrency_mode = UseEnum(KernelConcurrencyMode)
    """
    The mode to use when getting the run mode for running the handler of a message request.
    
    See also:
        - [async_kernel.Kernel.handle_message_request][]
    """
    help_links = Tuple()
    ""
    quiet = traitlets.Bool(True)
    "Only send stdout/stderr to output stream"
    connection_file: traitlets.TraitType[Path, Path | str] = traitlets.TraitType()
    """
    JSON file in which to store connection info [default: kernel-<pid>.json]

    This file will contain the IP, ports, and authentication key needed to connect
    clients to this kernel. By default, this file will be created in the security dir
    of the current profile, but can be specified by absolute path.
    """
    kernel_name: str | Unicode = Unicode()
    "The kernels name - if it contains 'trio' a trio backend will be used instead of an asyncio backend."

    ip = Unicode()
    """
    The kernel's IP address [default localhost].
    
    If the IP address is something other than localhost, then Consoles on other machines 
    will be able to connect to the Kernel, so be careful!"""
    log = Instance(logging.LoggerAdapter)
    ""
    shell = Instance(AsyncInteractiveShell, ())
    ""
    session = Instance(Session, ())
    ""
    debugger = Instance(Debugger, ())
    ""
    comm_manager: Instance[CommManager] = Instance("async_kernel.comm.CommManager")
    ""
    transport: CaselessStrEnum[str] = CaselessStrEnum(
        ["tcp", "ipc"] if sys.platform == "linux" else ["tcp"], default_value="tcp", config=True
    )
    event_started = Instance(AsyncEvent, (), read_only=True)
    "An event that occurs when the kernel is started."
    event_stopped = Instance(AsyncEvent, (), read_only=True)
    "An event that occurs when the kernel is stopped."

    def load_connection_info(self, info: dict[str, Any]) -> None:
        """
        Load connection info from a dict containing connection info.

        Typically this data comes from a connection file
        and is called by load_connection_file.

        Args:
            info: Dictionary containing connection_info. See the connection_file spec for details.
        """
        if self._ports:
            msg = "Connection info is already loaded!"
            raise RuntimeError(msg)
        self.transport = info.get("transport", self.transport)
        self.ip = info.get("ip") or self.ip
        for socket in SocketID:
            name = f"{socket}_port"
            if socket not in self._ports and name in info:
                self._ports[socket] = info[name]
        if "key" in info:
            key = info["key"]
            if isinstance(key, str):
                key = key.encode()
            assert isinstance(key, bytes)

            self.session.key = key
        if "signature_scheme" in info:
            self.session.signature_scheme = info["signature_scheme"]

    def __new__(cls, settings: dict | None = None, /) -> Self:  # noqa: ARG004
        #  There is only one instance (including subclasses).
        if not (instance := Kernel._instance):
            Kernel._instance = instance = super().__new__(cls)
        return instance  # pyright: ignore[reportReturnType]

    def __init__(self, settings: dict | None = None, /) -> None:
        if self._initialised:
            return  # Only initialize once
        assert threading.current_thread() is threading.main_thread(), "The kernel must start in the main thread."
        self._initialised = True
        super().__init__()
        sys.excepthook = self.excepthook
        sys.unraisablehook = self.unraisablehook
        signal.signal(signal.SIGINT, self._signal_handler)
        if not os.environ.get("MPLBACKEND"):
            os.environ["MPLBACKEND"] = "module://matplotlib_inline.backend_inline"
        # setting get loaded in `_validate_settings`
        self._settings = settings or {}

    @override
    def __repr__(self) -> str:
        info = [f"{k}={v}" for k, v in self.settings.items()]
        return f"{self.__class__.__name__}<{', '.join(info)}>"

    async def __aenter__(self) -> Self:
        """
        Start the kernel.

        - Only one instance can (should) run at a time.
        - An instance can only be started once.
        - A new instance can be started after a previous instance has stopped.

        !!! example

            ```python
            async with Kerne() as kernel:
                await anyio.sleep_forever()
            ```
        """
        async with contextlib.AsyncExitStack() as stack:
            self._running = True
            await stack.enter_async_context(self._start_in_context())
            self.__stack = stack.pop_all()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> None:
        await self.__stack.__aexit__(exc_type, exc_value, exc_tb)

    @traitlets.default("log")
    def _default_log(self) -> LoggerAdapter[Logger]:
        return logging.LoggerAdapter(logging.getLogger(self.__class__.__name__))

    @traitlets.default("kernel_name")
    def _default_kernel_name(self) -> Literal[KernelName.trio, KernelName.asyncio]:
        try:
            if sniffio.current_async_library() == "trio":
                return KernelName.trio
        except Exception:
            pass
        return KernelName.asyncio

    @traitlets.default("connection_file")
    def _default_connection_file(self) -> Path:
        return Path(jupyter_runtime_dir()).joinpath(f"kernel-{uuid.uuid4()}.json")

    @traitlets.default("comm_manager")
    def _default_comm_manager(self) -> CommManager:
        from async_kernel import comm  # noqa: PLC0415

        comm.set_comm()
        return comm.get_comm_manager()

    @traitlets.default("shell")
    def _default_shell(self) -> AsyncInteractiveShell:
        return AsyncInteractiveShell.instance()

    @traitlets.default("anyio_backend_options")
    def _default_anyio_backend_options(self):
        return {Backend.asyncio: {"use_uvloop": True} if importlib.util.find_spec("uvloop") else {}, Backend.trio: None}

    @traitlets.default("ip")
    def _default_ip(self) -> str:
        return str(self.connection_file) + "-ipc" if self.transport == "ipc" else localhost()

    @traitlets.default("help_links")
    def _default_help_links(self) -> tuple[dict[str, str], ...]:
        return (
            {
                "text": "Async Kernel Reference ",
                "url": "TODO",
            },
            {
                "text": "IPython Reference",
                "url": "https://ipython.readthedocs.io/en/stable/",
            },
            {
                "text": "IPython magic Reference",
                "url": "https://ipython.readthedocs.io/en/stable/interactive/magics.html",
            },
            {
                "text": "Matplotlib ipympl Reference",
                "url": "https://matplotlib.org/ipympl/",
            },
            {
                "text": "Matplotlib Reference",
                "url": "https://matplotlib.org/contents.html",
            },
        )

    @traitlets.observe("connection_file")
    def _observe_connection_file(self, change) -> None:
        if not self._ports and (path := self.connection_file).exists():
            self.log.debug("Loading connection file %s", path)
            with path.open("r") as f:
                self.load_connection_info(json.load(f))

    @traitlets.validate("ip")
    def _validate_ip(self, proposal) -> str:
        return "0.0.0.0" if (val := proposal["value"]) == "*" else val

    @traitlets.validate("connection_file")
    def _validate_connection_file(self, proposal) -> Path:
        return pathlib.Path(proposal.value)

    @traitlets.validate("_settings")
    def _validate_settings(self, proposal) -> dict[str, Any]:
        settings = self._settings or {"kernel_name": self.kernel_name}
        for k, v in proposal.value.items():
            settings |= utils.setattr_nested(self, k, v)
        return settings

    @property
    def settings(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in ("kernel_name", "connection_file")} | self._settings

    @property
    def execution_count(self) -> int:
        "The execution count in context of the current coroutine, else the current value if there isn't one in context."
        return utils.get_execution_count()

    @property
    def kernel_info(self) -> dict[str, str | dict[str, str | dict[str, str | int]] | Any | tuple[Any, ...] | bool]:
        return {
            "protocol_version": async_kernel.kernel_protocol_version,
            "implementation": "async_kernel",
            "implementation_version": async_kernel.__version__,
            "language_info": async_kernel.kernel_protocol_version_info,
            "banner": self.shell.banner,
            "help_links": self.help_links,
            "debugger": not utils.LAUNCHED_BY_DEBUGPY,
            "kernel_name": self.kernel_name,
        }

    @staticmethod
    def stop() -> None:
        """
        Stop the running kernel.

        Once a kernel is stopped; that instance of the kernel cannot be restarted.
        Instead, a new kernel must be started.
        """
        if instance := Kernel._instance:
            Kernel._instance = None
            instance.event_stopped.set()

    @asynccontextmanager
    async def _start_in_context(self) -> AsyncGenerator[Self, Any]:
        """Start the kernel in an already running anyio event loop."""
        if self._sockets:
            msg = "Already started"
            raise RuntimeError(msg)
        assert self.shell
        self.anyio_backend = sniffio.current_async_library()
        try:
            async with Caller(log=self.log, create=True, protected=True) as caller:
                caller.call_soon(self._wait_stopped)
                try:
                    await self._start_heartbeat()
                    await self._start_iopub_proxy()
                    await self._start_control_loop()
                    await self._start_main_loop()
                    assert len(self._sockets) == len(SocketID)
                    self._write_connection_file()
                    print(f"Kernel started: {self!r}")
                    with self._iopub():
                        self.event_started.set()
                        self.comm_manager.kernel = self
                        yield self
                finally:
                    self.comm_manager.kernel = None
                    self.stop()
        finally:
            AsyncInteractiveShell.clear_instance()
            Context.instance().term()
            print(f"Kernel stopped: {self!r}")

    def _signal_handler(self, signum, frame: FrameType | None) -> None:
        "Handle interrupt signals."
        if self._interrupt_requested:
            self._interrupt_requested = False
            if frame and frame.f_locals is self.shell.user_ns:
                raise KernelInterruptError
            if self._last_interrupt_frame is frame:
                # A blocking call that is not an execute_request
                raise KernelInterruptError
            self._last_interrupt_frame = frame
        else:
            signal.default_int_handler(signum, frame)

    @contextlib.contextmanager
    def _bind_socket(self, socket_id: SocketID, socket: zmq.Socket) -> Generator[None, Any, None]:
        """
        Bind a zmq.Socket storing a reference to the socket and the port
        details and closing the socket on leaving the context."""
        if socket_id in self._sockets:
            msg = f"{socket_id=} is already loaded"
            raise RuntimeError(msg)
        socket.linger = 500
        port = bind_socket(socket=socket, transport=self.transport, ip=self.ip, port=self._ports.get(socket_id, 0))  # pyright: ignore[reportArgumentType]
        self._ports[socket_id] = port
        self.log.debug("%s socket on port: %i", socket_id, port)
        self._sockets[socket_id] = socket
        try:
            yield
        finally:
            socket.close(linger=500)
            self._sockets.pop(socket_id)

    def _write_connection_file(self) -> None:
        """Write connection info to JSON dict in self.connection_file."""
        if not (path := self.connection_file).exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            write_connection_file(
                str(path),
                transport=self.transport,
                ip=self.ip,
                key=self.session.key,
                signature_scheme=self.session.signature_scheme,
                kernel_name=self.kernel_name,
                **{f"{socket_id}_port": self._ports[socket_id] for socket_id in SocketID},
            )
            ip_files: list[pathlib.Path] = []
            if self.transport == "ipc":
                for s in self._sockets.values():
                    f = pathlib.Path(s.get_string(zmq.LAST_ENDPOINT).removeprefix("ipc://"))
                    assert f.exists()
                    ip_files.append(f)

            def cleanup_file_files() -> None:
                path.unlink(missing_ok=True)
                for f in ip_files:
                    f.unlink(missing_ok=True)

            atexit.register(cleanup_file_files)

    def _input_request(self, prompt: str, *, password=False) -> Any:
        job = utils.get_job()
        if not job["msg"].get("content", {}).get("allow_stdin", False):
            msg = "Stdin is not allowed in this context!"
            raise StdinNotImplementedError(msg)
        socket = self._sockets[SocketID.stdin]
        # Clear messages on the stdin socket
        while socket.get(SocketOption.EVENTS) & PollEvent.POLLIN:  # pyright: ignore[reportOperatorIssue]
            socket.recv_multipart(flags=Flag.DONTWAIT, copy=False)
        # Send the input request.
        assert self is not None
        self.session.send(
            stream=socket,
            msg_or_type="input_request",
            content={"prompt": prompt, "password": password},
            parent=job["msg"],  # pyright: ignore[reportArgumentType]
            ident=job["ident"],
        )
        # Poll for a reply.
        while not (socket.poll(100) & PollEvent.POLLIN):
            if self._last_interrupt_frame:
                raise KernelInterruptError
        return self.session.recv(socket)[1]["content"]["value"]  # pyright: ignore[reportOptionalSubscript]

    async def _wait_stopped(self) -> None:
        try:
            await self.event_stopped.wait()
            if self.debugger.debugpy_client.connected:
                await self.control_thread_caller.call_soon(self.debugger.disconnect)
        except BaseException:
            with anyio.CancelScope(shield=True):
                self.event_stopped.set()
                await anyio.sleep(0)
            raise
        finally:
            Caller.stop_all(_stop_protected=True)

    async def _start_heartbeat(self) -> None:
        # Reference: https://jupyter-client.readthedocs.io/en/stable/messaging.html#heartbeat-for-kernels

        def heartbeat():
            socket: Socket = Context.instance().socket(zmq.ROUTER)
            with utils.do_not_debug_this_thread(), self._bind_socket(SocketID.heartbeat, socket):
                ready_event.set()
                try:
                    zmq.proxy(socket, socket)
                except zmq.ContextTerminated:
                    return

        ready_event = AsyncEvent()
        heartbeat_thread = threading.Thread(target=heartbeat, name="heartbeat", daemon=True)
        heartbeat_thread.start()
        await ready_event.wait()

    async def _start_iopub_proxy(self) -> None:
        """Provide an io proxy."""

        def pub_proxy():
            # We use an internal proxy to collect pub messages for distribution.
            # Each thread needs to open its own socket to publish to the internal proxy.
            # When thread-safe sockets become available, this could be changed...
            # Ref: https://zguide.zeromq.org/docs/chapter2/#Working-with-Messages (fig 14)
            frontend: zmq.Socket = Context.instance().socket(zmq.XSUB)
            frontend.bind(Caller.iopub_url)
            iopub_socket: zmq.Socket = Context.instance().socket(zmq.XPUB)
            with utils.do_not_debug_this_thread(), self._bind_socket(SocketID.iopub, iopub_socket):
                ready_event.set()
                try:
                    zmq.proxy(frontend, iopub_socket)
                except zmq.ContextTerminated:
                    frontend.close(linger=500)

        ready_event = AsyncEvent()
        iopub_thread = threading.Thread(target=pub_proxy, name="iopub proxy", daemon=True)
        iopub_thread.start()
        await ready_event.wait()

    @contextlib.contextmanager
    def _iopub(self):
        # Save IO
        self._original_io = sys.stdout, sys.stderr, sys.displayhook, builtins.input, self.getpass

        builtins.input = self.raw_input
        getpass.getpass = self.getpass
        for name in ["stdout", "stderr"]:

            def flusher(string: str, name=name):
                "Publish stdio or stderr when flush is called"
                self.iopub_send(
                    msg_or_type="stream",
                    content={"name": name, "text": string},
                    ident=f"stream.{name}".encode(),
                )
                if not self.quiet and (echo := (sys.__stdout__ if name == "stdout" else sys.__stderr__)):
                    echo.write(string)
                    echo.flush()

            wrapper = OutStream(flusher=flusher)
            setattr(sys, name, wrapper)
        try:
            yield
        finally:
            # Reset IO
            sys.stdout, sys.stderr, sys.displayhook, builtins.input, getpass.getpass = self._original_io

    async def _start_control_loop(self) -> None:
        self.control_thread_caller = Caller.start_new(backend=self.anyio_backend, name="ControlThread", protected=True)
        ready = AsyncEvent()
        self.control_thread_caller.call_soon(self._receive_msg_loop, SocketID.control, ready.set)
        await ready.wait()

    async def _start_main_loop(self):
        async def run_in_main_event_loop():
            stdin_socket = Context.instance().socket(SocketType.ROUTER)
            with self._bind_socket(SocketID.stdin, stdin_socket):
                await self._receive_msg_loop(SocketID.shell, ready.set)

        ready = AsyncEvent()
        Caller().call_soon(run_in_main_event_loop)
        await ready.wait()

    async def _receive_msg_loop(
        self, socket_id: Literal[SocketID.control, SocketID.shell], started: Callable[[], None]
    ) -> None:
        """Receive shell and control messages over zmq sockets."""
        if (
            sys.platform == "win32"
            and self.anyio_backend is Backend.asyncio
            and isinstance(asyncio.get_running_loop(), asyncio.ProactorEventLoop)
        ):
            from anyio._core._asyncio_selector_thread import get_selector  # noqa: PLC0415

            utils.mark_thread_pydev_do_not_trace(get_selector()._thread)  # pyright: ignore[reportPrivateUsage]
        socket: Socket[Literal[SocketType.ROUTER]] = Context.instance().socket(SocketType.ROUTER)
        with self._bind_socket(socket_id, socket), contextlib.suppress(anyio.get_cancelled_exc_class()):
            started()
            while True:
                while socket.get(SocketOption.EVENTS) & PollEvent.POLLIN:  # pyright: ignore[reportOperatorIssue]
                    try:
                        ident, msg = self.session.recv(socket, copy=False)
                        if ident and msg:
                            if socket_id == SocketID.shell:
                                # Reset the frame to show the main thread is not blocked.
                                self._last_interrupt_frame = None
                            self.log.debug("*** _receive_msg_loop %s*** %s", socket_id, msg)
                            await self.handle_message_request(
                                Job(
                                    socket_id=socket_id,
                                    socket=socket,
                                    ident=ident,
                                    msg=msg,  # pyright: ignore[reportArgumentType]
                                    received_time=time.monotonic(),
                                    run_mode=None,  #  pyright: ignore[reportArgumentType]. This value is set by `get_handler_and_run_mode`.
                                )
                            )
                    except Exception as e:
                        self.log.debug("Bad message on %s: %s", socket_id, e)
                        continue
                    await anyio.sleep(0)
                await anyio.wait_readable(socket)

    async def handle_message_request(self, job: Job, /) -> None:
        """
        The main handler for all shell and control messages.

        Args:
            job: The packed [message][async_kernel.typing.Message] for handling.
        """
        try:
            msg_type = MsgType(job["msg"]["header"]["msg_type"])
            socket_id = job["socket_id"]
            handler = self.get_handler(msg_type)
        except (ValueError, TypeError):
            self.log.debug("Invalid job %s", job)
            return
        run_mode = self.get_run_mode(msg_type, socket_id=socket_id, job=job)
        self.log.debug("%s  %s run mode %s handler: %s", socket_id, msg_type, run_mode, handler)
        job["run_mode"] = run_mode
        runner = _wrap_handler(self.run_handler, handler)
        match run_mode:
            case RunMode.queue:
                Caller().queue_call(runner, job)
            case RunMode.thread:
                Caller.to_thread(runner, job)
            case RunMode.task:
                Caller().call_soon(runner, job)
            case RunMode.blocking:
                await runner(job)

    def get_run_mode(
        self,
        msg_type: MsgType,
        *,
        socket_id: Literal[SocketID.shell, SocketID.control] = SocketID.shell,
        concurrency_mode: KernelConcurrencyMode | NoValue = NoValue,  # pyright: ignore[reportInvalidTypeForm]
        job: Job | None = None,
    ) -> RunMode:
        """
        Determine the run mode for a given channel, message type and concurrency mode.

        The run mode determines how the kernel will execute the message.

        Args:
            socket_id: The socket ID the message was received on.
            msg_type: The type of the message.
            concurrency_mode: The concurrency mode of the kernel. Defaults to [kernel.concurrency_mode][async_kernel.Kernel.concurrency_mode]
            job: The job associated with the message, if any.

        Returns:
            The run mode for the message.

        Raises:
            ValueError: If a shutdown or debug request is received on the shell socket.
        """

        concurrency_mode = self.concurrency_mode if concurrency_mode is NoValue else concurrency_mode
        # TODO: Are any of these options worth including?
        # if mode_from_metadata := job["msg"]["metadata"].get("run_mode"):
        #     return RunMode( mode_from_metadata)
        # if mode_from_header := job["msg"]["header"].get("run_mode"):
        #     return RunMode( mode_from_header)
        match (concurrency_mode, socket_id, msg_type):
            case _, SocketID.shell, MsgType.shutdown_request | MsgType.debug_request:
                msg = f"{msg_type=} not allowed on shell!"
                raise ValueError(msg)
            case KernelConcurrencyMode.blocking, _, _:
                return RunMode.blocking
            case _, SocketID.control, MsgType.execute_request:
                return RunMode.task
            case _, _, MsgType.execute_request:
                if job:
                    if content := job["msg"].get("content", {}):
                        if (code := content.get("code")) and (mode_ := RunMode.get_mode(code)):
                            return mode_
                        if content.get("silent"):
                            return RunMode.task
                    if mode_ := set(utils.get_tags(job)).intersection(RunMode):
                        return RunMode(next(iter(mode_)))
                return RunMode.queue
            case _, _, MsgType.inspect_request | MsgType.complete_request | MsgType.is_complete_request:
                return RunMode.thread
            case _, _, MsgType.history_request:
                return RunMode.thread
            case _, _, MsgType.comm_msg:
                return RunMode.queue
            case _, _, MsgType.kernel_info_request | MsgType.comm_info_request | MsgType.comm_open | MsgType.comm_close:
                return RunMode.blocking
            case _, _, MsgType.debug_request:
                return RunMode.blocking
            case _:
                return RunMode.blocking

    def all_concurrency_run_modes(
        self,
        socket_ids: Iterable[Literal[SocketID.shell, SocketID.control]] = (SocketID.shell, SocketID.control),
        msg_types: Iterable[MsgType] = MsgType,
    ) -> dict[
        Literal["SocketID", "KernelConcurrencyMode", "MsgType", "RunMode"],
        tuple[SocketID, KernelConcurrencyMode, MsgType, RunMode | None],
    ]:
        """
        Generates a dictionary containing all combinations of SocketID, KernelConcurrencyMode, and MsgType,
        along with their corresponding RunMode (if available)."""
        data: list[Any] = []
        for socket_id in socket_ids:
            for concurrency_mode in KernelConcurrencyMode:
                for msg_type in msg_types:
                    try:
                        mode = self.get_run_mode(msg_type, socket_id=socket_id, concurrency_mode=concurrency_mode)
                    except ValueError:
                        mode = None
                    data.append((socket_id, concurrency_mode, msg_type, mode))
        data_ = zip(*data, strict=True)
        return dict(zip(["SocketID", "KernelConcurrencyMode", "MsgType", "RunMode"], data_, strict=True))

    def get_handler(self, msg_type: MsgType) -> HandlerType:
        if not callable(f := getattr(self, msg_type, None)):
            msg = f"A handler was not found for {msg_type=}"
            raise TypeError(msg)
        return f  # pyright: ignore[reportReturnType]

    async def run_handler(self, handler: HandlerType, job: Job[dict]) -> None:
        """
        Runs the handler in the context of the job/message sending the reply content if it is provided.

        This method gets called for every valid request with the relevant handler.
        """

        def send_reply(job: Job[dict], content: dict, /) -> None:
            if "status" not in content:
                content["status"] = "ok"
            msg = self.session.send(
                stream=job["socket"],
                msg_or_type=job["msg"]["header"]["msg_type"].replace("request", "reply"),
                content=content,
                parent=job["msg"]["header"],  # pyright: ignore[reportArgumentType]
                ident=job["ident"],
            )
            if msg:
                self.log.debug("*** _send_reply %s*** %s", job["socket_id"], msg)

        token = utils._job_var.set(job)  # pyright: ignore[reportPrivateUsage]
        try:
            self.iopub_send(msg_or_type="status", content={"execution_state": "busy"}, ident=self.topic("status"))
            if (content := await handler(job)) is not None:
                send_reply(job, content)
        except Exception as e:
            send_reply(job, error_to_content(e))
            self.log.exception("Exception in message handler:", exc_info=e)
        finally:
            utils._job_var.reset(token)  # pyright: ignore[reportPrivateUsage]
            self.iopub_send(
                msg_or_type="status", parent=job["msg"], content={"execution_state": "idle"}, ident=self.topic("status")
            )

    def iopub_send(
        self,
        msg_or_type: dict[str, Any] | str,
        content: Content | None = None,
        metadata: dict[str, Any] | None = None,
        parent: dict[str, Any] | None | NoValue = NoValue,  # pyright: ignore[reportInvalidTypeForm]
        ident: bytes | list[bytes] | None = None,
        buffers: list[bytes] | None = None,
    ) -> None:
        """Send a message on the zmq iopub socket."""
        if socket := Caller.iopub_sockets.get(thread := threading.current_thread()):
            msg = self.session.send(
                stream=socket,
                msg_or_type=msg_or_type,
                content=content,
                metadata=metadata,
                parent=parent if parent is not NoValue else utils.get_parent(),  # pyright: ignore[reportArgumentType]
                ident=ident,
                buffers=buffers,
            )
            if msg:
                self.log.debug(
                    "iopub_send: (thread=%s) msg_type:'%s', content: %s", thread.name, msg["msg_type"], msg["content"]
                )
        else:
            self.control_thread_caller.call_direct(
                self.iopub_send,
                msg_or_type=msg_or_type,
                content=content,
                metadata=metadata,
                parent=parent if parent is not NoValue else None,
                ident=ident,
                buffers=buffers,
            )

    def topic(self, topic) -> bytes:
        """prefixed topic for IOPub messages."""
        return (f"kernel.{topic}").encode()

    async def kernel_info_request(self, job: Job[Content], /) -> Content:
        """Handle a [kernel info request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#kernel-info)."""
        return self.kernel_info

    async def comm_info_request(self, job: Job[Content], /) -> Content:
        """Handle a [comm info request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#comm-info)."""
        c = job["msg"]["content"]
        target_name = c.get("target_name", None)
        comms = {
            k: {"target_name": v.target_name}
            for (k, v) in tuple(self.comm_manager.comms.items())
            if v.target_name == target_name or target_name is None
        }
        return {"comms": comms}

    async def execute_request(self, job: Job[ExecuteContent], /) -> Content:
        """Handle a [execute request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#execute)."""
        c = job["msg"]["content"]
        if (
            job["run_mode"] is RunMode.queue
            and (job["received_time"] < self._stop_on_error_time)
            and not c.get("silent", False)
        ):
            self.log.info("Aborting execute_request: %s", job)
            return error_to_content(RuntimeError("Aborting due to prior exception")) | {
                "execution_count": self.execution_count
            }
        metadata = job["msg"].get("metadata") or {}
        if not (silent := c["silent"]):
            self._execution_count += 1
            utils._execution_count_var.set(self._execution_count)  # pyright: ignore[reportPrivateUsage]
            self.iopub_send(
                msg_or_type="execute_input",
                content={"code": c["code"], "execution_count": self.execution_count},
                parent=job["msg"],
                ident=self.topic("execute_input"),
            )
        fut = (Caller.to_thread if job["run_mode"] is RunMode.thread else Caller().call_soon)(
            self.shell.run_cell_async,
            raw_cell=c["code"],
            store_history=c.get("store_history", False),
            silent=silent,
            transformed_cell=self.shell.transform_cell(c["code"]),
            shell_futures=True,
            cell_id=metadata.get("cellId"),
        )
        if not silent:
            self._interrupts.add(fut.cancel)
            fut.add_done_callback(lambda fut: self._interrupts.discard(fut.cancel))
        try:
            result: ExecutionResult = await fut
            err = result.error_before_exec or result.error_in_exec if result else KernelInterruptError()
        except Exception as e:
            # A safeguard to catch exceptions not caught by the shell.
            err = e
        if (err) and (
            (Tags.suppress_error in metadata.get("tags", ()))
            or (isinstance(err, anyio.get_cancelled_exc_class()) and (utils.get_execute_request_timeout() is not None))
        ):
            # Suppress the error due to either:
            # 1. tag
            # 2. timeout
            err = None
        content = {
            "status": "error" if err else "ok",
            "execution_count": self.execution_count,
            "user_expressions": self.shell.user_expressions(c.get("user_expressions", {})),
        }
        if err:
            content |= error_to_content(err)
            if (not silent) and c.get("stop_on_error"):
                try:
                    self._stop_on_error_time = math.inf
                    self.log.info("An error occurred in a non-silent execution request")
                    await anyio.sleep(0)
                finally:
                    self._stop_on_error_time = time.monotonic()
        return content

    async def complete_request(self, job: Job[Content], /) -> Content:
        """Handle a [completion request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#completion)."""
        c = job["msg"]["content"]
        code: str = c["code"]
        cursor_pos = c.get("cursor_pos") or len(code)
        with IPython.core.completer.provisionalcompleter():
            completions = self.shell.Completer.completions(code, cursor_pos)
            completions = list(IPython.core.completer.rectify_completions(code, completions))
        comps = [
            {
                "start": comp.start,
                "end": comp.end,
                "text": comp.text,
                "type": comp.type,
                "signature": comp.signature,
            }
            for comp in completions
        ]
        s, e = completions[0].start, completions[0].end if completions else (cursor_pos, cursor_pos)
        matches = [c.text for c in completions]
        return {
            "matches": matches,
            "cursor_end": e,
            "cursor_start": s,
            "metadata": {"_jupyter_types_experimental": comps},
        }

    async def is_complete_request(self, job: Job[Content], /) -> Content:
        """Handle a [is_complete request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#code-completeness)."""
        status, indent_spaces = self.shell.input_transformer_manager.check_complete(job["msg"]["content"]["code"])
        content = {"status": status}
        if status == "incomplete":
            content["indent"] = " " * indent_spaces
        return content

    async def inspect_request(self, job: Job[Content], /) -> Content:
        """Handle a [inspect request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#introspection)."""
        c = job["msg"]["content"]
        detail_level = int(c.get("detail_level", 0))
        omit_sections = set(c.get("omit_sections", []))
        name = token_at_cursor(c["code"], c["cursor_pos"])
        content = {"data": {}, "metadata": {}, "found": True}
        try:
            bundle = self.shell.object_inspect_mime(name, detail_level=detail_level, omit_sections=omit_sections)
            content["data"] = bundle
            if not self.shell.enable_html_pager:
                content["data"].pop("text/html")
        except KeyError:
            content["found"] = False
        return content

    async def history_request(self, job: Job[Content], /) -> Content:
        """Handle a [history request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#history)."""
        c = job["msg"]["content"]
        history_manager = self.shell.history_manager
        assert history_manager
        if c.get("hist_access_type") == "tail":
            hist = history_manager.get_tail(c["n"], raw=c.get("raw"), output=c.get("output"), include_latest=True)
        elif c.get("hist_access_type") == "range":
            hist = history_manager.get_range(
                c.get("session", 0),
                c.get("start", 1),
                c.get("stop", None),
                raw=c.get("raw", True),
                output=c.get("output", False),
            )
        elif c.get("hist_access_type") == "search":
            hist = history_manager.search(
                c.get("pattern"), raw=c.get("raw"), output=c.get("output"), n=c.get("n"), unique=c.get("unique")
            )
        else:
            hist = []
        return {"history": list(hist)}

    async def comm_open(self, job: Job[Content], /) -> None:
        """Handle a [comm open request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#opening-a-comm)."""
        self.comm_manager.comm_open(stream=job["socket"], ident=job["ident"], msg=job["msg"])  # pyright: ignore[reportArgumentType]

    async def comm_msg(self, job: Job[Content], /) -> None:
        """Handle a [comm msg request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#comm-messages)."""
        self.comm_manager.comm_msg(stream=job["socket"], ident=job["ident"], msg=job["msg"])  # pyright: ignore[reportArgumentType]

    async def comm_close(self, job: Job[Content], /) -> None:
        """Handle a [comm close request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#tearing-down-comms)."""
        self.comm_manager.comm_close(stream=job["socket"], ident=job["ident"], msg=job["msg"])  # pyright: ignore[reportArgumentType]

    async def interrupt_request(self, job: Job[Content], /) -> Content:
        """Handle a [interrupt request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#kernel-interrupt) (control only)."""
        self._interrupt_requested = True
        if sys.platform == "win32":
            signal.raise_signal(signal.SIGINT)
            time.sleep(0)
        else:
            os.kill(os.getpid(), signal.SIGINT)
        for interrupter in tuple(self._interrupts):
            interrupter()
        return {}

    async def shutdown_request(self, job: Job[Content], /) -> Content:
        """Handle a [shutdown request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#kernel-shutdown) (control only)."""
        self.stop()
        return {"restart": job["msg"]["content"].get("restart", False)}

    async def debug_request(self, job: Job[Content], /) -> Content:
        """Handle a [debug request](https://jupyter-client.readthedocs.io/en/stable/messaging.html#debug-request) (control only)."""
        return await self.debugger.process_request(job["msg"]["content"])

    def excepthook(self, etype, evalue, tb) -> None:
        """Handle an exception."""
        # write uncaught traceback to 'real' stderr, not zmq-forwarder
        traceback.print_exception(etype, evalue, tb, file=sys.__stderr__)

    def unraisablehook(self, unraisable: sys.UnraisableHookArgs, /) -> None:
        "Handle unraisable exceptions (during gc for instance)."
        exc_info = (
            unraisable.exc_type,
            unraisable.exc_value or unraisable.exc_type(unraisable.err_msg),
            unraisable.exc_traceback,
        )
        self.log.exception(unraisable.err_msg, exc_info=exc_info, extra={"object": unraisable.object})

    def raw_input(self, prompt="") -> Any:
        """
        Forward raw_input to frontends.

        Raises
        ------
        StdinNotImplementedError if active frontend doesn't support stdin.
        """
        return self._input_request(str(prompt), password=False)

    def getpass(self, prompt="") -> Any:
        """Forward getpass to frontends."""
        return self._input_request(prompt, password=True)

    def get_connection_info(self) -> dict[str, Any]:
        """Return the connection info as a dict."""
        with self.connection_file.open("r") as f:
            return json.load(f)

    def get_parent(self) -> Message[dict[str, Any]] | None:
        """A convenience method to access the 'message' in the current context if there is one.

        'parent' is the parameter name uses in [Session.send][jupyter_client.session.Session.send].

        See also:
            - [Kernel.iopub_send][async_kernel.Kernel.iopub_send]
            - [ipywidgets.Output][ipywidgets.widgets.widget_output.Output]:
                Uses `get_ipython().kernel.get_parent()` to obtain the `msg_id` which
                is used to 'capture' output when it's context has been acquired.
        """
        return utils.get_parent()
