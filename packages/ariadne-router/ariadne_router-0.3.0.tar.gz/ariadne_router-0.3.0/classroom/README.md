# Ariadne Quantum Classroom Docker Image

A ready-to-use Docker container for quantum computing education with Ariadne.

## Quick Start

```bash
# Build the image
docker build -t ariadne-classroom .

# Run the classroom
docker run -p 8888:8888 ariadne-classroom
```

Then open http://localhost:8888 in your browser.

## Multi-Architecture Build

For M1/M2 Mac and x86_64 support:

```bash
# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t your-username/ariadne-classroom:latest --push .

# Or build locally for current platform
docker buildx build --platform linux/$(uname -m) -t ariadne-classroom .
```

## Features

- Pre-installed Ariadne with all backends (Stim, Qiskit, MPS, Metal, CUDA)
- Jupyter Lab environment
- Education notebooks included:
  - Bell State classroom demonstration
  - QAOA algorithm exploration
  - Variational circuits tutorial
- No configuration required - works out of the box

## Usage Examples

### Running a Notebook

Once Jupyter Lab is running, you can:

1. Open any of the pre-loaded notebooks in the `/notebooks` directory
2. Create new notebooks to test quantum circuits
3. Use the Ariadne CLI from the terminal

### CLI Usage

```bash
# Start a shell in the container
docker exec -it <container-id> bash

# Run benchmarks
ariadne benchmark-suite --algorithms bell,ghz --backends auto --output results.json

# Test individual circuits
ariadne simulate /workspace/notebooks/bell.qasm --shots 1000
```

## Customization

### Adding Custom Notebooks

1. Mount your notebooks directory:
```bash
docker run -p 8888:8888 -v /path/to/your/notebooks:/workspace/custom-notebooks ariadne-classroom
```

2. Or build a custom image:
```dockerfile
FROM ariadne-classroom
COPY your-notebooks/ /workspace/notebooks/
```

### Installing Additional Packages

```dockerfile
FROM ariadne-classroom
RUN pip install matplotlib seaborn plotly
```

## Production Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  ariadne-classroom:
    image: ariadne-classroom:latest
    ports:
      - "8888:8888"
    environment:
      - JUPYTER_TOKEN=your-secret-token
    volumes:
      - ./notebooks:/workspace/notebooks
      - ./data:/workspace/data
    restart: unless-stopped
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ariadne-classroom
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ariadne-classroom
  template:
    metadata:
      labels:
        app: ariadne-classroom
    spec:
      containers:
      - name: ariadne-classroom
        image: ariadne-classroom:latest
        ports:
        - containerPort: 8888
---
apiVersion: v1
kind: Service
metadata:
  name: ariadne-classroom-service
spec:
  selector:
    app: ariadne-classroom
  ports:
  - port: 80
    targetPort: 8888
  type: LoadBalancer
```

## Security Notes

- The default configuration runs Jupyter Lab without authentication for convenience
- For production use, enable authentication:
  ```bash
  docker run -p 8888:8888 -e JUPYTER_TOKEN=your-secure-token ariadne-classroom
  ```
- Consider using HTTPS in production environments

## Troubleshooting

### Port Already in Use

```bash
# Use a different port
docker run -p 8889:8888 ariadne-classroom
```

### Permission Issues

```bash
# Ensure proper permissions for mounted volumes
docker run -p 8888:8888 -v $(pwd)/notebooks:/workspace/notebooks:Z ariadne-classroom
```

### Memory Limitations

For large quantum circuits, increase available memory:

```bash
docker run -p 8888:8888 --memory=4g ariadne-classroom
```

## Support

- Documentation: https://github.com/Hmbown/ariadne
- Issues: https://github.com/Hmbown/ariadne/issues
- Discussions: https://github.com/Hmbown/ariadne/discussions
