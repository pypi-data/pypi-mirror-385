from __future__ import annotations

import inspect
import logging
import pathlib
import sys
import threading
import time
from typing import TYPE_CHECKING, Any, Literal, cast

import anyio
import pytest
import zmq

import async_kernel.utils
from async_kernel.caller import Caller
from async_kernel.comm import Comm
from async_kernel.compiler import murmur2_x86
from async_kernel.typing import ExecuteContent, Job, MsgType, RunMode, SocketID, Tags
from tests import utils

if TYPE_CHECKING:
    from collections.abc import Mapping

    from async_kernel.kernel import Kernel


from async_kernel.kernel import bind_socket


@pytest.fixture(scope="module", params=["tcp", "ipc"] if sys.platform == "linux" else ["tcp"])
def transport(request):
    return request.param


def test_bind_socket(transport: Literal["tcp", "ipc"], tmp_path):
    ctx = zmq.Context()
    ip = tmp_path / "mypath" if transport == "ipc" else "0.0.0.0"
    with ctx:
        with ctx.socket(zmq.SocketType.ROUTER) as socket:
            port = bind_socket(socket, transport, ip)  # pyright: ignore[reportArgumentType]
        with ctx.socket(zmq.SocketType.ROUTER) as socket:
            assert bind_socket(socket, transport, ip, port) == port  # pyright: ignore[reportArgumentType]
            if transport == "tcp":
                with pytest.raises(RuntimeError):
                    bind_socket(socket, transport, ip, max_attempts=0)  # pyright: ignore[reportArgumentType]
                with pytest.raises(ValueError, match="Invalid transport"):
                    bind_socket(socket, "", ip, max_attempts=1)  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize("mode", ["direct", "proxy"])
async def test_iopub(kernel, mode: Literal["direct", "proxy"]) -> None:
    def pubio_subscribe():
        """Consume messages."""
        with ctx.socket(zmq.SocketType.SUB) as socket:
            socket.linger = 0
            socket.connect(url)
            socket.setsockopt(zmq.SocketOption.SUBSCRIBE, b"")
            i = 0
            while i < n:
                msg = socket.recv_multipart()
                if msg[0] == b"0":
                    assert int(msg[1]) == i
                    i += 1
            # Also test iopub from a thread that doesn't have a socket works via control thread.
            print("done")
            msg = socket.recv_multipart()
            assert msg[-1] == b'{"name": "stdout", "text": "done"}'

    n = 10
    socket = kernel._sockets[SocketID.iopub]
    url = socket.get_string(zmq.SocketOption.LAST_ENDPOINT)
    assert url.endswith(str(kernel._ports[SocketID.iopub]))
    ctx = zmq.Context()
    thread = threading.Thread(target=pubio_subscribe)
    thread.start()
    try:
        time.sleep(0.05)
        if mode == "proxy":
            socket = Caller.iopub_sockets[threading.current_thread()]
        for i in range(n):
            socket.send_multipart([b"0", f"{i}".encode()])
        thread.join()
    finally:
        ctx.term()


async def test_load_connection_info_error(kernel: Kernel, tmp_path):
    with pytest.raises(RuntimeError):
        kernel.load_connection_info({})


async def test_execute_request_success(client):
    reply: dict[Any, Any] | Mapping[str, Mapping[str, Any]] = await utils.send_shell_message(
        client, MsgType.execute_request, {"code": "1 + 1", "silent": False}
    )
    assert reply["header"]["msg_type"] == "execute_reply"
    assert reply["content"]["status"] == "ok"


@pytest.mark.parametrize("quiet", [True, False])
async def test_simple_print(kernel, client, quiet: bool):
    """Simple print statement in kernel."""
    await utils.clear_iopub(client)
    kernel.quiet = quiet
    try:
        client.execute("print('test_simple_print')")
        stdout, stderr = await utils.assemble_output(client)
        assert stdout == "test_simple_print\n"
        assert stderr == ""
    finally:
        kernel.quiet = True


