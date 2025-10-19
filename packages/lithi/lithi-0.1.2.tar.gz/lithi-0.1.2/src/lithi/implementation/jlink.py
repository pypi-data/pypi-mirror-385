"""Target for Segger's JLink debugger."""

import threading
import time
from typing import cast

import pylink
from pydantic import BaseModel

from lithi.interface.target import (
    BaseTarget,
    CoreRegister,
    MemoryArea,
    register_target,
)
from lithi.logger import logger


class JLinkConfig(BaseModel):
    """
    Configuration for a J-Link target.

    Attributes:
        device: The target device name (e.g., "STM32F072RB").
        speed: Connection speed in kHz. Defaults to 4000.
        autoconnect: Whether to automatically connect on initialization.
                     Defaults to True. Can be set to None for
                     optional behavior.
    """

    device: str
    speed: int = 4000
    autoconnect: bool | None = True


@register_target(name="jlink", config_cls=JLinkConfig)
class JLinkTarget(BaseTarget):
    """Represent the Segger's JLink debugger."""

    def __init__(self, config: JLinkConfig) -> None:
        """Initialize the object."""
        super().__init__(config)
        self.speed = config.speed
        self.device = config.device

        self.jlink = pylink.JLink()
        self.jlink.disable_dialog_boxes()
        self.jlink.exec_command("SuppressGUI 1")
        self.core_registers: dict[str, int] = {}

        self.is_auto_connect_enabled = config.autoconnect
        self.lock = threading.RLock()

        # Start background thread
        self.thread = threading.Thread(
            target=self._connector_loop, daemon=True
        )
        logger.info("Initialised")
        self.thread.start()

    def __del__(self) -> None:
        """Stop auto-connect and close J-Link safely."""
        self.is_auto_connect_enabled = False

        # Wait for background thread to finish
        if self.thread.is_alive():
            self.thread.join(timeout=0.5)

        if self.jlink:
            try:
                self.jlink.close()
                logger.info("Closed J-Link")
            except pylink.errors.JLinkException as error:
                logger.error("Failed to close J-Link: %s", error)
            finally:
                self.jlink = None

        logger.info("Deinitialised")

    def __str__(self) -> str:
        """Return a human-readable string representation of the object."""
        with self.lock:
            is_target_connected = self.jlink.target_connected()
            is_halted = None
            if is_target_connected:
                is_halted = self.jlink.halted()
            return (
                f"Status: jlink: {self.jlink.connected()} "
                f"target: {is_target_connected} "
                f"isHalted: {is_halted}"
            )

    def is_connected(self) -> bool:
        """Check connection with the target backend."""
        with self.lock:
            return self.jlink is not None and self.jlink.connected()

    def connect(self) -> None:
        """Connect to the J-Link device if not already connected."""
        with self.lock:
            if self.is_connected():
                logger.warning("Already connected")
                return

            # Create new JLink instance
            self.jlink = pylink.JLink()
            self.jlink.disable_dialog_boxes()
            self.jlink.exec_command("SuppressGUI 1")
            logger.info("Trying to reconnect")
            try:
                self.jlink.open()
                logger.info("Opened J-Link")
                try:
                    self.jlink.connect(self.device, speed=self.speed)
                    self._populate_core_regs()
                    logger.info("Connected")
                except pylink.errors.JLinkException as connect_error:
                    logger.error("Failed to connect: %s", connect_error)
                    # Attempt to close cleanly
                    try:
                        self.jlink.close()
                        logger.info("Closed J-Link after failed connect")
                    except pylink.errors.JLinkException as close_error:
                        logger.error(
                            "Failed to close after failed connect: %s",
                            close_error,
                        )
            except pylink.errors.JLinkException as open_error:
                logger.error("Failed to open J-Link: %s", open_error)

    def disconnect(self) -> None:
        """Close the connection to the target backend."""
        raise NotImplementedError

    def is_stopped(self) -> bool:
        """Check if the target is currently stopped."""
        with self.lock:
            return cast(bool, self.jlink.halted())

    def stop(self) -> None:
        """Stop the target."""
        with self.lock:
            self.jlink.halt()

    def run(self) -> None:
        """Resume execution on the target."""
        with self.lock:
            self.jlink.restart()

    def _populate_core_regs(self) -> None:
        """Populate the core registers."""
        if not self.core_registers:
            with self.lock:
                for reg_id in self.jlink.register_list():
                    reg_name = self.jlink.register_name(reg_id)
                    self.core_registers[reg_name] = reg_id
                    # logger.info(
                    #     f"name: {reg_name} id: {reg_id}") # noqa: ERA001
                logger.info("Populated core registers")

    def get_core_registers(self) -> list[CoreRegister]:
        """Get a list of the available core registers."""
        with self.lock:
            registers = []
            for reg_id in self.jlink.register_list():
                reg_name = self.jlink.register_name(reg_id)
                # print(f"Reg: {name} = {hex(value)}") # noqa: ERA001
                reg = CoreRegister(reg_name)
                registers.append(reg)
                self.core_registers[reg_name] = reg_id
            return registers

    def _read_coreregister(self, register: CoreRegister) -> int:
        """Read a single core register safely."""
        reg_id = self.core_registers[register.name]
        value = self.__class__.UNKNOWN_BYTE
        with self.lock:
            was_stopped = self.is_stopped()
            if not was_stopped:
                self.stop()
            try:
                value = self.jlink.register_read(reg_id)
            except pylink.errors.JLinkException as error:
                logger.error(
                    "Failed to read register %s: %s", register.name, error
                )
            finally:
                if not was_stopped:
                    self.run()
        return value

    def _read_memoryarea(self, memory: MemoryArea) -> list[int]:
        """Read a memory area safely."""
        result: list[int] = []
        with self.lock:
            try:
                result = self.jlink.memory_read8(memory.address, memory.size)
            except pylink.errors.JLinkException as error:
                logger.error(
                    "Failed to read memory at address 0x%X: %s",
                    memory.address,
                    error,
                )
        return result

    def _connector_loop(self) -> None:
        """Background thread that ensures J-Link is connected."""
        while self.is_auto_connect_enabled:
            with self.lock:
                if self.jlink is not None and not self.is_connected():
                    try:
                        self.connect()
                    except pylink.errors.JLinkException as error:
                        logger.warning("Background connect failed: %s", error)
            time.sleep(0.1)
