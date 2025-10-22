# Developer Guide

This README is intended for developers and contributors.

- **User Guide & Local Usage:** For end-user documentation and local MCP server usage, see [`docs/tessell_mcp.md`](docs/tessell_mcp.md).
- **Building & Publishing:** For instructions on building the package and publishing to PyPI, see [`docs/publish_pypi.md`](docs/publish_pypi.md).
- **Docs Search Deployment:** For deployment and configuration of the Docs Search workflow (AWS Bedrock KB, OpenSearch, Lambda), see [`docs/README.docs_search_deployment.md`](docs/README.docs_search_deployment.md).
- **Contributing:** See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines. This applies to both human contributors and AI copilots.

## Code Structure

- `mcp_core/` — Common core logic and utilities for both local MCP and AWS Lambda deployments
- `api_client/` — Common API client code used by both local MCP and AWS Lambda
- `tessell_mcp/` — Root package for the local MCP server (entrypoint: `tessell_mcp/main.py`)
- `app.py` — AWS Lambda entrypoint for serverless deployment
- `docs_lambda.py` — AWS Lambda handler for documentation search (see Docs Search Deployment)
- `docs/` — Documentation, including user-facing instructions in `tessell_mcp.md`

## Running the Tessell MCP Server

For full details on running and configuring the Tessell MCP Server in local mode, see the package documentation in `docs/tessell_mcp.md`.

### Quick Start (Local Mode)

You can test the Tessell MCP server using your MCP client config with a local package (wheel file):

```json
{
  "mcpServers": {
    "tessell": {
      "command": "uvx",
      "args": [
        "/absolute/path/to/your/dist/tessell_mcp-1.0.0-py3-none-any.whl"
      ],
      "env": {
        "TESSELL_API_BASE": "{your-tenant-api-url}",
        "TESSELL_API_KEY": "{your-api-key}",
        "TESSELL_TENANT_ID": "{your-tenant-id}"
      }
    }
  }
}
```
- This installs and runs the MCP server from your locally built wheel file (no need to publish to PyPI).

Replace the environment variables and paths with your actual values.

For more usage instructions, features, and security notes, see `docs/tessell_mcp.md`.

If you are an end user, you will typically configure your MCP client to use the published PyPI package (e.g., `tessell-mcp@latest`), as described in the user guide (`docs/tessell_mcp.md`).

## AWS Lambda Entrypoint

The file `app.py` serves as the entry point for deploying the Tessell MCP Server as an AWS Lambda function. Use this file when you want to run the MCP server in a serverless environment. Configure your Lambda environment variables as needed for your Tessell tenant.

For local development and integration with MCP clients, use the local mode instructions above.


## [ARCHIVED] Generate the SDK Folder

> **Note:** This section is archived and not used in the current workflow.

To generate a Python SDK from your OpenAPI specification and use it in this project:

1. **Choose a name for your SDK output folder.**
   - Example: `sdk/tessell_sdk`
2. **Place your OpenAPI YAML file** (e.g., `api_spec.yaml`) in the project root (same level as `pyproject.toml`).
3. **Generate the SDK using OpenAPI Generator:**
   ```sh
   mkdir -p sdk
   openapi-generator generate \
     -i api_spec.yaml \
     -g python \
     -o sdk/tessell_sdk
   ```
   - `-i api_spec.yaml` — Path to your OpenAPI spec file.
   - `-g python` — Generate a Python client.
   - `-o sdk/tessell_sdk` — Output directory for the generated SDK.

4. **Verify the output:**
   You should see a structure like:
   ```
   sdk/tessell_sdk/
   ├── README.md
   ├── setup.py
   ├── tessell_sdk/
   │   ├── __init__.py
   │   ├── configuration.py
   │   ├── api_client.py
   │   ├── api/
   │   │   ├── default_api.py
   │   │   └── ...
   │   ├── model/
   │   │   └── ...
   │   └── rest.py
   └── tests/
       └── ...
   ```

5. **(Optional) Install the SDK locally for development:**
   ```sh
   cd sdk/tessell_sdk
   pip install -e .
   ```
   This allows you to import the SDK in your project or Python REPL:
   ```python
   import tessell_sdk
   # Use the SDK as needed
   ```

6. **Regenerate the SDK whenever your OpenAPI spec changes** to keep your client up to date.

> **Tip:** You can add the SDK folder (e.g., `sdk/tessell_sdk`) to your `.gitignore` if you want to avoid committing generated code, or commit it for reproducibility.