@pytest.mark.parametrize("mode", ["kernel_timeout", "metadata"])
async def test_execute_kernel_timeout(client, kernel: Kernel, mode: str):
    await utils.clear_iopub(client)
    kernel.shell.execute_request_timeout = 0.1 if "kernel" in mode else None
    last_stop_time = kernel._stop_on_error_time  # pyright: ignore[reportPrivateUsage]
    metadata: dict[str, float | list] = {"timeout": 0.1}
    try:
        code = "\n".join(["import anyio", "await anyio.sleep_forever()"])
        msg_id, content = await utils.execute(client, code=code, metadata=metadata, clear_pub=False)
        assert last_stop_time == kernel._stop_on_error_time, "Should not cause cancellation"  # pyright: ignore[reportPrivateUsage]
        assert content["status"] == "ok"
        await utils.check_pub_message(client, msg_id, execution_state="busy")
        await utils.check_pub_message(client, msg_id, msg_type="execute_input")
        expected = {"traceback": [], "ename": "TimeoutError", "evalue": "Cell execute timeout"}
        await utils.check_pub_message(client, msg_id, msg_type="error", **expected)
        await utils.check_pub_message(client, msg_id, execution_state="idle")
    finally:
        kernel.shell.execute_request_timeout = None


async def test_bad_message(client):
    await utils.send_shell_message(client, "bad_message", reply=False)  # pyright: ignore[reportArgumentType]
    await utils.send_control_message(client, "bad_message", reply=False)  # pyright: ignore[reportArgumentType]
    await utils.execute(client, "")


@pytest.mark.parametrize("test_mode", ["interrupt", "reply", "allow_stdin=False"])
@pytest.mark.parametrize("mode", ["input", "password"])
async def test_input(
    subprocess_kernels_client,
    mode: Literal["input", "password"],
    test_mode: Literal["interrupt", "reply", "allow_stdin=False"],
):
    client = subprocess_kernels_client
    client.input("Some input that should be discardes")
    theprompt = "Enter a value >"
    match mode:
        case "input":
            code = f"response = input('{theprompt}')"
        case "password":
            code = f"import getpass;response = getpass.getpass('{theprompt}')"
    # allow_stdin=False
    if test_mode == "allow_stdin=False":
        _, reply = await utils.execute(client, code, allow_stdin=False)
        assert reply["status"] == "error"
        assert reply["ename"] == "StdinNotImplementedError"
        return
    msg_id = client.execute(code, allow_stdin=True, user_expressions={"response": "response"})
    msg = await client.get_stdin_msg()
    assert msg["header"]["msg_type"] == "input_request"
    content = msg["content"]
    assert content["prompt"] == theprompt
    # interrupt
    if test_mode == "interrupt":
        await utils.send_control_message(client, MsgType.interrupt_request)
        reply = await utils.get_reply(client, msg_id, clear_pub=False)
        assert reply["content"]["status"] == "error"
        return
    # reply
    text = "some text"
    client.input(text)
    reply = await utils.get_reply(client, msg_id)
    assert reply["content"]["status"] == "ok"
    assert text in reply["content"]["user_expressions"]["response"]["data"]["text/plain"]


async def test_unraisablehook(kernel, mocker):
    handler = logging.Handler()
    kernel.log.logger.addHandler(handler)

    class Unraiseable:
        def __init__(self) -> None:
            self.exc_type = BaseException
            self.exc_value = BaseException()
            self.exc_traceback = None
            self.err_msg = "my error message"
            self.object = ""

    emit = mocker.patch.object(handler, "emit")
    kernel.unraisablehook(Unraiseable())
    assert emit.call_count == 1
    kernel.log.logger.removeHandler(handler)


async def test_save_history(client, tmp_path):
    file = tmp_path.joinpath("hist.out")
    client.execute("a=1")
    await utils.wait_for_idle(client)
    client.execute('b="abcþ"')
    await utils.wait_for_idle(client)
    _, reply = await utils.execute(client, f"%hist -f {file}")
    assert reply["status"] == "ok"
    with file.open("r", encoding="utf-8") as f:
        content = f.read()
    assert "a=1" in content
    assert 'b="abcþ"' in content


