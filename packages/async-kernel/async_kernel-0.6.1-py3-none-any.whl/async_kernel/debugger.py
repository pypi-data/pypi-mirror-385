from __future__ import annotations

import logging
import os
import re
import sys
import threading
from pathlib import Path
from typing import TYPE_CHECKING

import anyio.abc
from IPython.core.inputtransformer2 import leading_empty_lines
from traitlets import Bool, Dict, HasTraits, Instance, Set, default

from async_kernel import AsyncEvent, Future, utils
from async_kernel.caller import AsyncLock

if TYPE_CHECKING:
    from anyio.abc import TaskGroup

    from async_kernel import Kernel
    from async_kernel.typing import DebugMessage

try:
    if "PYDEVD_IPYTHON_COMPATIBLE_DEBUGGING" not in os.environ:
        os.environ["PYDEVD_IPYTHON_COMPATIBLE_DEBUGGING"] = "1"

    # This import is required to provide _pydevd_bundle imports
    from debugpy.server import api  # noqa: F401  # pyright: ignore[reportUnusedImport]

    _is_debugpy_available = True
except ImportError:
    _is_debugpy_available = False
except Exception as e:
    # We cannot import the module where the DebuggerInitializationError
    # is defined
    if e.__class__.__name__ == "DebuggerInitializationError":
        _is_debugpy_available = False
    else:
        raise

_host_port: None | tuple[str, int] = None


class _FakeCode:
    """Fake code class.  Origin: [IPyKernel][ipykernel.debugger._FakeCode]."""

    def __init__(self, co_filename, co_name):
        """Init."""
        self.co_filename = co_filename
        self.co_name = co_name


class _FakeFrame:
    """Fake frame class. Origin: [IPyKernel][ipykernel.debugger._FakeFrame]."""

    def __init__(self, f_code, f_globals, f_locals):
        """Init."""
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals
        self.f_back = None


class _DummyPyDB:
    """Fake PyDb class. Origin: [IPyKernel][ipykernel.debugger._DummyPyDB]."""

    def __init__(self):
        """Init."""
        from _pydevd_bundle.pydevd_api import PyDevdAPI  # type: ignore[attr-defined]  # noqa: PLC0415

        self.variable_presentation = PyDevdAPI.VariablePresentation()


class VariableExplorer(HasTraits):
    """
    A variable explorer.

    Origin: [IPyKernel][ipykernel.debugger.VariableExplorer]
    """

    kernel: Instance[Kernel] = Instance("async_kernel.Kernel", ())

    def __init__(self):
        """Initialize the explorer."""
        super().__init__()
        from _pydevd_bundle.pydevd_suspended_frames import SuspendedFramesManager, _FramesTracker  # type: ignore[attr-defined]  # noqa: I001, PLC0415

        self.suspended_frame_manager = SuspendedFramesManager()
        self.py_db = _DummyPyDB()
        self.tracker = _FramesTracker(self.suspended_frame_manager, self.py_db)
        self.frame = None

    def track(self):
        """Start tracking."""
        from _pydevd_bundle import pydevd_frame_utils  # type: ignore[attr-defined]  # noqa: PLC0415

        shell = self.kernel.shell
        var = shell.user_ns
        self.frame = _FakeFrame(_FakeCode("<module>", shell.compile.get_file_name("sys._getframe()")), var, var)
        self.tracker.track("thread1", pydevd_frame_utils.create_frames_list_from_frame(self.frame))

    def untrack_all(self):
        """Stop tracking."""
        self.tracker.untrack_all()

    def get_children_variables(self, variable_ref=None):
        """Get the child variables for a variable reference."""
        var_ref = variable_ref
        if not var_ref:
            var_ref = id(self.frame)
        try:
            variables = self.suspended_frame_manager.get_variable(var_ref)
        except KeyError:
            return []
        return [x.get_var_data() for x in variables.get_children_variables()]


