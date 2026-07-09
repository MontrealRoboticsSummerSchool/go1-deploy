ARG BASE_TAG=r32.5.0

FROM nvcr.io/nvidia/l4t-base:${BASE_TAG}

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    curl \
    ca-certificates \
    libgomp1 \
    pkg-config \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/sdk
COPY ./unitree_legged_sdk .
RUN mkdir build && cd build && cmake ../ && make

WORKDIR /root
RUN curl -L -o miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh \
    && bash miniforge.sh -b -p /root/miniforge3 \
    && rm miniforge.sh

RUN /root/miniforge3/bin/conda init
ENV PATH="/root/miniforge3/bin:${PATH}"

WORKDIR /app
COPY environment.yml /app/

RUN conda env create -f environment.yml

ENV PATH="/root/miniforge3/envs/depl/bin:${PATH}"
ENV CONDA_DEFAULT_ENV="depl"
ENV PYTHONPATH="/app/sdk/lib/python/arm64/:${PYTHONPATH}"

CMD ["/bin/bash"]
