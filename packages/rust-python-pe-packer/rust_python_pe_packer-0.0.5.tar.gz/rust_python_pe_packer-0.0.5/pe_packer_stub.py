import textwrap


def main() -> None:
    print(
        textwrap.dedent(
            """
            PE-Packer — Educational Metadata Stub
            -------------------------------------
            This PyPI package does not contain functional packing code.

            Educational source and instructions:
              https://github.com/codeamt/rust-python-pe-packer

            Safe install from source (non-functional by default):
              pip install git+https://github.com/codeamt/rust-python-pe-packer

            All packing functions are disabled by default and require explicit opt-in.
            See SECURITY.md and LICENSE-APPENDIX.md for details.
            """
        ).strip()
    )