class DebugpyClient(HasTraits):
    """A client for debugpy. Origin: [IPyKernel][ipykernel.debugger.DebugpyClient]."""

    HEADER = b"Content-Length: "
    SEPARATOR = b"\r\n\r\n"
    SEPARATOR_LENGTH = 4
    tcp_buffer = b""
    _future_responses: Dict[int, Future] = Dict()
    capabilities = Dict()
    kernel: Instance[Kernel] = Instance("async_kernel.Kernel", ())
    _socketstream: anyio.abc.SocketStream | None = None
    _send_lock = Instance(AsyncLock, ())

    def __init__(self, log, event_callback):
        """Initialize the client."""
        super().__init__()
        self.log = log
        self.event_callback = event_callback
        self._pack = self.kernel.session.pack
        self._unpack = self.kernel.session.unpack

    @property
    def connected(self):
        return bool(self._socketstream)

    async def send_request(self, request: dict) -> Future:
        if not (socketstream := self._socketstream):
            raise RuntimeError
        async with self._send_lock:
            self._future_responses[request["seq"]] = fut = Future()
            content = self._pack(request)
            content_length = str(len(content)).encode()
            buf = self.HEADER + content_length + self.SEPARATOR
            buf += content
            self.log.debug("DEBUGPYCLIENT: request %s", buf)
            await socketstream.send(buf)
            return fut

    def put_tcp_frame(self, frame: bytes):
        """Buffer the frame and process the buffer."""
        self.tcp_buffer += frame
        data = self.tcp_buffer.split(self.HEADER)
        if len(data) > 1:
            for buf in data[1:]:
                size, raw_msg = buf.split(self.SEPARATOR, maxsplit=1)
                size = int(size)
                msg: DebugMessage = self._unpack(raw_msg[:size])
                self.log.debug("_put_message :%s %s", msg["type"], msg)
                if msg["type"] == "event":
                    self.event_callback(msg)
                elif future := self._future_responses.pop(msg["request_seq"], None):
                    future.set_result(msg)
            self.tcp_buffer = b""

    async def connect_tcp_socket(self, ready: AsyncEvent):
        """Connect to the tcp socket."""
        global _host_port  # noqa: PLW0603
        if not _host_port:
            import debugpy  # noqa: PLC0415

            _host_port = debugpy.listen(0)
            utils.mark_thread_pydev_do_not_trace(threading.current_thread())
            for thread in threading.enumerate():
                if thread.name == "IPythonHistorySavingThread":
                    thread.pydev_do_not_trace = True  # pyright: ignore[reportAttributeAccessIssue]
            # This thread can't be stopped by the debugger when debugging
        try:
            self.log.debug("++ debugpy socketstream connecting ++")
            async with await anyio.connect_tcp(*_host_port) as socketstream:
                self._socketstream = socketstream
                self.log.debug("++ debugpy socketstream connected ++")
                ready.set()
                while True:
                    data = await socketstream.receive()
                    self.put_tcp_frame(data)
        except anyio.EndOfStream:
            self.log.debug("++ debugpy socketstream disconnected ++")
            return
        finally:
            self._socketstream = None


