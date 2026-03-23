# Dagster MCP Server and Components

## What is MCP?

The Model Context Protocol (MCP) is an open standard developed by Anthropic to connect large language models (LLMs) with external data sources in a secure, standardized way.

MCP standardizes the connection between AI agents and external services. Instead of every AI system learning how to talk to every data source, the external service provides an MCP interface.

Benefits of MCP:
- **Interoperability**: Any MCP-compatible AI can instantly integrate with the service.
- **Reduced Maintenance**: The service owner maintains the MCP interface, ensuring accuracy and reliability.
- **Future-proofing**: As AI systems evolve, the MCP layer stays consistent.

MCP shifts the integration burden from the AI agent to the service, making the ecosystem simpler, more reliable, and easier to maintain.

## Dagster's MCP Server

Dagster's MCP server integrates with `dg` and Dagster Components. These abstractions sit on top of core Dagster objects (such as assets) and make it much easier to build new features or integrate with tools and workflows, often with minimal code.

The combination of a rich core library paired with opinionated tooling is a perfect match for MCP. With a well-documented, structured library, MCP can gain a deep understanding of Dagster's capabilities.

### Installation

```bash
pip install mcp-server-dagster
# or
pip install "dg[mcp]"
```

### Configuration

You can install the MCP server through the `dg[mcp]` package, and easily enable it within your tool using:

```bash
dg mcp configure
```

### Example Usage

With the Dagster MCP configured, AI tools like Cursor know where to route requests and translate them to the correct `dg` CLI commands. For example:

- **Scaffolding**: "Can you scaffold me a new Dagster project named example-project" → uses `uvx -U create-dagster`
- **Adding integrations**: "Can you add dbt to my Dagster project" → uses dg commands to scaffold a dbt integration, generating just YAML config

### Composability

The Dagster MCP is composable. If you're using other tools like dbt, Snowflake, Airbyte, or any service that exposes an MCP interface, your AI assistant can seamlessly interact with all of them together.

This interoperability unlocks AI agents operating across your entire stack, coordinating multiple tools through a shared, universal protocol instead of stitching together brittle point-to-point integrations.

## Dagster Components and dg CLI

Dagster Components and the `dg` CLI are abstractions that sit on top of core Dagster objects (assets, resources, etc.). They provide:
- Opinionated scaffolding and project structure
- Minimal code for common integrations (dbt, etc.)
- YAML-based configuration for integrations
- Tighter guardrails for code quality and safety

This makes it much easier to build new features or integrate with tools and workflows, often with minimal code.
