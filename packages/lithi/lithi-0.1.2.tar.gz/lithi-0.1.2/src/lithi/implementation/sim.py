"""Target for simulation."""

from lithi.interface.target import (
    BaseTarget,
    CoreRegister,
    MemoryArea,
    register_target,
)
from lithi.logger import logger


@register_target(name="sim", config_cls=None)
class SimulationTarget(BaseTarget):
    """The simulator target."""

    def __init__(self) -> None:
        """Initialize the object."""
        super().__init__()
        self._is_connected: bool = False
        self._is_stopped: bool = False
        self._core_registers: list[CoreRegister] = []
        logger.info("Initialised")

    def __del__(self) -> None:
        """Deinitialize the object."""
        logger.info("Deinitialised")

    def __str__(self) -> str:
        """Return a human-readable string representation of the object."""
        return "Simulator"

    def is_connected(self) -> bool:
        """Check connection."""
        return self._is_connected

    def connect(self) -> None:
        """Connect to the J-Link device if not already connected."""
        if self.is_connected():
            logger.warning("Already connected")
        else:
            self._is_connected = True

    def disconnect(self) -> None:
        """Close the connection to the target backend."""
        if not self.is_connected():
            logger.warning("Already disconnected")
        else:
            self._is_connected = False

    def is_stopped(self) -> bool:
        """Check if the target is currently stopped."""
        return self._is_stopped

    def stop(self) -> None:
        """Stop the target."""
        if self.is_stopped():
            logger.warning("Already stopped")
        else:
            self._is_stopped = True

    def run(self) -> None:
        """Resume execution on the target."""
        if not self.is_stopped():
            logger.warning("Already running")
        else:
            self._is_stopped = False

    def get_core_registers(self) -> list[CoreRegister]:
        """Get a list of the available core registers."""
        return self._core_registers

    def _read_coreregister(self, _: CoreRegister) -> int:
        """Read a single core register safely."""
        return self.__class__.UNKNOWN_BYTE

    def _read_memoryarea(self, memory: MemoryArea) -> list[int]:
        """Read a memory area safely."""
        result: list[int] = [self.__class__.UNKNOWN_BYTE] * memory.size
        return result
