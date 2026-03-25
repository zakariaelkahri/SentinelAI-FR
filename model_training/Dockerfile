# ── Base: PyTorch 2.2 + CUDA 12.1 + cuDNN 8 ────────────────────────────────
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

LABEL maintainer="SentinelAI-FR"
LABEL description="YOLOv8l training environment with Jupyter Lab"

# ── System dependencies ──────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ────────────────────────────────────────────────────────
WORKDIR /workspace

# ── Python dependencies ──────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Copy project files (datasets are mounted as volumes, see below) ──────────
COPY notebooks/ ./notebooks/
COPY scripts/ ./scripts/
# COPY load_datasets.py .

# ── Jupyter configuration ────────────────────────────────────────────────────
RUN jupyter lab --generate-config && \
    echo "c.ServerApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.port = 8888" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.open_browser = False" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.allow_root = True" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.token = ''" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.password = ''" >> /root/.jupyter/jupyter_lab_config.py

# ── Expose Jupyter port ───────────────────────────────────────────────────────
EXPOSE 8888

# ── Mount points for datasets and model outputs ───────────────────────────────
# docker run -v /host/images:/workspace/images -v /host/runs:/workspace/runs ...
VOLUME ["/workspace/images", "/workspace/runs"]

# ── Entrypoint ────────────────────────────────────────────────────────────────
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
