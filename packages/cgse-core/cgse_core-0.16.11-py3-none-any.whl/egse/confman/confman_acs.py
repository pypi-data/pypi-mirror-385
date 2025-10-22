import multiprocessing

from egse.async_control import AsyncControlServer
from egse.confman import AsyncConfigurationManagerProtocol
from egse.log import logging
from egse.settings import Settings

logger = logging.getLogger("egse.confman")

settings = Settings.load("Configuration Manager Control Server")

PROCESS_NAME = "cm_acs"


class AsyncConfigurationManager(AsyncControlServer):
    def __init__(self):

        multiprocessing.current_process().name = PROCESS_NAME

        super().__init__()

        self.logger = logger
        self.service_name = PROCESS_NAME
        self.service_type = settings.SERVICE_TYPE

        self.device_protocol = AsyncConfigurationManagerProtocol(self)

        self.logger.debug(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")

        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

        self.set_hk_delay(10.0)

        self.logger.info(f"CM housekeeping saved every {self.hk_delay / 1000:.1f} seconds.")
