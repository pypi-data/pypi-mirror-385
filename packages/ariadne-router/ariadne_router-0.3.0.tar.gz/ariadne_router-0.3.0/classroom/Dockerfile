FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    JUPYTER_ENABLE_LAB=yes

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Ariadne with all optional dependencies
RUN pip install --no-cache-dir ariadne-router[all] jupyterlab

# Copy education notebooks
COPY examples/education/*.ipynb /workspace/notebooks/

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "========================================="\n\
echo "Ariadne Quantum Classroom Environment"\n\
echo "========================================="\n\
echo "Available notebooks:"\n\
ls -la /workspace/notebooks/\n\
echo ""\n\
echo "Starting Jupyter Lab..."\n\
echo "Access at: http://localhost:8888"\n\
echo "========================================="\n\
exec jupyter lab --ip=0.0.0.0 --no-browser --port=8888 --NotebookApp.token="" --NotebookApp.password=""\n\
' > /workspace/start.sh && chmod +x /workspace/start.sh

# Expose Jupyter port
EXPOSE 8888

# Set the default command
CMD ["/workspace/start.sh"]
