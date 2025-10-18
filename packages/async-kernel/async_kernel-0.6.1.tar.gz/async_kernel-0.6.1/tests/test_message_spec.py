from queue import Empty

import pytest

from async_kernel.typing import MsgType
from tests import utils


async def test_execute(client, kernel):
    msg_id = client.execute(code="x=1")
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "execute_reply", msg_id)
    assert kernel.shell.user_ns["x"] == 1


async def test_execute_control(client, kernel):
    await utils.clear_iopub(client)
    reply = await utils.send_control_message(
        client, MsgType.execute_request, {"code": "y=10", "silent": True}, clear_pub=False
    )
    assert kernel.shell.user_ns["y"] == 10
    await utils.check_pub_message(client, reply["parent_header"]["msg_id"], execution_state="busy")
    await utils.check_pub_message(client, reply["parent_header"]["msg_id"], execution_state="idle")


async def test_execute_silent(client):
    await utils.clear_iopub(client)
    msg_id, reply = await utils.execute(client, code="x=1", silent=True, clear_pub=False)
    count = reply["execution_count"]
    await utils.check_pub_message(client, msg_id, execution_state="busy")
    await utils.check_pub_message(client, msg_id, execution_state="idle")
    with pytest.raises(Empty):
        await client.get_iopub_msg(timeout=0.1)

    # Do a second execution
    msg_id, reply = await utils.execute(client, code="x=2", silent=True, clear_pub=False)
    await utils.check_pub_message(client, msg_id, execution_state="busy")
    await utils.check_pub_message(client, msg_id, execution_state="idle")
    with pytest.raises(Empty):
        await client.get_iopub_msg(timeout=0.1)
    count_2 = reply["execution_count"]

    assert count_2 == count, "count should not increment when silent"


async def test_execute_error(client):
    await utils.clear_iopub(client)
    msg_id, reply = await utils.execute(client, code="1/0", clear_pub=False)
    assert reply["status"] == "error"
    assert reply["ename"] == "ZeroDivisionError"

    await utils.check_pub_message(client, msg_id, execution_state="busy")
    await utils.check_pub_message(client, msg_id, msg_type="execute_input")
    await utils.check_pub_message(client, msg_id, msg_type="error")
    await utils.check_pub_message(client, msg_id, execution_state="idle")


async def test_execute_inc(client):
    """Execute request should increment execution_count."""

    _, reply = await utils.execute(client, code="x=1")
    count = reply["execution_count"]

    _, reply = await utils.execute(client, code="x=2")
    count_2 = reply["execution_count"]
    assert count_2 == count + 1


async def test_execute_stop_on_error(client):
    """Execute request should not abort execution queue with stop_on_error False."""

    bad_code = "\n".join(
        [
            # sleep to ensure subsequent message is waiting in the queue to be aborted
            # async sleep to ensure coroutines are processing while this happens
            "import anyio",
            "await anyio.sleep(0.1)",
            "raise ValueError()",
        ]
    )

    msg_id_bad_code = client.execute(bad_code)
    msg_id_1 = client.execute('print("Hello")')
    msg_id_2 = client.execute('print("world")')
    content = await utils.get_shell_message(client, msg_id_bad_code, "execute_reply")
    assert content.get("status") == "error"
    assert content.get("traceback")

    content = await utils.get_shell_message(client, msg_id_1, "execute_reply")
    assert content["status"] == "error"

    content = await utils.get_shell_message(client, msg_id_2, "execute_reply")
    assert content["status"] == "error"

    #  Test stop_on_error=False
    msg_id_3 = client.execute(bad_code, stop_on_error=False)
    msg_id_4 = client.execute('print("Hello")')
    content = await utils.get_shell_message(client, msg_id_3, "execute_reply")
    content = await utils.get_shell_message(client, msg_id_4, "execute_reply")
    assert content["status"] == "ok"


async def test_non_execute_stop_on_error(client):
    """Test that non-execute_request's are not aborted after an error."""

    execute_id = client.execute("raise ValueError")
    content = await utils.get_shell_message(client, execute_id, "execute_reply")
    assert content.get("status") == "error"

    kernel_info_id = client.kernel_info()
    comm_info_id = client.comm_info()
    inspect_id = client.inspect(code="print")

    content = await utils.get_shell_message(client, kernel_info_id, "kernel_info_reply")
    assert content.get("status") == "ok"
    content = await utils.get_shell_message(client, comm_info_id, "comm_info_reply")
    assert content.get("status") == "ok"
    content = await utils.get_shell_message(client, inspect_id, "inspect_reply")
    assert content.get("status") == "ok"


