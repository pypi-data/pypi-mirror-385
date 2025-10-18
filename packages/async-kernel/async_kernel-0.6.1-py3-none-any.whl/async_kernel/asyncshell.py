from __future__ import annotations

import builtins
import json
import pathlib
import sys
from typing import TYPE_CHECKING, Any, ClassVar, Literal

import anyio
import IPython.core.release
from IPython.core.displayhook import DisplayHook
from IPython.core.displaypub import DisplayPublisher
from IPython.core.interactiveshell import ExecutionResult, InteractiveShell, InteractiveShellABC
from IPython.core.magic import Magics, line_magic, magics_class
from jupyter_client.jsonutil import json_default
from jupyter_core.paths import jupyter_runtime_dir
from traitlets import CFloat, Dict, Instance, Type, default, observe
from typing_extensions import override

from async_kernel import utils
from async_kernel.caller import Caller
from async_kernel.compiler import XCachingCompiler
from async_kernel.typing import MetadataKeys, Tags

if TYPE_CHECKING:
    from collections.abc import Callable

    from async_kernel.kernel import Kernel


__all__ = ["AsyncDisplayHook", "AsyncDisplayPublisher", "AsyncInteractiveShell"]


class AsyncDisplayHook(DisplayHook):
    """
    A displayhook subclass that publishes data using ZeroMQ.

    This is intended to work with an InteractiveShell instance. It sends a dict of different
    representations of the object."""

    kernel: Instance[Kernel] = Instance("async_kernel.Kernel", ())
    content: Dict[str, Any] = Dict()

    @property
    @override
    def prompt_count(self) -> int:
        return self.kernel.execution_count

    @override
    def start_displayhook(self) -> None:
        """Start the display hook."""
        self.content = {}

    @override
    def write_output_prompt(self) -> None:
        """Write the output prompt."""
        self.content["execution_count"] = self.prompt_count

    @override
    def write_format_data(self, format_dict, md_dict=None) -> None:
        """Write format data to the message."""
        self.content["data"] = format_dict
        self.content["metadata"] = md_dict

    @override
    def finish_displayhook(self) -> None:
        """Finish up all displayhook activities."""
        if self.content:
            self.kernel.iopub_send("display_data", content=self.content)
            self.content = {}


class AsyncDisplayPublisher(DisplayPublisher):
    """A display publisher that publishes data using a ZeroMQ PUB socket."""

    topic: ClassVar = b"display_data"

    def __init__(self, shell=None, *args, **kwargs) -> None:
        super().__init__(shell, *args, **kwargs)
        self._hooks = []

    @override
    def publish(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        data: dict[str, Any],
        metadata: dict | None = None,
        *,
        transient: dict | None = None,
        update: bool = False,
        **kwargs,
    ) -> None:
        """
        Publish a display-data message.

        Args:
            data: A mime-bundle dict, keyed by mime-type.
            metadata: Metadata associated with the data.
            transient: Transient data that may only be relevant during a live display, such as display_id.
                Transient data should not be persisted to documents.
            update: If True, send an update_display_data message instead of display_data.

        [Reference](https://jupyter-client.readthedocs.io/en/stable/messaging.html#update-display-data)
        """
        content = {"data": data, "metadata": metadata or {}, "transient": transient or {}} | kwargs
        msg_type = "update_display_data" if update else "display_data"
        msg = utils.get_kernel().session.msg(msg_type, content, parent=utils.get_parent())  # pyright: ignore[reportArgumentType]
        for hook in self._hooks:
            try:
                msg = hook(msg)
            except Exception:
                pass
            if msg is None:
                return
        utils.get_kernel().iopub_send(msg)

    @override
    def clear_output(self, wait: bool = False) -> None:
        """
        Clear output associated with the current execution (cell).

        Args:
            wait: If True, the output will not be cleared immediately,
                instead waiting for the next display before clearing.
                This reduces bounce during repeated clear & display loops.
        """
        utils.get_kernel().iopub_send(msg_or_type="clear_output", content={"wait": wait}, ident=self.topic)

    def register_hook(self, hook: Callable[[dict], dict | None]) -> None:
        """Register a hook for when publish is called.

        The hook should return the message or None.
        Only return `None` when the message should *not* be sent.
        """
        self._hooks.append(hook)

    def unregister_hook(self, hook: Callable[[dict], dict | None]) -> None:
        while hook in self._hooks:
            self._hooks.remove(hook)