@pytest.mark.parametrize(
    ("code", "status"),
    [
        ("2+2", "complete"),
        ("raise = 2", "invalid"),
        ("a = [1,\n2,", "incomplete"),
        ("%%timeit\na\n\n", "complete"),
    ],
)
async def test_is_complete(client, code: str, status: str):
    # There are more test cases for this in core - here we just check
    # that the kernel exposes the interface correctly.
    client.is_complete(code)
    reply = await client.get_shell_msg()
    assert reply["content"]["status"] == status


async def test_message_order(client):
    N = 100  # number of messages to test

    _, reply = await utils.execute(client, "a = 1")
    offset = reply["execution_count"] + 1
    cell = "a += 1\na"

    # submit N executions as fast as we can
    msg_ids = [client.execute(cell) for _ in range(N)]
    # check message-handling order
    for i, msg_id in enumerate(msg_ids, offset):
        reply = await client.get_shell_msg()
        assert reply["content"]["execution_count"] == i
        assert reply["parent_header"]["msg_id"] == msg_id


async def test_execute_request_error_tag_ignore_error(client):
    await utils.clear_iopub(client)
    metadata = {"tags": [Tags.suppress_error]}
    await utils.execute(client, "stop - suppress me", metadata=metadata, clear_pub=False)
    stdout, _ = await utils.assemble_output(client)
    assert "⚠" in stdout


@pytest.mark.parametrize("run_mode", RunMode)
@pytest.mark.parametrize(
    "code",
    [
        "some invalid code",
        """
        from async_kernel.caller import FutureCancelledError,
        async def fail():,
            raise FutureCancelledError,
        await fail()""",
    ],
)
async def test_execute_request_error(client, code: str, run_mode: RunMode):
    reply = await utils.send_shell_message(client, MsgType.execute_request, {"code": code, "silent": False})
    assert reply["header"]["msg_type"] == "execute_reply"
    assert reply["content"]["status"] == "error"


async def test_execute_request_stop_on_error(client):
    client.execute("import anyio;await anyio.sleep(0.1);stop-here")
    _, content = await utils.execute(client)
    assert content["evalue"] == "Aborting due to prior exception"


async def test_complete_request(client):
    reply = await utils.send_shell_message(client, MsgType.complete_request, {"code": "hello", "cursor_pos": 0})
    assert reply["header"]["msg_type"] == "complete_reply"


async def test_inspect_request(client):
    reply = await utils.send_shell_message(client, MsgType.inspect_request, {"code": "hello", "cursor_pos": 0})
    assert reply["header"]["msg_type"] == "inspect_reply"


async def test_history_request(client, kernel):
    assert kernel.shell
    # assert kernel.shell.history_manager

    # kernel.shell.history_manager.db = DummyDB()
    reply = await utils.send_shell_message(
        client, MsgType.history_request, {"hist_access_type": "", "output": "", "raw": ""}
    )
    assert reply["header"]["msg_type"] == "history_reply"
    reply = await utils.send_shell_message(
        client, MsgType.history_request, {"hist_access_type": "tail", "output": "", "raw": ""}
    )
    assert reply["header"]["msg_type"] == "history_reply"
    reply = await utils.send_shell_message(
        client, MsgType.history_request, {"hist_access_type": "range", "output": "", "raw": ""}
    )
    assert reply["header"]["msg_type"] == "history_reply"
    reply = await utils.send_shell_message(
        client, MsgType.history_request, {"hist_access_type": "search", "output": "", "raw": ""}
    )
    assert reply["header"]["msg_type"] == "history_reply"


async def test_comm_info_request(client):
    reply = await utils.send_shell_message(client, MsgType.comm_info_request)
    assert reply["header"]["msg_type"] == "comm_info_reply"