class Debugger(HasTraits):
    """The debugger class. Origin: [IPyKernel][ipykernel.debugger.DebugpyClient]."""

    _seq = 0
    breakpoint_list = Dict()
    capabilities = Dict()
    stopped_threads = Set()
    _removed_cleanup = Dict()
    just_my_code = Bool(True)
    variable_explorer = Instance(VariableExplorer, ())
    debugpy_client = Instance(DebugpyClient)
    log = Instance(logging.LoggerAdapter)
    kernel: Instance[Kernel] = Instance("async_kernel.Kernel", ())
    taskgroup: TaskGroup | None = None
    init_event = Instance(AsyncEvent, ())

    @default("log")
    def _default_log(self):
        return logging.LoggerAdapter(logging.getLogger(self.__class__.__name__))

    def __init__(self):
        """Initialize the debugger."""
        super().__init__()
        self.debugpy_client = DebugpyClient(log=self.log, event_callback=self._handle_event)
        self.started_debug_handlers = {
            "setBreakpoints": self.do_set_breakpoints,
            "stackTrace": self.do_stack_trace,
            "variables": self.do_variables,
            "attach": self.do_attach,
            "configurationDone": self.do_configuration_done,
            "copyToGlobals": self.do_copy_to_globals,
            "disconnect": self.do_disconnect,
        }
        self.static_debug_handlers = {
            "initialize": self.do_initialize,
            "dumpCell": self.do_dump_cell,
            "source": self.do_source,
            "debugInfo": self.do_debug_info,
            "inspectVariables": self.do_inspect_variables,
            "richInspectVariables": self.do_rich_inspect_variables,
            "modules": self.do_modules,
        }
        self._forbidden_names = tuple(self.kernel.shell.user_ns_hidden)

    async def send_dap_request(self, msg: DebugMessage, /):
        """Sends a DAP request to the debug server, waits for and returns the corresponding response."""
        return await (await self.debugpy_client.send_request(msg))

    def next_seq(self):
        "A monotonically decreasing negative number so as not to clash with the frontend seq."
        self._seq = self._seq - 1
        return self._seq

    def _handle_event(self, event):
        if event["event"] == "stopped":

            async def _handle_stopped_event():
                names = {t.name for t in threading.enumerate() if not getattr(t, "pydev_do_not_trace", False)}
                msg = {"seq": self.next_seq(), "type": "request", "command": "threads"}
                rep = await self.send_dap_request(msg)
                for thread in rep["body"]["threads"]:
                    if thread["name"] in names:
                        self.stopped_threads.add(thread["id"])
                self._publish_event(event)

            self.kernel.control_thread_caller.call_soon(_handle_stopped_event)
            return

        if event["event"] == "continued":
            self.stopped_threads.clear()
        elif event["event"] == "initialized":
            self.init_event.set()
        self._publish_event(event)

    def _publish_event(self, event: dict):
        self.kernel.iopub_send(
            msg_or_type="debug_event",
            content=event,
            ident=self.kernel.topic("debug_event"),
            parent=None,
        )

    def _build_variables_response(self, request, variables):
        var_list = [var for var in variables if self._accept_variable(var["name"])]
        return {
            "seq": request["seq"],
            "type": "response",
            "request_seq": request["seq"],
            "success": True,
            "command": request["command"],
            "body": {"variables": var_list},
        }

    def _accept_variable(self, variable_name):
        """Accept a variable by name."""
        return (
            variable_name not in self._forbidden_names
            and not bool(re.search(r"^_\d", variable_name))
            and not variable_name.startswith("_i")
        )

    async def process_request(self, msg: DebugMessage, /):
        """Process a request."""
        command = msg["command"]
        if handler := self.static_debug_handlers.get(command):
            return await handler(msg)
        if not self.debugpy_client.connected:
            msg_ = "Debugy client not connected."
            raise RuntimeError(msg_)
        if handler := self.started_debug_handlers.get(command):
            return await handler(msg)

        return await self.send_dap_request(msg)

    ## Static handlers

    async def do_initialize(self, msg: DebugMessage, /):
        "Initialize debugpy server starting as required."
        if not self.debugpy_client.connected:
            ready = AsyncEvent()
            self.kernel.control_thread_caller.call_soon(self.debugpy_client.connect_tcp_socket, ready)
            await ready.wait()
            # Don't remove leading empty lines when debugging so the breakpoints are correctly positioned
            cleanup_transforms = self.kernel.shell.input_transformer_manager.cleanup_transforms
            if leading_empty_lines in cleanup_transforms:
                index = cleanup_transforms.index(leading_empty_lines)
                self._removed_cleanup[index] = cleanup_transforms.pop(index)
        reply = await self.send_dap_request(msg)
        if capabilities := reply.get("body"):
            self.capabilities = capabilities
        return reply

    async def do_debug_info(self, msg: DebugMessage, /):
        """Handle a debug info message."""
        if not _is_debugpy_available or utils.LAUNCHED_BY_DEBUGPY:
            return {}
        breakpoint_list = []
        for key, value in self.breakpoint_list.items():
            breakpoint_list.append({"source": key, "breakpoints": value})
        compiler = self.kernel.shell.compile
        return {
            "type": "response",
            "request_seq": msg["seq"],
            "success": True,
            "command": msg["command"],
            "body": {
                "isStarted": self.debugpy_client.connected,
                "hashMethod": compiler.hash_method,
                "hashSeed": compiler.hash_seed,
                "tmpFilePrefix": compiler.tmp_file_prefix,
                "tmpFileSuffix": compiler.tmp_file_suffix,
                "breakpoints": breakpoint_list,
                "stoppedThreads": sorted(self.stopped_threads),
                "richRendering": True,
                "exceptionPaths": ["Python Exceptions"],
                "copyToGlobals": True,
            },
        }

    async def do_inspect_variables(self, msg: DebugMessage, /):
        """Handle an inspect variables message."""
        self.variable_explorer.untrack_all()
        # looks like the implementation of untrack_all in ptvsd
        # destroys objects we need in track. We have no choice but
        # reinstantiate the object
        self.variable_explorer = VariableExplorer()
        self.variable_explorer.track()
        variables = self.variable_explorer.get_children_variables()
        return self._build_variables_response(msg, variables)

    async def do_rich_inspect_variables(self, msg: DebugMessage, /):
        """Handle a rich inspect variables message."""
        reply = {
            "type": "response",
            "sequence_seq": msg["seq"],
            "success": False,
            "command": msg["command"],
        }
        variable_name = msg["arguments"].get("variableName", "")
        if not str.isidentifier(variable_name):
            reply["body"] = {"data": {}, "metadata": {}}
            if variable_name in {"special variables", "function variables"}:
                reply["success"] = True
            return reply
        repr_data = {}
        repr_metadata = {}
        if not self.stopped_threads:
            # The code did not hit a breakpoint, we use the interpreter
            # to get the rich representation of the variable
            result = self.kernel.shell.user_expressions({"var": variable_name})["var"]
            if result.get("status", "error") == "ok":
                repr_data = result.get("data", {})
                repr_metadata = result.get("metadata", {})
        else:
            # The code has stopped on a breakpoint, we use the evaluate
            # request to get the rich representation of the variable
            code = f"get_ipython().display_formatter.format({variable_name})"
            reply = await self.send_dap_request(
                {
                    "type": "request",
                    "command": "evaluate",
                    "seq": self.next_seq(),
                    "arguments": {"expression": code, "context": "clipboard"} | msg["arguments"],
                }
            )
            if reply["success"]:
                repr_data, repr_metadata = eval(reply["body"]["result"], {}, {})
        body = {
            "data": repr_data,
            "metadata": {k: v for k, v in repr_metadata.items() if k in repr_data},
        }
        reply["body"] = body
        reply["success"] = True
        return reply

    async def do_modules(self, msg: DebugMessage, /):
        """Handle a modules message."""
        modules = list(sys.modules.values())
        startModule = msg.get("startModule", 0)
        moduleCount = msg.get("moduleCount", len(modules))
        mods = []
        for i in range(startModule, moduleCount):
            module = modules[i]
            filename = getattr(getattr(module, "__spec__", None), "origin", None)
            if filename and filename.endswith(".py"):
                mods.append({"id": i, "name": module.__name__, "path": filename})
        return {"body": {"modules": mods, "totalModules": len(modules)}}

    async def do_dump_cell(self, msg: DebugMessage, /):
        """Handle a dump cell message."""
        code = msg["arguments"]["code"]
        path = self.kernel.shell.compile.get_file_name(code)
        path.parent.mkdir(exist_ok=True)
        with path.open("w") as f:
            f.write(code)
        return {
            "type": "response",
            "request_seq": msg["seq"],
            "success": True,
            "command": msg["command"],
            "body": {"sourcePath": str(path)},
        }

    # Started handlers (requires debug_client connection)

    async def do_copy_to_globals(self, msg: DebugMessage, /):
        dst_var_name = msg["arguments"]["dstVariableName"]
        src_var_name = msg["arguments"]["srcVariableName"]
        src_frame_id = msg["arguments"]["srcFrameId"]
        # Copy the variable to the user_ns
        await self.send_dap_request(
            {
                "type": "request",
                "command": "evaluate",
                "seq": self.next_seq(),
                "arguments": {
                    "expression": f"import async_kernel;async_kernel.Kernel().shell.user_ns['{dst_var_name}'] = {src_var_name}",
                    "frameId": src_frame_id,
                    "context": "repl",
                },
            }
        )
        return await self.send_dap_request(
            {
                "type": "request",
                "command": "evaluate",
                "seq": msg["seq"],
                "arguments": {
                    "expression": f"globals()['{dst_var_name}'] = {src_var_name}",
                    "frameId": src_frame_id,
                    "context": "repl",
                },
            }
        )

    async def do_set_breakpoints(self, msg: DebugMessage, /):
        """Handle a set breakpoints message."""
        source = msg["arguments"]["source"]["path"]
        self.breakpoint_list[source] = msg["arguments"]["breakpoints"]
        message_response = await self.send_dap_request(msg)
        # debugpy can set breakpoints on different lines than the ones requested,
        # so we want to record the breakpoints that were actually added
        if message_response.get("success"):
            self.breakpoint_list[source] = [
                {"line": breakpoint["line"]} for breakpoint in message_response["body"]["breakpoints"]
            ]
        return message_response

    async def do_source(self, msg: DebugMessage, /):
        """Handle a source message."""
        reply = {"type": "response", "request_seq": msg["seq"], "command": msg["command"]}
        if (path := Path(msg["arguments"].get("source", {}).get("path", "missing"))).is_file():
            with path.open("r", encoding="utf-8") as f:
                reply["success"] = True
                reply["body"] = {"content": f.read()}
        else:
            reply["success"] = False
            reply["message"] = "source unavailable"
            reply["body"] = {}

        return reply

    async def do_stack_trace(self, msg: DebugMessage, /):
        """Handle a stack trace message."""
        reply = await self.send_dap_request(msg)
        # The stackFrames array can have the following content:
        # { frames from the notebook}
        # ...
        # { 'id': xxx, 'name': '<module>', ... } <= this is the first frame of the code from the notebook
        # { frames from async_kernel }
        # ...
        # {'id': yyy, 'name': '<module>', ... } <= this is the first frame of async_kernel code
        # or only the frames from the notebook.
        # We want to remove all the frames from async_kernel when they are present.
        try:
            sf_list = reply["body"]["stackFrames"]
            module_idx = len(sf_list) - next(
                i for i, v in enumerate(reversed(sf_list), 1) if v["name"] == "<module>" and i != 1
            )
            reply["body"]["stackFrames"] = reply["body"]["stackFrames"][: module_idx + 1]
        except StopIteration:
            pass
        return reply

    async def do_variables(self, msg: DebugMessage, /):
        """Handle a variables message."""
        reply = {}
        if not self.stopped_threads:
            variables = self.variable_explorer.get_children_variables(msg["arguments"]["variablesReference"])
            return self._build_variables_response(msg, variables)
        reply = await self.send_dap_request(msg)
        if "body" in reply:
            variables = [var for var in reply["body"]["variables"] if self._accept_variable(var["name"])]
            reply["body"]["variables"] = variables
        return reply

    async def do_attach(self, msg: DebugMessage, /):
        """Handle an attach message."""
        assert _host_port
        msg["arguments"]["connect"] = {"host": _host_port[0], "port": _host_port[1]}
        if self.just_my_code:
            msg["arguments"]["debugOptions"] = ["justMyCode"]
        reply = await self.debugpy_client.send_request(msg)
        await self.init_event.wait()
        await self.send_dap_request(
            {
                "type": "request",
                "seq": self.next_seq(),
                "command": "configurationDone",
            }
        )
        return await reply

    async def do_configuration_done(self, msg: DebugMessage, /):
        """Handle a configuration done message."""
        # This is only supposed to be called during initialize but can come at anytime. Ref: https://microsoft.github.io/debug-adapter-protocol/specification#Events_Initialized
        # see : https://github.com/jupyterlab/jupyterlab/issues/17673
        return {
            "seq": msg["seq"],
            "type": "response",
            "request_seq": msg["seq"],
            "success": True,
            "command": msg["command"],
        }

    async def do_disconnect(self, msg: DebugMessage, /):
        response = await self.send_dap_request(msg)
        # Restore the leading whitespace remove transform.
        cleanup_transforms = self.kernel.shell.input_transformer_manager.cleanup_transforms
        for index in sorted(self._removed_cleanup):
            func = self._removed_cleanup.pop(index)
            cleanup_transforms.insert(index, func)
        self.init_event = AsyncEvent()
        self.breakpoint_list = {}
        return response

    async def disconnect(self):
        if self.debugpy_client.connected:
            await self.send_dap_request(
                {
                    "type": "request",
                    "command": "disconnect",
                    "seq": self.next_seq(),
                    "arguments": {
                        "restart": False,
                        "terminateDebuggee": False,
                        "suspendDebuggee": False,
                    },
                }
            )
