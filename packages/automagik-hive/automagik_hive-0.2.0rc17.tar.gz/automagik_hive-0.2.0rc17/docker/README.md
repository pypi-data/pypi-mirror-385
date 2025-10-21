# Docker Architecture Overview

This directory contains all Docker-related files for the Automagik Hive multi-agent system.

## Directory Structure

```
docker/
├── main/                       # Main workspace environment
│   ├── Dockerfile             # Main application container
│   ├── docker-compose.yml     # Main services orchestration
│   ├── .dockerignore          # Main-specific ignore patterns
│   └── README.md              # Main environment documentation
├── templates/                  # Reusable Docker templates
│   └── workspace.yml          # Generic workspace template
├── scripts/                    # Docker-related scripts
│   └── validate.sh            # Validation script
├── lib/                        # Docker service libraries
│   ├── compose_manager.py     # Compose management utilities
│   ├── compose_service.py     # Service orchestration
│   └── postgres_manager.py    # PostgreSQL management
└── README.md                   # This file
```

## Environment

### Main Environment (docker/main/)
- **Ports**: API 8886, PostgreSQL 5532
- **Usage**: Primary development and production workloads
- **Integration**: Used by `make prod`, `make dev`

## Quick Commands

```bash
# Main environment
docker compose -f docker/main/docker-compose.yml up -d

# Validate environment
bash docker/scripts/validate.sh
```

## Runtime Surfaces

- **Agno Playground**: Enabled by default inside the Hive API when `HIVE_EMBED_PLAYGROUND=true` (default). Access it at `http://<HIVE_API_HOST>:<HIVE_API_PORT>/playground` (defaults to `http://localhost:8886/playground`).
- **AgentOS Control Pane**: Point control pane tooling at the Hive server base URL (`HIVE_CONTROL_PANE_BASE_URL`, default is the API base). The AgentOS config endpoint lives at `/api/v1/agentos/config`.
- **Authentication**: Playground honours the API key guard; disable authentication only for local development.

Set `HIVE_EMBED_PLAYGROUND=false` to run the API without mounting the Playground. Override the mount path with `HIVE_PLAYGROUND_MOUNT_PATH` when reverse proxies require a different location.

> Compose deployments should now proxy the Hive API directly instead of exposing a separate `localhost:8000` Playground stack. The optional compose services remain available for local infrastructure, but the authoritative routes live inside the Hive server.

## Migration Notes

This structure was created by consolidating Docker files from the root directory:
- All Dockerfile.* files moved to environment-specific directories
- All docker-compose*.yml files organized by environment
- Templates consolidated from /templates/ directory
- Docker libraries moved from /lib/docker/ to /docker/lib/
- All references updated throughout the codebase
