"""Memory command."""

import argparse
import time
from dataclasses import dataclass
from typing import ClassVar

from lithi.bizlog.settings import Settings
from lithi.config import ConfigManager
from lithi.core.args import (
    Argument,
    ArgumentBoolean,
    ArgumentInt,
    ArgumentString,
)
from lithi.core.cli import Command
from lithi.interface.target import MemoryArea, TargetFactory


@dataclass
class MemoryCommand(Command):
    """Read memory given the address and the size."""

    name: ClassVar[str] = "mem"

    args: ClassVar[list[Argument]] = [
        ArgumentString(
            name="address", flag="a", default="0", description="Address in hex"
        ),
        ArgumentInt(
            name="size",
            flag="s",
            default=4,
            description="How many bytes to read",
        ),
        ArgumentBoolean(
            name="loop", flag="l", default=False, description="Run in a loop"
        ),
    ]

    def exec(self, args: argparse.Namespace) -> None:
        """Execute the command."""
        # Load the default target
        settings: Settings = ConfigManager.load()

        if settings.default.session_name is None:
            raise ValueError("No default session name configured")

        session = settings.sessions[settings.default.session_name]
        target = TargetFactory.create(session.target, session.config)

        # Use the target
        target.connect()
        memory = MemoryArea(address=int(args.address, 0), size=args.size)
        repeat_measurement = True
        while repeat_measurement:
            # Read memory
            if target.is_connected():
                value = target.read(memory)
                print(f"[{session.target}] {memory} = {memory.format(value)}")
            if args.loop:
                time.sleep(0.1)
            repeat_measurement = args.loop
