"""
Provides TypeScript specific instantiation of the LanguageServer class. Contains various configurations and settings specific to TypeScript.
"""

import asyncio
import json
import logging
import os
import pathlib
import shutil
import subprocess
from contextlib import asynccontextmanager
from typing import AsyncIterator

from scubalspy import scubalspy_types
from scubalspy.language_server import LanguageServer
from scubalspy.lsp_protocol_handler.lsp_constants import LSPConstants
from scubalspy.lsp_protocol_handler.lsp_types import InitializeParams
from scubalspy.lsp_protocol_handler.server import ProcessLaunchInfo
from scubalspy.scubalspy_config import ScubalspyConfig
from scubalspy.scubalspy_exceptions import ScubalspyException
from scubalspy.scubalspy_logger import ScubalspyLogger
from scubalspy.scubalspy_utils import PathUtils, PlatformId, PlatformUtils

# Conditionally import pwd module (Unix-only)
if not PlatformUtils.get_platform_id().value.startswith("win"):
    import pwd


class TypeScriptLanguageServer(LanguageServer):
    """
    Provides TypeScript specific instantiation of the LanguageServer class. Contains various configurations and settings specific to TypeScript.
    """

    def __init__(
        self,
        config: ScubalspyConfig,
        logger: ScubalspyLogger,
        repository_root_path: str,
    ):
        """
        Creates a TypeScriptLanguageServer instance. This class is not meant to be instantiated directly. Use LanguageServer.create() instead.
        """
        ts_lsp_executable_path = self.setup_runtime_dependencies(logger, config)
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=ts_lsp_executable_path, cwd=repository_root_path),
            "typescript",
        )
        self.server_ready = asyncio.Event()

    def setup_runtime_dependencies(
        self, logger: ScubalspyLogger, config: ScubalspyConfig
    ) -> str:
        """
        Setup runtime dependencies for TypeScript Language Server.
        """
        platform_id = PlatformUtils.get_platform_id()

        valid_platforms = [
            PlatformId.LINUX_x64,
            PlatformId.LINUX_arm64,
            PlatformId.OSX,
            PlatformId.OSX_x64,
            PlatformId.OSX_arm64,
            PlatformId.WIN_x64,
            PlatformId.WIN_arm64,
        ]
        assert (
            platform_id in valid_platforms
        ), f"Platform {platform_id} is not supported for scubalspy javascript/typescript at the moment"

        with open(
            os.path.join(os.path.dirname(__file__), "runtime_dependencies.json"), "r"
        ) as f:
            d = json.load(f)
            del d["_description"]

        runtime_dependencies = d.get("runtimeDependencies", [])
        tsserver_ls_dir = os.path.join(os.path.dirname(__file__), "static", "ts-lsp")
        tsserver_executable_path = os.path.join(
            tsserver_ls_dir, "typescript-language-server"
        )

        # Verify both node and npm are installed
        is_node_installed = shutil.which("node") is not None
        assert is_node_installed, "node is not installed or isn't in PATH. Please install NodeJS and try again."
        is_npm_installed = shutil.which("npm") is not None
        assert (
            is_npm_installed
        ), "npm is not installed or isn't in PATH. Please install npm and try again."

        # Install typescript and typescript-language-server if not already installed
        if not os.path.exists(tsserver_ls_dir):
            os.makedirs(tsserver_ls_dir, exist_ok=True)
            for dependency in runtime_dependencies:
                # Windows doesn't support the 'user' parameter and doesn't have pwd module
                if PlatformUtils.get_platform_id().value.startswith("win"):
                    subprocess.run(
                        dependency["command"],
                        shell=True,
                        check=True,
                        cwd=tsserver_ls_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    # On Unix-like systems, run as non-root user
                    user = pwd.getpwuid(os.getuid()).pw_name
                    subprocess.run(
                        dependency["command"],
                        shell=True,
                        check=True,
                        user=user,
                        cwd=tsserver_ls_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )

        tsserver_executable_path = os.path.join(
            tsserver_ls_dir, "node_modules", ".bin", "typescript-language-server"
        )
        assert os.path.exists(
            tsserver_executable_path
        ), "typescript-language-server executable not found. Please install typescript-language-server and try again."
        return f"{tsserver_executable_path} --stdio"

    def _get_initialize_params(self, repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the TypeScript Language Server.
        """
        with open(
            os.path.join(os.path.dirname(__file__), "initialize_params.json"), "r"
        ) as f:
            d = json.load(f)

        del d["_description"]

        d["processId"] = os.getpid()
        assert d["rootPath"] == "$rootPath"
        d["rootPath"] = repository_absolute_path

        assert d["rootUri"] == "$rootUri"
        d["rootUri"] = pathlib.Path(repository_absolute_path).as_uri()

        assert d["workspaceFolders"][0]["uri"] == "$uri"
        d["workspaceFolders"][0]["uri"] = pathlib.Path(
            repository_absolute_path
        ).as_uri()

        assert d["workspaceFolders"][0]["name"] == "$name"
        d["workspaceFolders"][0]["name"] = os.path.basename(repository_absolute_path)

        return d

    @asynccontextmanager
    async def start_server(self) -> AsyncIterator["TypeScriptLanguageServer"]:
        """
        Starts the TypeScript Language Server, waits for the server to be ready and yields the LanguageServer instance.

        Usage:
        ```
        async with lsp.start_server():
            # LanguageServer has been initialized and ready to serve requests
            await lsp.request_definition(...)
            await lsp.request_references(...)
            # Shutdown the LanguageServer on exit from scope
        # LanguageServer has been shutdown
        """

        async def register_capability_handler(params):
            assert "registrations" in params
            for registration in params["registrations"]:
                if registration["method"] == "workspace/executeCommand":
                    self.initialize_searcher_command_available.set()
                    # TypeScript doesn't have a direct equivalent to resolve_main_method
                    # You might want to set a different flag or remove this line
                    # self.resolve_main_method_available.set()
            return

        async def execute_client_command_handler(params):
            return []

        async def do_nothing(params):
            return

        async def window_log_message(msg):
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)

        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_request(
            "workspace/executeClientCommand", execute_client_command_handler
        )
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        async with super().start_server():
            self.logger.log("Starting TypeScript server process", logging.INFO)
            await self.server.start()
            initialize_params = self._get_initialize_params(self.repository_root_path)

            self.logger.log(
                "Sending initialize request from LSP client to LSP server and awaiting response",
                logging.INFO,
            )
            init_response = await self.server.send.initialize(initialize_params)

            # TypeScript-specific capability checks
            assert init_response["capabilities"]["textDocumentSync"] == 2
            assert "completionProvider" in init_response["capabilities"]
            assert init_response["capabilities"]["completionProvider"] == {
                "triggerCharacters": [".", '"', "'", "/", "@", "<"],
                "resolveProvider": True,
            }

            self.server.notify.initialized({})
            self.completions_available.set()

            # TypeScript server is typically ready immediately after initialization
            self.server_ready.set()
            await self.server_ready.wait()

            yield self

            await self.server.shutdown()
            await self.server.stop()

    async def request_definition(
        self, relative_file_path: str, line: int, column: int
    ) -> list[scubalspy_types.Location]:
        if not self.server_started:
            self.logger.log(
                "find_function_definition called before Language Server started",
                logging.ERROR,
            )
            raise ScubalspyException("Language Server not started")

        with self.open_file(relative_file_path):
            response = await self.server.send.execute_command(
                {
                    LSPConstants.COMMAND: "_typescript.goToSourceDefinition",
                    LSPConstants.ARGUMENTS: [
                        pathlib.Path(
                            str(
                                pathlib.PurePath(
                                    self.repository_root_path, relative_file_path
                                )
                            )
                        ).as_uri(),
                        {
                            LSPConstants.LINE: line,
                            LSPConstants.CHARACTER: column,
                        },
                    ],
                }
            )

        ret: list[scubalspy_types.Location] = []
        if isinstance(response, list):
            # response is either of type Location[] or LocationLink[]
            for item in response:
                assert isinstance(item, dict)
                if LSPConstants.URI in item and LSPConstants.RANGE in item:
                    new_item: scubalspy_types.Location = {}
                    new_item.update(item)
                    new_item["absolutePath"] = PathUtils.uri_to_path(new_item["uri"])
                    new_item["relativePath"] = PathUtils.get_relative_path(
                        new_item["absolutePath"], self.repository_root_path
                    )
                    ret.append(scubalspy_types.Location(new_item))
                elif (
                    LSPConstants.ORIGIN_SELECTION_RANGE in item
                    and LSPConstants.TARGET_URI in item
                    and LSPConstants.TARGET_RANGE in item
                    and LSPConstants.TARGET_SELECTION_RANGE in item
                ):
                    new_item: scubalspy_types.Location = {}
                    new_item["uri"] = item[LSPConstants.TARGET_URI]
                    new_item["absolutePath"] = PathUtils.uri_to_path(new_item["uri"])
                    new_item["relativePath"] = PathUtils.get_relative_path(
                        new_item["absolutePath"], self.repository_root_path
                    )
                    new_item["range"] = item[LSPConstants.TARGET_SELECTION_RANGE]
                    ret.append(scubalspy_types.Location(**new_item))
                else:
                    assert False, f"Unexpected response from Language Server: {item}"
        elif isinstance(response, dict):
            # response is of type Location
            assert LSPConstants.URI in response
            assert LSPConstants.RANGE in response

            new_item: scubalspy_types.Location = {}
            new_item.update(response)
            new_item["absolutePath"] = PathUtils.uri_to_path(new_item["uri"])
            new_item["relativePath"] = PathUtils.get_relative_path(
                new_item["absolutePath"], self.repository_root_path
            )
            ret.append(scubalspy_types.Location(**new_item))
        else:
            assert False, f"Unexpected response from Language Server: {response}"

        return ret
