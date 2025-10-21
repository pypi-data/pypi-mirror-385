from . import hello, __version__

def main() -> None:
    print(hello())
    print(f"version: {__version__}")

