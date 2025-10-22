# pytest-tui-runner

**Textual-based terminal UI for running pytest tests**

`pytest-tui-runner` is a plugin and standalone tool that provides an interactive **Textual User Interface (TUI)** for configuring and running Python tests using [pytest](https://pytest.org/).  
It allows developers to easily filter, parametrize, and execute tests directly from the terminal in a clear, interactive environment.

---

## Installation

You can install the package from PyPI:

```bash
pip install pytest-tui-runner
```

---


## Usage
```bash
pytest-tui run
```

Or you can run it with specific path to tests
```bash
pytest-tui run /path/to/your/tests
```

---

## Configuration

`pytest-tui-runner` is configured in the pytest_tui_runner folder, which you have to create in the whole project at the ROOT level.
In that folder, create a default_test.ya file and define your required test structure according to the template.

---

## License

This project is licensed under the **[MIT License]** - see the `LICENSE' file for more details..