async def test_comm_open_msg_close(client, kernel, mocker):
    comm = None

    def cb(comm_, _):
        nonlocal comm
        comm = comm_

    kernel.comm_manager.register_target("my target", cb)
    # open a comm
    with anyio.move_on_after(0.1):
        await utils.send_shell_message(
            client, MsgType.comm_open, {"content": {}, "comm_id": "comm id", "target_name": "my target"}
        )
    assert isinstance(comm, Comm)
    comm = cast("Comm", comm)
    reply = await utils.send_shell_message(client, MsgType.comm_info_request)
    assert reply["header"]["msg_type"] == "comm_info_reply"
    assert reply["content"]["comms"].get("comm id") == {"target_name": "my target"}

    msg_received = mocker.patch.object(comm, "handle_msg")
    with anyio.move_on_after(0.1):
        await utils.send_shell_message(client, MsgType.comm_msg, {"comm_id": comm.comm_id})
    assert msg_received.call_count == 1
    # close comm
    closed = mocker.patch.object(comm, "handle_close")
    with anyio.move_on_after(0.1):
        await utils.send_shell_message(client, MsgType.comm_close, {"comm_id": comm.comm_id})
    assert closed.call_count == 1
    kernel.comm_manager.unregister_target("my target", cb)


async def test_interrupt_request(client, kernel):
    event = threading.Event()
    kernel._interrupts.add(event.set)
    reply = await utils.send_control_message(client, MsgType.interrupt_request)
    assert reply["header"]["msg_type"] == "interrupt_reply"
    assert reply["content"] == {"status": "ok"}
    assert event.is_set()


async def test_interrupt_request_async_request(subprocess_kernels_client):
    await utils.clear_iopub(subprocess_kernels_client)
    client = subprocess_kernels_client
    msg_id = client.execute(f"await anyio.sleep({utils.TIMEOUT * 4})")
    await utils.check_pub_message(client, msg_id, execution_state="busy")
    await utils.check_pub_message(client, msg_id, msg_type="execute_input")
    await anyio.sleep(0.5)
    reply = await utils.send_control_message(client, MsgType.interrupt_request)
    reply = await utils.get_reply(client, msg_id)
    assert reply["content"]["status"] == "error"


# @pytest.mark.flaky
async def test_interrupt_request_blocking_exec_request(subprocess_kernels_client):
    await utils.clear_iopub(subprocess_kernels_client)
    client = subprocess_kernels_client
    msg_id = client.execute(f"import time;time.sleep({utils.TIMEOUT * 4})")
    await utils.check_pub_message(client, msg_id, execution_state="busy")
    await utils.check_pub_message(client, msg_id, msg_type="execute_input")
    await anyio.sleep(0.5)
    reply = await utils.send_control_message(client, MsgType.interrupt_request)
    with anyio.fail_after(utils.TIMEOUT):
        reply = await utils.get_reply(client, msg_id)
    assert reply["content"]["status"] == "error"
    assert reply["content"]["ename"] == "FutureCancelledError"


async def test_interrupt_request_blocking_task(subprocess_kernels_client):
    await utils.clear_iopub(subprocess_kernels_client)
    code = f"""
    import time
    from async_kernel import Caller
    await Caller().call_soon(time.sleep, {utils.TIMEOUT * 2})
    """
    client = subprocess_kernels_client
    msg_id = client.execute(code, reply=False)
    await utils.check_pub_message(client, msg_id, execution_state="busy")
    await utils.check_pub_message(client, msg_id, msg_type="execute_input")
    await anyio.sleep(0.5)
    for _ in range(2):  # Blocking calls in tasks need to be interrupted twice
        await utils.send_control_message(client, MsgType.interrupt_request)
    reply = await utils.get_reply(client, msg_id)
    assert reply["content"]["status"] == "error"
    assert reply["content"]["ename"] == "FutureCancelledError"


