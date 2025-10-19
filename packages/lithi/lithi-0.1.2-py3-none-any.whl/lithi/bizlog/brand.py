"""Module for the applications's brand."""


def get_logo() -> str:
    """Return the printable logo."""
    logo = (
        ""
        "  ░█░░░▀█▀░▀█▀░█░█░▀█▀\n"
        "  ░█░░░░█░░░█░░█▀█░░█░\n"
        "  ░▀▀▀░▀▀▀░░▀░░▀░▀░▀▀▀\n"
    )
    logo += "ELF parser and memory live inspector\n"
    return logo
