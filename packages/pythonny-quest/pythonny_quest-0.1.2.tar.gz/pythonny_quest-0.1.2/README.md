# Pythonny Quest

## Quickstart

On Python >= 3.11 you can just `pip install pythonny-quest` and then launch your journey with the `pyquest` command. This should give you an iPython-like console with some hints in comment lines above the prompt.

## Contributing

If you want to contribute or modify the source code, make sure you have `uv` installed. 

### Install `uv`

If you do not have `uv` installed, you can use `curl` or `wget` within [`git-bash`](https://gitforwindows.org):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**OR**

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

You may need to relaunch your `git-bash` terminal before it will recognize your new `uv` command line command.

## Install `pythonny-quest` (`pyquest`)

Download the git repository:

```bash
git clone git@gitlab.com:hobs/pythonny-quest
cd pythonny-quest
```

Create and activate a Python 3.12 virtual environment within the `pythonny-quest/` folder:

```bash
uv venv -p 3.12
source .venv/bin/activate
```

Install pythonny-quest within your virtual environment:

```bash
uv pip install --editable .
```

Now whenever you run the `pyquest` command, you will be running the latest source code that you have edited within `src/pyquest/shell.py` starting with the `main()` function there.
