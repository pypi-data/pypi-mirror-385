# MCTS-Gen: A Generic MCTS Framework

This project provides a generic Monte Carlo Tree Search (MCTS) framework. Its core concept is the replacement of the Genetic Programming (GP) engine from `chess-ant` with a modern AI agent. While inspired by AlphaZero, it uses a simpler, decoupled approach: the standard UCT algorithm is augmented by an external AI agent that provides policy and value predictions.

## Features

-   **AI-Augmented UCT**: Utilizes the standard UCT algorithm. The AI agent enhances the search by providing value predictions and, most importantly, by performing **Policy Pruning**—narrowing the search space by supplying a pre-filtered list of promising moves.
-   **AI Agent Integration**: Exposes the MCTS engine as a set of tools, enabling seamless integration with AI agents like the Gemini CLI.
-   **Extensible Game Logic**: Easily add support for new games by creating a new game state module.
-   **Optional Dependencies**: Install support for specific games on demand (e.g., `pip install mcts-gen[shogi]`).

## Quickstart

### 1. Installation

#### Standard Installation

The core package can be installed directly using pip:
```bash
pip install mcts-gen
```

#### Installation with Game-Specific Dependencies

To include support for specific games, you can install optional dependencies.

-   **For Shogi support**:
    ```bash
    pip install mcts-gen[shogi]
    ```
    This installs the `python-shogi` library.

-   **For Chess support**:
    ```bash
    pip install mcts-gen[chess]
    ```
    This installs the `python-chess` library.

### 2. Server Setup for Gemini CLI

To allow the Gemini agent to use the MCTS-Gen tools, you must register the server in your `settings.json` file. This allows the Gemini CLI to automatically manage the server process and provide the necessary context files.

**Note on v0.0.2+**: As of version 0.0.2, the core agent instructions are built-in. Specifying a context file is no longer required for standard operation. Only configure the `context` block if you wish to provide *additional* instructions to the agent.

Create or update your `settings.json` file with the following configuration:

```json
{
  "context": {
    "fileName": [
      "src/mcts_gen/AGENTS.md",
      "GEMINI.md"
    ]
  },
  "mcpServers": {
    "mcts_gen_simulator_server": {
      "command": "python",
      "args": [
        "-m",
        "mcts_gen.fastmcp_server"
      ]
    }
  }
}
```

**Note**: The `context` block tells the Gemini CLI to load `AGENTS.md` (and `GEMINI.md` if it exists), which is crucial for the agent to understand how to use the tools.

You can place this `settings.json` file in one of two locations:

1.  **Project-Specific**: `./.gemini/settings.json` (inside this project directory)
2.  **Global**: `~/.gemini/settings.json` (in your home directory)

For an alternative setup method using the `fastmcp` command-line tool, please see the official guide:
- [Gemini CLI 🤝 FastMCP](https://gofastmcp.com/integrations/gemini-cli)

#### Installation with `uv` (Recommended)

For a faster and more modern package management experience, we recommend using `uv`.

1.  **Install `pipx` and `uv`**:
    ```bash
    # Install pipx (a tool to install and run Python applications in isolated environments)
    sudo apt install pipx

    # Install uv using pipx
    pipx install uv
    ```

2.  **Set up the environment and install `mcts-gen`**:
    ```bash
    # Create a virtual environment in your project directory
    uv venv

    # Activate the environment
    source .venv/bin/activate

    # Install mcts-gen with Shogi support
    uv pip install mcts-gen[shogi]
    ```
    To exit the virtual environment, simply run `deactivate`.

3.  **Configure `gemini-cli` with `fastmcp`**:
    Instead of manually editing `settings.json`, you can use the `fastmcp` command to automatically configure the tool server.
    ```bash
    fastmcp install gemini-cli .venv/lib/python3.12/site-packages/mcts_gen/fastmcp_server.py:mcp
    ```
    This command will automatically detect and configure the `mcts_gen` server, creating a `.gemini/settings.json` file for you.

    **Note on the `:mcp` suffix**: The `:mcp` at the end is required because `fastmcp_server.py` contains multiple objects. This suffix explicitly tells `fastmcp` which object is the MCP server instance to be run.

#### Agent Context Configuration with `uv`

**Note on v0.0.2+**: The instructions below are for older versions or for cases where you need to add custom, additional context. As of v0.0.2, specifying `AGENTS.md` is not required for the agent to function correctly.

If you installed the package using `uv` or `pip`, the `AGENTS.md` file is included inside the package. To allow the Gemini agent to use it, you need to specify its full path in your `.gemini/settings.json` file.

Add the path to the `context.fileName` list. The exact path may vary depending on your Python version and environment.

**Example `.gemini/settings.json`:**
```json
{
  "context": {
    "fileName": [
      ".venv/lib/python3.12/site-packages/mcts_gen/AGENTS.md",
      "GEMINI.md"
    ]
  },
  "mcpServers": {
    "mcts_gen_simulator_server": {
      "command": "uv",
      "args": [
        "run",
        "fastmcp",
        "run",
        ".venv/lib/python3.12/site-packages/mcts_gen/fastmcp_server.py:mcp"
      ]
    }
  }
}
```

## For Maintainers: How to Release a New Version

The package publication process is automated using GitHub Actions.

#### a) Releasing to TestPyPI (for testing)

To release a version to the TestPyPI repository for verification, create and push a git tag with a `-test` suffix.

```bash
# Example for version 0.1.0
git tag v0.1.0-test1
git push origin v0.1.0-test1
```

#### b) Releasing to PyPI (Official)

To perform an official release, create and push a git tag that follows the semantic versioning format (e.g., `vX.Y.Z`).

```bash
# Example for version 0.1.0
git tag v0.1.0
git push origin v0.1.0
```

## Development

### Testing

To run all tests:
```bash
pytest
```

## License

This project is licensed under the GPL-3.0-or-later license.
