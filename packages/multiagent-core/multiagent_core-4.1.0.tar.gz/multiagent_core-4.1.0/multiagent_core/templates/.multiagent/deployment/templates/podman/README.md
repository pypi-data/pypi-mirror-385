# Podman Container Templates

Alternative container templates for Podman instead of Docker.

## Key Differences

### Podman vs Docker

1. **No Daemon**: Podman doesn't require a daemon, containers run as child processes
2. **Rootless by Default**: Containers run without root privileges
3. **Containerfile**: Podman uses `Containerfile` by convention (though `Dockerfile` also works)
4. **Compatible**: Podman is OCI-compliant and works with Docker images/Dockerfiles
5. **Pod Support**: Native support for Kubernetes-like pods

## Usage

### Switch to Podman Templates

```bash
# Swap from docker to podman
multiagent templates swap deployment podman

# Verify
multiagent templates active deployment
```

### Building Containers

```bash
# Podman syntax is identical to Docker
podman build -t myapp:latest .

# Run container
podman run -p 8000:8000 myapp:latest

# Create systemd services (rootless)
podman generate systemd --new --name myapp > ~/.config/systemd/user/myapp.service
systemctl --user enable myapp
systemctl --user start myapp
```

### Docker Compose Alternative

Podman supports `podman-compose` or `docker-compose`:

```bash
# Install podman-compose
pip install podman-compose

# Use same docker-compose.yml
podman-compose up -d
```

Or use Podman's native pod functionality:

```bash
# Create a pod (similar to docker-compose)
podman pod create --name myapp-pod -p 8000:8000

# Run containers in the pod
podman run --pod myapp-pod --name web myapp:latest
podman run --pod myapp-pod --name db postgres:15
```

## Template Variables

Same variables as Docker templates:

- `{{PYTHON_VERSION}}` - Python version (e.g., 3.11)
- `{{NODE_VERSION}}` - Node.js version (e.g., 18)
- `{{PORT}}` - Application port
- `{{MAIN_MODULE}}` - Python module (e.g., main)
- `{{MAIN_FILE}}` - Node.js entry file (e.g., server.js)

## Advantages

- **Security**: Rootless by default, no daemon running as root
- **Resources**: Lower memory footprint (no daemon)
- **Integration**: Works with systemd for service management
- **Compatibility**: Drop-in replacement for most Docker workflows
- **Kubernetes**: Better pod support for local testing

## Migration from Docker

1. Swap templates: `multiagent templates swap deployment podman`
2. Alias podman to docker: `alias docker=podman` (optional)
3. Regenerate deployment configs in your project
4. Build and run with podman commands

No code changes needed - Podman is API-compatible with Docker!