class AsyncInteractiveShell(InteractiveShell):
    """
    An [IPython InteractiveShell][IPython.core.interactiveshell.InteractiveShell] modified to work with [Async kernel][async_kernel.Kernel].

    !!! note "Notable differences"

        - All [execute requests][async_kernel.Kernel.execute_request] are run asynchronously.
        - Supports a soft timeout with the metadata {"timeout":<value in seconds>}[^1].

            [^1]: When the execution time exceeds the timeout value, the code execution will "move on".
        - Not all features are support (see "not-supported" features listed below).

    """

    displayhook_class = Type(AsyncDisplayHook)
    display_pub_class = Type(AsyncDisplayPublisher)
    displayhook: Instance[AsyncDisplayHook]
    display_pub: Instance[AsyncDisplayPublisher]
    compiler_class = Type(XCachingCompiler)
    compile: Instance[XCachingCompiler]
    user_ns_hidden = Dict()
    _main_mod_cache = Dict()

    execute_request_timeout = CFloat(default_value=None, allow_none=True)
    "A timeout in seconds to complete [execute requests][async_kernel.Kernel.execute_request]."

    run_cell = None  # pyright: ignore[reportAssignmentType]
    "**not-supported**"
    should_run_async = None  # pyright: ignore[reportAssignmentType]
    loop_runner_map = None
    "**not-supported**"
    loop_runner = None
    "**not-supported**"
    debug = None
    "**not-supported**"
    readline_use = False
    "**not-supported**"
    autoindent = False
    "**not-supported**"

    @default("banner1")
    def _default_banner1(self) -> str:
        return (
            f"Python {sys.version}\n"
            f"Async kernel ({self.kernel.kernel_name})\n"
            f"IPython shell {IPython.core.release.version}\n"
        )

    @property
    def kernel(self) -> Kernel:
        "The current kernel."
        return utils.get_kernel()

    @observe("exit_now")
    def _update_exit_now(self, _) -> None:
        """Stop eventloop when `exit_now` fires."""
        if self.exit_now:
            self.kernel.stop()

    def ask_exit(self) -> None:
        if self.kernel.raw_input("Are you sure you want to stop the kernel?\ny/[n]\n") == "y":
            self.exit_now = True

    @override
    def init_create_namespaces(self, user_module=None, user_ns=None) -> None:
        return

    @override
    def save_sys_module_state(self) -> None:
        return

    @override
    def init_sys_modules(self) -> None:
        return

    @property
    @override
    def execution_count(self) -> int:
        return self.kernel.execution_count

    @execution_count.setter
    def execution_count(self, value) -> None:
        return

    @property
    @override
    def user_ns(self) -> dict[Any, Any]:
        if not hasattr(self, "_user_ns"):
            self.user_ns = {}
        return self._user_ns

    @user_ns.setter
    def user_ns(self, ns: dict) -> None:
        assert hasattr(ns, "clear")
        assert isinstance(ns, dict)
        self._user_ns = ns
        self.init_user_ns()

    @property
    @override
    def user_global_ns(self) -> dict[Any, Any]:
        return self.user_ns

    @property
    @override
    def ns_table(self) -> dict[str, dict[Any, Any] | dict[str, Any]]:
        return {"user_global": self.user_ns, "user_local": self.user_ns, "builtin": builtins.__dict__}

    @override
    async def run_cell_async(
        self,
        raw_cell: str,
        store_history=False,
        silent=False,
        shell_futures=True,
        *,
        transformed_cell: str | None = None,
        preprocessing_exc_tuple: tuple | None = None,
        cell_id: str | None = None,
    ) -> ExecutionResult:
        """
        Run a complete IPython cell asynchronously.

        This function runs [execute requests][async_kernel.Kernel.execute_request] for the kernel
        wrapping [InteractiveShell][IPython.core.interactiveshell.InteractiveShell.run_cell_async].
        """
        with anyio.fail_after(delay=utils.get_execute_request_timeout()):
            result: ExecutionResult = await super().run_cell_async(
                raw_cell=raw_cell,
                store_history=store_history,
                silent=silent,
                shell_futures=shell_futures,
                transformed_cell=transformed_cell,
                preprocessing_exc_tuple=preprocessing_exc_tuple,
                cell_id=cell_id,
            )
        self.events.trigger("post_execute")
        if not silent:
            self.events.trigger("post_run_cell", result)
        return result

    @override
    def _showtraceback(self, etype, evalue, stb) -> None:
        if Tags.suppress_error in utils.get_tags():
            if msg := utils.get_metadata().get(MetadataKeys.suppress_error_message, "⚠"):
                print(msg)
            return
        if utils.get_execute_request_timeout() is not None and etype is anyio.get_cancelled_exc_class():
            etype, evalue, stb = TimeoutError, "Cell execute timeout", []
        self.kernel.iopub_send(
            msg_or_type="error",
            content={"traceback": stb, "ename": str(etype.__name__), "evalue": str(evalue)},
        )

    @override
    def init_magics(self) -> None:
        """Initialize magics."""
        super().init_magics()
        self.register_magics(KernelMagics)

    @override
    def enable_gui(self, gui=None) -> None:
        pass


@magics_class
class KernelMagics(Magics):
    """Extra magics for async kernel."""

    @line_magic
    def connect_info(self, _) -> None:
        """Print information for connecting other clients to this kernel."""
        kernel = utils.get_kernel()
        connection_file = pathlib.Path(kernel.connection_file)
        # if it's in the default dir, truncate to basename
        if jupyter_runtime_dir() == str(connection_file.parent):
            connection_file = connection_file.name
        info = kernel.get_connection_info()
        print(
            json.dumps(info, indent=2, default=json_default),
            "Paste the above JSON into a file, and connect with:\n"
            + "    $> jupyter <app> --existing <file>\n"
            + "or, if you are local, you can connect with just:\n"
            + f"    $> jupyter <app> --existing {connection_file}\n"
            + "or even just:\n"
            + "    $> jupyter <app> --existing\n"
            + "if this is the most recent Jupyter kernel you have started.",
        )

    @line_magic
    def callers(self, _) -> None:
        "Print a table of [Callers][async_kernel.Caller], indicating its status including:  -running - protected - on the current thread."
        lines = ["\t".join(["Running", "Protected", "\t", "Name"]), "─" * 70]
        for caller in Caller.all_callers(running_only=False):
            symbol = "   ✓" if caller.running else "   ✗"
            current_thread: Literal["← current thread", ""] = "← current thread" if caller is Caller() else ""
            protected = "   🔐" if caller.protected else ""
            lines.append("\t".join([symbol, protected, "", caller.thread.name, current_thread]))
        print(*lines, sep="\n")


InteractiveShellABC.register(AsyncInteractiveShell)