async def test_user_expressions(client):
    msg_id = client.execute(code="x=1", user_expressions={"foo": "x+1"})
    reply = await utils.get_reply(client, msg_id)  # execute
    user_expressions = reply["content"]["user_expressions"]
    assert user_expressions == {
        "foo": {
            "status": "ok",
            "data": {"text/plain": "2"},
            "metadata": {},
        }
    }


async def test_user_expressions_fail(client):
    _, reply = await utils.execute(client, code="x=0", user_expressions={"foo": "nosuchname"})
    user_expressions = reply["user_expressions"]
    foo = user_expressions["foo"]
    assert foo["status"] == "error"
    assert foo["ename"] == "NameError"


async def test_oinfo(client):
    msg_id = client.inspect("a")
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "inspect_reply", msg_id)


async def test_oinfo_found(client):
    msg_id, reply = await utils.execute(client, code="a=5")

    msg_id = client.inspect("a")
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "inspect_reply", msg_id)
    content = reply["content"]
    assert content["found"]
    text = content["data"]["text/plain"]
    assert "Type:" in text
    assert "Docstring:" in text


async def test_oinfo_detail(client):
    msg_id, reply = await utils.execute(client, code="ip=get_ipython()")

    msg_id = client.inspect("ip.object_inspect", cursor_pos=10, detail_level=1)
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "inspect_reply", msg_id)
    content = reply["content"]
    assert content["found"]
    text = content["data"]["text/plain"]
    assert "Signature:" in text
    assert "Source:" in text


async def test_oinfo_not_found(client):
    msg_id = client.inspect("does_not_exist")
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "inspect_reply", msg_id)
    content = reply["content"]
    assert not content["found"]


async def test_complete(client):
    msg_id, reply = await utils.execute(client, code="alpha = albert = 5")

    msg_id = client.complete("al", 2)
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "complete_reply", msg_id)
    matches = reply["content"]["matches"]
    for name in ("alpha", "albert"):
        assert name in matches


async def test_kernel_info_request(client):
    msg_id = client.kernel_info()
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "kernel_info_reply", msg_id)
    assert not {
        "implementation",
        "status",
        "debugger",
        "protocol_version",
        "implementation_version",
        "language_info",
        "help_links",
        "banner",
    }.difference(reply["content"])


async def test_comm_info_request(client):
    msg_id = client.comm_info()
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "comm_info_reply", msg_id)


async def test_is_complete(client):
    msg_id = client.is_complete("a = 1")
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "is_complete_reply", msg_id)


async def test_history_range(client):
    await utils.execute(client, code="x=1", store_history=True)
    msg_id = client.history(hist_access_type="range", raw=True, output=True, start=1, stop=2, session=0)
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "history_reply", msg_id)
    content = reply["content"]
    assert len(content["history"]) == 1


async def test_history_tail(client):
    await utils.execute(client, code="x=1", store_history=True)
    msg_id = client.history(hist_access_type="tail", raw=True, output=True, n=1, session=0)
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "history_reply", msg_id)
    content = reply["content"]
    assert len(content["history"]) == 1


async def test_history_search(client):
    await utils.execute(client, code="x=1", store_history=True)
    msg_id = client.history(hist_access_type="search", raw=True, output=True, n=1, pattern="*", session=0)
    reply = await utils.get_reply(client, msg_id)
    utils.validate_message(reply, "history_reply", msg_id)
    content = reply["content"]
    assert len(content["history"]) == 1


async def test_stream(client):
    await utils.clear_iopub(client)
    client.execute("print('hi')")
    stdout, _ = await utils.assemble_output(client)
    assert stdout.startswith("hi")


@pytest.mark.parametrize("clear", [True, False])
async def test_display_data(kernel, client, clear: bool):
    await utils.clear_iopub(client)
    # kernel.display_formatter
    msg_id, _ = await utils.execute(
        client, f"from IPython.display import display; display(1, clear={clear})", clear_pub=False
    )
    await utils.check_pub_message(client, msg_id, execution_state="busy")
    await utils.check_pub_message(client, msg_id, msg_type="execute_input")
    if clear:
        await utils.check_pub_message(client, msg_id, msg_type="clear_output")
    await utils.check_pub_message(client, msg_id, msg_type="display_data", data={"text/plain": "1"})
    await utils.check_pub_message(client, msg_id, execution_state="idle")
