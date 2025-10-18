# Container Manager MCP Server

![PyPI - Version](https://img.shields.io/pypi/v/container-manager-mcp)
![PyPI - Downloads](https://img.shields.io/pypi/dd/container-manager-mcp)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/container-manager-mcp)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/container-manager-mcp)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/container-manager-mcp)
![PyPI - License](https://img.shields.io/pypi/l/container-manager-mcp)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/container-manager-mcp)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/container-manager-mcp)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/container-manager-mcp)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/container-manager-mcp)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/container-manager-mcp)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/container-manager-mcp)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/container-manager-mcp)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/container-manager-mcp)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/container-manager-mcp)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/container-manager-mcp)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/container-manager-mcp)

*Version: 1.1.9*

Container Manager MCP Server provides a robust interface to manage Docker and Podman containers, networks, volumes, and Docker Swarm services through a FastMCP server, enabling programmatic and remote container management.

This repository is actively maintained - Contributions are welcome!

## Features

- Manage Docker and Podman containers, images, volumes, and networks
- Support for Docker Swarm operations
- Support for Docker Compose and Podman Compose operations
- FastMCP server for remote API access
- Comprehensive logging and error handling
- Extensible architecture for additional container runtimes

<details>
  <summary><b>Usage:</b></summary>

### MCP CLI

| Short Flag | Long Flag                          | Description                                                                 |
|------------|------------------------------------|-----------------------------------------------------------------------------|
| -h         | --help                             | Display help information                                                    |
| -t         | --transport                        | Transport method: 'stdio', 'http', or 'sse' [legacy] (default: stdio)       |
| -s         | --host                             | Host address for HTTP transport (default: 0.0.0.0)                          |
| -p         | --port                             | Port number for HTTP transport (default: 8000)                              |
|            | --auth-type                        | Authentication type: 'none', 'static', 'jwt', 'oauth-proxy', 'oidc-proxy', 'remote-oauth' (default: none) |
|            | --token-jwks-uri                   | JWKS URI for JWT verification                                              |
|            | --token-issuer                     | Issuer for JWT verification                                                |
|            | --token-audience                   | Audience for JWT verification                                              |
|            | --oauth-upstream-auth-endpoint     | Upstream authorization endpoint for OAuth Proxy                             |
|            | --oauth-upstream-token-endpoint    | Upstream token endpoint for OAuth Proxy                                    |
|            | --oauth-upstream-client-id         | Upstream client ID for OAuth Proxy                                         |
|            | --oauth-upstream-client-secret     | Upstream client secret for OAuth Proxy                                     |
|            | --oauth-base-url                   | Base URL for OAuth Proxy                                                   |
|            | --oidc-config-url                  | OIDC configuration URL                                                     |
|            | --oidc-client-id                   | OIDC client ID                                                             |
|            | --oidc-client-secret               | OIDC client secret                                                         |
|            | --oidc-base-url                    | Base URL for OIDC Proxy                                                    |
|            | --remote-auth-servers              | Comma-separated list of authorization servers for Remote OAuth             |
|            | --remote-base-url                  | Base URL for Remote OAuth                                                  |
|            | --allowed-client-redirect-uris     | Comma-separated list of allowed client redirect URIs                       |
|            | --eunomia-type                     | Eunomia authorization type: 'none', 'embedded', 'remote' (default: none)   |
|            | --eunomia-policy-file              | Policy file for embedded Eunomia (default: mcp_policies.json)              |
|            | --eunomia-remote-url               | URL for remote Eunomia server                                              |


### Using as an MCP Server

The MCP Server can be run in two modes: `stdio` (for local testing) or `http` (for networked access). To start the server, use the following commands:

#### Run in stdio mode (default):
```bash
container-manager-mcp
```

#### Run in HTTP mode:
```bash
container-manager-mcp --transport "http"  --host "0.0.0.0"  --port "8000"
```

### Available MCP Tools
- `get_version`: Retrieve version information of the container runtime
- `get_info`: Get system information about the container runtime
- `list_images`: List all available images
- `pull_image`: Pull an image from a registry
- `remove_image`: Remove an image
- `list_containers`: List running or all containers
- `run_container`: Run a new container
- `stop_container`: Stop a running container
- `remove_container`: Remove a container
- `get_container_logs`: Retrieve logs from a container
- `exec_in_container`: Execute a command in a container
- `list_volumes`: List all volumes
- `create_volume`: Create a new volume
- `remove_volume`: Remove a volume
- `list_networks`: List all networks
- `create_network`: Create a new network
- `remove_network`: Remove a network
- `compose_up`: Start services defined in a Compose file
- `compose_down`: Stop and remove services defined in a Compose file
- `compose_ps`: List containers for a Compose project
- `compose_logs`: View logs for a Compose project or specific service
- `init_swarm`: Initialize a Docker Swarm
- `leave_swarm`: Leave a Docker Swarm
- `list_nodes`: List nodes in a Docker Swarm
- `list_services`: List services in a Docker Swarm
- `create_service`: Create a new service in a Docker Swarm
- `remove_service`: Remove a service from a Docker Swarm

### Deploy MCP Server as a Service

The ServiceNow MCP server can be deployed using Docker, with configurable authentication, middleware, and Eunomia authorization.

#### Using Docker Run

```bash
docker pull knucklessg1/container-manager:latest

docker run -d \
  --name container-manager-mcp \
  -p 8004:8004 \
  -e HOST=0.0.0.0 \
  -e PORT=8004 \
  -e TRANSPORT=http \
  -e AUTH_TYPE=none \
  -e EUNOMIA_TYPE=none \
  knucklessg1/container-manager:latest
```

For advanced authentication (e.g., JWT, OAuth Proxy, OIDC Proxy, Remote OAuth) or Eunomia, add the relevant environment variables:

```bash
docker run -d \
  --name container-manager-mcp \
  -p 8004:8004 \
  -e HOST=0.0.0.0 \
  -e PORT=8004 \
  -e TRANSPORT=http \
  -e AUTH_TYPE=oidc-proxy \
  -e OIDC_CONFIG_URL=https://provider.com/.well-known/openid-configuration \
  -e OIDC_CLIENT_ID=your-client-id \
  -e OIDC_CLIENT_SECRET=your-client-secret \
  -e OIDC_BASE_URL=https://your-server.com \
  -e ALLOWED_CLIENT_REDIRECT_URIS=http://localhost:*,https://*.example.com/* \
  -e EUNOMIA_TYPE=embedded \
  -e EUNOMIA_POLICY_FILE=/app/mcp_policies.json \
  knucklessg1/container-manager:latest
```

#### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
services:
  container-manager-mcp:
    image: knucklessg1/container-manager:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8004
      - TRANSPORT=http
      - AUTH_TYPE=none
      - EUNOMIA_TYPE=none
    ports:
      - 8004:8004
```

For advanced setups with authentication and Eunomia:

```yaml
services:
  container-manager-mcp:
    image: knucklessg1/container-manager:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8004
      - TRANSPORT=http
      - AUTH_TYPE=oidc-proxy
      - OIDC_CONFIG_URL=https://provider.com/.well-known/openid-configuration
      - OIDC_CLIENT_ID=your-client-id
      - OIDC_CLIENT_SECRET=your-client-secret
      - OIDC_BASE_URL=https://your-server.com
      - ALLOWED_CLIENT_REDIRECT_URIS=http://localhost:*,https://*.example.com/*
      - EUNOMIA_TYPE=embedded
      - EUNOMIA_POLICY_FILE=/app/mcp_policies.json
    ports:
      - 8004:8004
    volumes:
      - ./mcp_policies.json:/app/mcp_policies.json
```

Run the service:

```bash
docker-compose up -d
```

#### Configure `mcp.json` for AI Integration

```json
{
  "mcpServers": {
    "container_manager": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "container-manager-mcp",
        "container-manager-mcp"
      ],
      "env": {
        "CONTAINER_MANAGER_SILENT": "False",                                  //Optional
        "CONTAINER_MANAGER_LOG_FILE": "~/Documents/container_manager_mcp.log" //Optional
        "CONTAINER_MANAGER_TYPE": "podman",                                   //Optional
        "CONTAINER_MANAGER_PODMAN_BASE_URL": "tcp://127.0.0.1:8080"           //Optional
      },
      "timeout": 200000
    }
  }
}
```
</details>

<details>
  <summary><b>Installation Instructions:</b></summary>

### Install Python Package

```bash
python -m pip install container-manager-mcp
```

or

```bash
uv pip install --upgrade container-manager-mcp
```

## Test Server

```bash
container-manager-mcp --transport http --host 127.0.0.1 --port 8080
```

This starts the MCP server using HTTP transport on localhost port 8080.

To interact with the MCP server programmatically, you can use a FastMCP client or make HTTP requests to the exposed endpoints. Example using curl to pull an image:

```bash
curl -X POST http://127.0.0.1:8080/pull_image \
  -H "Content-Type: application/json" \
  -d '{"image": "nginx", "tag": "latest", "manager_type": "docker"}'
```

Install the Python package:

```bash
python -m pip install container-manager-mcp
```

### Dependencies
- Python 3.7+
- `fastmcp` for MCP server functionality
- `docker` for Docker support
- `podman` for Podman support
- `pydantic` for data validation

Install dependencies:

```bash
python -m pip install fastmcp docker podman pydantic
```

Ensure Docker or Podman is installed and running on your system.

</details>


<details>
  <summary><b>Development and Contribution:</b></summary>

## Development and Contribution

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

Please ensure your code follows the project's coding standards and includes appropriate tests.

</details>

<details>
  <summary><b>License:</b></summary>

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Knuckles-Team/container-manager-mcp/blob/main/LICENSE) file for details.

</details>
<details>
  <summary><b>Repository Owners:</b></summary>

<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)

</details>