@pytest.mark.parametrize("response", ["y", ""])
async def test_user_exit(client, kernel, mocker, response: Literal["y", ""]):
    stop = mocker.patch.object(kernel, "stop")
    raw_input = mocker.patch.object(kernel, "raw_input", return_value=response)
    await utils.execute(client, "quit()")
    assert raw_input.call_count == 1
    assert stop.call_count == (1 if response == "y" else 0)
    kernel.exit_now = False


async def test_is_complete_request(client):
    reply = await utils.send_shell_message(client, MsgType.is_complete_request, {"code": "hello"})
    assert reply["header"]["msg_type"] == "is_complete_reply"


@pytest.mark.parametrize("command", ["debugInfo", "inspectVariables", "modules", "dumpCell", "source"])
async def test_debug_static(client, command: str, mocker):
    # These are tests on the debugger that don't required the debugger to be connected.
    code = "my_variable=123"
    if command == "debugInfo":
        mocker.patch.object(async_kernel.utils, "LAUNCHED_BY_DEBUGPY", new=True)
        assert async_kernel.utils.LAUNCHED_BY_DEBUGPY
    reply = await utils.send_control_message(
        client, MsgType.debug_request, {"type": "request", "seq": 1, "command": command, "arguments": {"code": code}}
    )
    assert reply["content"]["status"] == "ok"
    if command == "dumpCell":
        path = reply["content"]["body"]["sourcePath"]
        reply = await utils.send_control_message(
            client,
            MsgType.debug_request,
            {"type": "request", "seq": 1, "command": "source", "arguments": {"source": {"path": path}}},
        )
        assert reply["content"]["status"] == "ok"
        assert reply["content"]["body"] == {"content": code}


async def test_debug_raises_no_socket(kernel):
    with pytest.raises(RuntimeError):
        await kernel.debugger.debugpy_client.send_request({})


async def test_debug_not_connected(client):
    reply = await utils.send_control_message(
        client, MsgType.debug_request, {"type": "request", "seq": 1, "command": "disconnect", "arguments": {}}
    )
    assert reply["content"]["status"] == "error"
    assert reply["content"]["evalue"] == "Debugy client not connected."


@pytest.mark.parametrize("variable_name", ["my_variable", "invalid variable name", "special variables"])
async def test_debug_static_richInspectVariables(client, variable_name):
    # These are tests on the debugger that don't required the debugger to be connected.
    reply = await utils.send_control_message(
        client,
        MsgType.debug_request,
        {
            "type": "request",
            "seq": 1,
            "command": "richInspectVariables",
            "arguments": {"code": "my_variable=123", "variableName": variable_name},
        },
    )
    assert reply["content"]["status"] == "ok"


async def test_properties(kernel) -> None:
    class user_mod:
        __dict__ = {}

    kernel.user_module = user_mod()
    kernel.user_ns = {}


@pytest.mark.parametrize("code", argvalues=["%connect_info", "%callers"])
async def test_magic(client, code: str, kernel, monkeypatch):
    await utils.clear_iopub(client)
    monkeypatch.setenv("JUPYTER_RUNTIME_DIR", str(pathlib.Path(kernel.connection_file).parent))
    assert code
    _, reply = await utils.execute(client, code, clear_pub=False)
    assert reply["status"] == "ok"
    stdout, _ = await utils.assemble_output(client)
    assert stdout


async def test_shell_required_properites(kernel):
    # used by ipython AutoMagicChecker via is_shadowed (requires 'builitin')
    assert set(kernel.shell.ns_table) == {"user_global", "user_local", "builtin"}
    # U
    kernel.shell.enable_gui()


async def test_shell_can_set_namespace(kernel):
    kernel.shell.user_ns = {}
    assert set(kernel.shell.user_ns) == {"Out", "_oh", "In", "exit", "_dh", "open", "get_ipython", "_ih", "quit"}


