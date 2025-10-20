import copy
import functools
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from string import Template
from typing import Callable, Literal, Union

import redis

from bec_lib.service_config import ServiceConfig
from bec_server.bec_server_utils.subprocess_launch import subprocess_start, subprocess_stop
from bec_server.bec_server_utils.tmux_launch import tmux_start, tmux_stop


class bcolors:
    """
    Colors for the terminal output.
    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


@dataclass
class TmuxSession:
    name: str = "bec"
    window_label: str = "BEC server"


@dataclass
class ServiceDesc:
    path: Template
    command: str
    tmux_session: TmuxSession = field(default_factory=TmuxSession)
    wait_func: Union[Callable, None] = None

    def __eq__(self, other):
        if isinstance(other, ServiceDesc):
            if other.path.template == self.path.template and self.command == other.command:
                if self.tmux_session.name == other.tmux_session.name:
                    if self.wait_func == other.wait_func:
                        return True
        return False


class ServiceHandler:
    """
    Service handler for the BEC server. This class is used to start, stop and restart the BEC server.
    Depending on the platform, the server is launched in a tmux session or in an iTerm2 session.
    """

    SERVICES = {
        "scan_server": ServiceDesc(Template("$base_path/scan_server"), "bec-scan-server"),
        "scan_bundler": ServiceDesc(Template("$base_path/scan_bundler"), "bec-scan-bundler"),
        "device_server": ServiceDesc(Template("$base_path/device_server"), "bec-device-server"),
        "file_writer": ServiceDesc(Template("$base_path/file_writer"), "bec-file-writer"),
        "scihub": ServiceDesc(Template("$base_path/scihub"), "bec-scihub"),
        "data_processing": ServiceDesc(Template("$base_path/data_processing"), "bec-dap"),
    }

    def __init__(
        self,
        bec_path: str,
        config_path: str = "",
        interface: Literal["tmux", "iterm2", "systemctl", "subprocess"] | None = None,
        start_redis: bool = False,
        no_persistence: bool = False,
    ):
        """

        Args:
            bec_path (str): Path to the BEC source code
            config_path (str): Path to the config file
            interface (str): Interface to use to start the BEC server. Can be "tmux", "iterm2", "systemctl" or "subprocess" (default: None)
            start_redis (bool): if True, start Redis server(s) with info from config (default: do not start Redis)
            no_persistence (bool): if True, do not save or load rdb file (default: do not disable persistence)
        """
        self.bec_path = bec_path
        self.config_path = config_path
        self.interface = interface
        self.start_redis = start_redis
        self.no_persistence = no_persistence

        if self.interface is None:
            self._detect_available_interfaces()

    def _detect_available_interfaces(self):
        # check if the systemctl command "bec_server" is available
        try:
            out = subprocess.run(["systemctl", "list-unit-files", "bec-server.service"], check=True)
            if out.returncode == 0:
                default_interface = "systemctl"
                print("Using systemctl to communicate with the BEC server.")
            else:
                default_interface = "tmux"
        except Exception:
            default_interface = "tmux"

        if default_interface == "systemctl" and os.environ.get("INVOCATION_ID"):
            # we are already within a systemd service, so we cannot use systemctl to start the BEC server
            default_interface = "tmux"

        # check if we are on MacOS and if so, check if we have iTerm2 installed
        if sys.platform == "darwin":
            try:
                import iterm2
            except ImportError:
                self.interface = default_interface
            else:
                self.interface = "iterm2"
        else:
            self.interface = default_interface

    def start(self) -> list:
        """
        Start the BEC server using the available interface.
        """

        def wait_ready(redis_host_port, key=None):
            while True:
                r = redis.from_url(f"redis://{redis_host_port}")
                try:
                    answer = r.ping() if key is None else r.get(key)
                except redis.exceptions.ConnectionError:
                    time.sleep(0.1)
                else:
                    if answer:
                        break

        services = {}
        if self.start_redis:
            config = ServiceConfig(self.config_path)
            redis_host_port = config.redis
            redis_port = redis_host_port.split(":")[-1]

            base_redis_cmd = f"redis-server --port {redis_port}"
            if self.no_persistence:
                redis_cmd = f"{base_redis_cmd} --save '' --dbfilename ''"
            else:
                redis_cmd = base_redis_cmd

            services.update(
                {
                    "redis": ServiceDesc(
                        Template(""),
                        redis_cmd,
                        TmuxSession("bec-redis", "BEC Redis servers"),
                        wait_func=functools.partial(wait_ready, redis_host_port),
                    )
                }
            )

        # redis must be started first ;
        # add to services dictionary
        for service_name, service_config in copy.deepcopy(self.SERVICES).items():
            services[service_name] = service_config
            if self.config_path:
                service_config.command += f" --config {self.config_path}"

        if self.interface == "tmux":
            print("Starting BEC server using tmux...")
            tmux_start(self.bec_path, services)
            print(
                f"{bcolors.OKCYAN}{bcolors.BOLD}Use `tmux attach -t bec` to attach to the BEC server. Once connected, use `ctrl+b d` to detach again.{bcolors.ENDC}"
            )
            return []
        if self.interface == "iterm2":
            return []
        if self.interface == "systemctl":
            subprocess.run(["sudo", "systemctl", "start", "bec-server.service"], check=True)
            return []
        if self.interface == "subprocess":
            return subprocess_start(self.bec_path, services)

        raise ValueError(
            f"Unsupported interface: {self.interface}. Supported interfaces are: tmux, iterm2, systemctl, subprocess"
        )

    def stop(self, processes=None):
        """
        Stop the BEC server using the available interface.
        """
        print("Stopping BEC server...")
        if self.interface == "tmux":
            tmux_stop("bec-redis")
            tmux_stop("bec")
        elif self.interface == "iterm2":
            pass
        elif self.interface == "systemctl":
            subprocess.run(["sudo", "systemctl", "stop", "bec-server.service"], check=True)
        elif self.interface == "subprocess":
            subprocess_stop(processes)
        else:
            raise ValueError(
                f"Unsupported interface: {self.interface}. Supported interfaces are: tmux, iterm2, systemctl, subprocess"
            )

    def restart(self):
        """
        Restart the BEC server using the available interface.
        """
        print("Restarting BEC server...")
        self.stop()
        self.start()
