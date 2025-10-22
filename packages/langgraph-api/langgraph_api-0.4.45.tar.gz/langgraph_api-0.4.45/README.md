# LangGraph API

This package implements the LangGraph API for rapid development and testing. Build and iterate on LangGraph agents with a tight feedback loop. The server is backed by a predominently in-memory data store that is persisted to local disk when the server is restarted.

For production use, see the various [deployment options](https://langchain-ai.github.io/langgraph/concepts/deployment_options/) for the LangGraph API, which are backed by a production-grade database.

## Installation

Install the `langgraph-cli` package with the `inmem` extra. Your CLI version must be no lower than `0.1.55`.

```bash
pip install -U langgraph-cli[inmem]
```

## Quickstart

1. (Optional) Clone a starter template:

   ```bash
   langgraph new --template new-langgraph-project-python ./my-project
   cd my-project
   ```

   (Recommended) Use a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install .
   ```

2. Start the development server:

   ```shell
   langgraph dev --config ./langgraph.json
   ```

3. The server will launch, opening a browser window with the graph UI. Interact with your graph or make code edits; the server automatically reloads on changes.

## Usage

Start the development server:

```bash
langgraph dev
```

Your agent's state (threads, runs, assistants) persists in memory while the server is running - perfect for development and testing. Each run's state is tracked and can be inspected, making it easy to debug and improve your agent's behavior.

## How-To

#### Attaching a debugger
Debug mode lets you attach your IDE's debugger to the LangGraph API server to set breakpoints and step through your code line-by-line.

1. Install debugpy:

   ```bash
   pip install debugpy
   ```

2. Start the server in debug mode:

   ```bash
   langgraph dev --debug-port 5678
   ```

3. Configure your IDE:

   - **VS Code**: Add this launch configuration:
     ```json
     {
       "name": "Attach to LangGraph",
       "type": "debugpy",
       "request": "attach",
       "connect": {
                "host": "0.0.0.0",
                "port": 5678
            },
     }
     ```
   - **PyCharm**: Use "Attach to Process" and select the langgraph process

4. Set breakpoints in your graph code and start debugging.

## CLI options

```bash
langgraph dev [OPTIONS]
Options:
  --debug-port INTEGER         Enable remote debugging on specified port
  --no-browser                 Skip opening browser on startup
  --n-jobs-per-worker INTEGER  Maximum concurrent jobs per worker process
  --config PATH               Custom configuration file path
  --no-reload                 Disable code hot reloading
  --port INTEGER              HTTP server port (default: 8000)
  --host TEXT                 HTTP server host (default: localhost)
```

## License

This project is licensed under the Elastic License 2.0 - see the [LICENSE](./LICENSE) file for details.