async def test_shell_display_hook_reg(kernel: Kernel):
    val: None | dict = None

    def my_hook(msg):
        nonlocal val
        val = msg

    kernel.shell.display_pub.register_hook(my_hook)
    assert my_hook in kernel.shell.display_pub._hooks  # pyright: ignore[reportPrivateUsage]
    kernel.shell.display_pub.publish({"test": True})
    kernel.shell.display_pub.unregister_hook(my_hook)
    assert my_hook not in kernel.shell.display_pub._hooks  # pyright: ignore[reportPrivateUsage]
    assert val


@pytest.mark.parametrize("mode", RunMode)
async def test_header_mode(client, mode: RunMode):
    code = f"""
{mode}
import time
time.sleep(0.1)
print("{mode.name}")
"""
    await utils.clear_iopub(client)
    _, reply = await utils.execute(client, code, clear_pub=False)
    assert reply["status"] == "ok"
    stdout, _ = await utils.assemble_output(client)
    assert mode.name in stdout
    Caller.stop_all()


@pytest.mark.parametrize(
    "code",
    [
        "from async_kernel import Caller; Caller().call_later(str, 0, 123)",
        "from async_kernel import Caller; Caller().call_soon(print, 'hello')",
    ],
)
async def test_namespace_default(client, code: str):
    assert code
    _, reply = await utils.execute(client, code)
    assert reply["status"] == "ok"
    await anyio.sleep(0.02)


@pytest.mark.parametrize("channel", ["shell", "control"])
async def test_invalid_message(client, channel):
    f = utils.send_control_message if channel == "control" else utils.send_shell_message
    response = None
    with anyio.move_on_after(0.1):
        response = await f(client, "test_invalid_message")  # pyright: ignore[reportArgumentType]
    assert response is None


async def test_kernel_get_handler(kernel: Kernel):
    with pytest.raises(TypeError):
        kernel.get_handler("invalid mode")  # pyright: ignore[reportArgumentType]
    for msg_type in MsgType:
        handler = kernel.get_handler(msg_type)
        assert inspect.iscoroutinefunction(handler)
        sig = inspect.signature(handler)
        assert len(sig.parameters) == 1
        param = sig.parameters["job"]
        assert param.kind == param.POSITIONAL_ONLY


@pytest.mark.parametrize(
    ("code", "silent", "socket_id", "expected"),
    [
        (f"{RunMode.task}", False, SocketID.shell, RunMode.task),
        (f" {RunMode.task}", False, SocketID.shell, RunMode.task),
        ("print(1)", False, SocketID.shell, RunMode.queue),
        ("", True, SocketID.shell, RunMode.task),
        (f"{RunMode.thread}\nprint('hello')", False, SocketID.shell, RunMode.thread),
        ("", False, SocketID.control, RunMode.task),
        ("threads", False, SocketID.shell, RunMode.queue),
        ("Task", False, SocketID.shell, RunMode.queue),
        ("RunMode.blocking", False, SocketID.shell, RunMode.blocking),
    ],
)
async def test_get_run_mode(
    kernel: Kernel, code: str, silent: bool, socket_id, expected: RunMode, job: Job[ExecuteContent]
):
    job["msg"]["content"]["code"] = code
    job["msg"]["content"]["silent"] = silent
    mode = kernel.get_run_mode(MsgType.execute_request, socket_id=socket_id, job=job)
    assert mode is expected


async def test_get_run_mode_tag(client):
    metadata = {"tags": [RunMode.thread]}
    _, content = await utils.execute(
        client,
        "from async_kernel import utils;run_mode=utils.get_job()['run_mode']",
        metadata=metadata,
        user_expressions={"run_mode": "run_mode"},
    )
    assert content["status"] == "ok"
    assert "thread" in content["user_expressions"]["run_mode"]["data"]["text/plain"]


async def test_all_concurrency_run_modes(kernel):
    data = kernel.all_concurrency_run_modes()
    # Regen the hash as required
    assert murmur2_x86(str(data), 1) == 790110932


async def test_get_parent(client, kernel):
    assert kernel.get_parent() is None
    code = "assert 'header' in get_ipython().kernel.get_parent()"
    await utils.execute(client, code)
