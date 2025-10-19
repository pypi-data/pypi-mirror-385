## Installation

## Installing pipx
[`pipx`](https://pypa.github.io/pipx/) creates isolated environments to avoid conflicts with existing system packages.

=== "MacOS"
    In the terminal, execute:
    ```bash
    --8<-- "install_pipx_macos.sh"
    ```

=== "Linux"
    First, ensure Python is installed.

    Enter in the terminal:

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```

=== "Windows"
    First, install Python if it's not already installed.

    In the command prompt, type (if Python was installed from the Microsoft Store, use `python3` instead of `python`):

    ```bash
    python -m pip install --user pipx
    ```

## Installing `dictforge`:
In the terminal (command prompt), execute:

```bash
pipx install dictforge
```

## Kindle Previewer
DictForge invokes Amazon's `kindlegen` utility to generate Kindle dictionaries. Install
[Kindle Previewer 3](https://kdp.amazon.com/en_US/help/topic/G202131170) to bundle the
binary into your system PATH.

In newer versions of Kindle Previewer 3, Amazon has stopped distributing kindlegen as a separate utility — it is now embedded
within Kindle Previewer itself and is not installed globally on the system.

See in [Installing Kindlegen](https://www.jutoh.com/kindlegen.html) how to find the path.

Place the path before the language arguments:

```bash
dictforge --kindlegen-path="/Applications/Kindle Previewer 3.app/Contents/lib/fc/bin/kindlegen" sr en
```
