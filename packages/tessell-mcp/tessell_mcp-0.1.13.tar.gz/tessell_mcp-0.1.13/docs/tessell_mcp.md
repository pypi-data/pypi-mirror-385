# Tessell MCP Server

**Tessell MCP Server** is your AI-powered command center for cloud data and services. It connects your favorite IDEs (like **VS Code**, **Cursor**) or chat-based clients (like **Claude**) to Tessell-—so you can manage everything using **natural language**.

With simple prompts, you can:

- Manage services, snapshots, and availability machines  
- Explore and operate databases (Oracle, PostgreSQL, and more)—on Tessell or anywhere else  
- Run queries, check health, and troubleshoot—without switching tools or writing scripts

Just describe what you want to do—**Tessell MCP Server takes care of the rest**.

## Why Use Tessell MCP Server?

- **Conversational Power**: Manage your cloud and databases using plain language—no scripts or CLI required  
- **Unified Control**: Access both Tessell-native and external databases from one place  
- **Instant Insights**: Query, analyze, and troubleshoot in seconds  
- **Secure & Local**: Your credentials stay safe—nothing leaves your environment unless you approve it  

## Installation & Configuration

### Requirements
- Tessell account with an active API key  
- Tenant API base URL and Tenant ID  
- Compatible MCP client (e.g., Claude Desktop, Cursor)

### Configuration
To set up the Tessell MCP Server, add the following configuration to your MCP client's configuration file (such as `mcp_config.json`):

```json
{
  "mcpServers": {
    "tessell": {
      "command": "uvx",
      "args": [
        "tessell-mcp@latest"
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

### Database Connections

Connect to your database by setting an environment variable with your connection string. The variable name must start with `CONNSTR_` (e.g., `CONNSTR_HR_DB`).

**Example:**
```json
"env": {
  "CONNSTR_ANALYTICS_DB": "postgresql://user:password@host:5432/database",
  "CONNSTR_HR_DB": "oracle://user:password@host:1521/service"
}
```

Tessell MCP supports PostgreSQL and Oracle, with MySQL and SQL Server coming soon. Use the standard URI format for your database engine.

Be sure to replace the placeholders with your actual database information and keep your credentials secure.


## What You Can Do

### Service

Manage your data services deployed on Tessell with ease - Discover services, manage snapshots, and control lifecycles—across clouds and environments—using simple prompts.

| Action                          | Example Prompt                                                    |
|----------------------------------|------------------------------------------------------------------|
| See all my services              | Show me all running services                                     |
| Get details about a service      | Show details for the 'hr' service                                |
| List databases in a service      | List all databases in the analytics service                      |
| Find a service by name           | Find all services with 'prod' in the name                        |
| Start/stop a service             | Stop the integration test service                                |
| Manage snapshots                 | Create a snapshot named 'pre-upgrade' for the hr availability machine |
| List snapshots                   | Show all snapshots for the analytics availability machine        |


### Database

Unlock the full potential of your databases—from provisioning and exploring metadata to running queries and troubleshooting performance, Tessell MCP Server simplifies every step of database interaction.

| Action                          | Example Prompt                                                    |
|----------------------------------|------------------------------------------------------------------|
| Create a new database (Postgres) | Create a db named prod_reporting with analytics connection       |
| List schemas in a database       | Show me all schemas in the analytics database                    |
| List tables/views in a schema    | List all tables and views in the public schema of sales          |
| Describe a table or view         | Describe the structure of the 'orders' table in reporting        |
| Get sample data                  | Show me 5 sample rows from the 'customers' table                 |
| Run a custom query               | Get top 10 transactions with amount greater than 1000            |
| See slowest queries              | What are the slowest queries running on analytics?               |
| Check database health            | Check the health of indexes and vacuum status in hr              |
| Explain a query plan             | Explain the query plan for 'SELECT * FROM sales WHERE region = 'US'' |

### Tessell Documentation

Get answers directly from Tessell’s documentation—search across product guides and configuration help, right from the MCP interface.

| Action                          | Example Prompt                                                    |
|----------------------------------|------------------------------------------------------------------|
| Search documentation             | What is Parameter Profile in Tessell?                            |
| Find setup instructions          | How do I configure IAM in Tessell?                               |
| List available features          | What can I do with Tessell's governance app?                     |


## Security Notes
- Tessell MCP Server is intended for local development and IDE integrations only.
- Keep your API key and tenant credentials secure and private.
- Review and approve all actions before allowing execution via the MCP client.
- Database connection files should be kept secure and not committed to version control.
