FROM fedora:33
MAINTAINER Chris Larson

# Conda
RUN dnf install -y \
    wget \
    bzip2 \
    libXcomposite \
    libXcursor \
    libXi \
    libXtst \
    libXrandr \
    alsa-lib \
    mesa-libEGL \
    libXdamage \
    mesa-libGL \
    libXScrnSaver
RUN wget https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh -O ~/anaconda.sh && \
    chmod +x ~/anaconda.sh && \
    bash ~/anaconda.sh -b -p $HOME/anaconda && \
    rm -f ~/anaconda.sh
RUN source $HOME/anaconda/bin/activate base && \
    $HOME/anaconda/bin/conda create -n 'virtex' python=3.8.5 && \
    source $HOME/anaconda/bin/activate virtex && \
    $HOME/anaconda/bin/conda install -c anaconda cudatoolkit==11.0.221 && \
    echo 'export PATH="$HOME/anaconda/bin${PATH:+:${PATH}}"' >> ~/.bashrc && \
    echo 'export PATH=$HOME/anaconda/pkgs/cudatoolkit-11.0.221-h6bb024c_0/bin${PATH:+:${PATH}}' >> ~/.bashrc && \
    echo 'export LD_LIBRARY_PATH=$HOME/anaconda/pkgs/cudatoolkit-11.0.221-h6bb024c_0/lib:$HOME/anaconda/pkgs/cudatoolkit-11.0.221-h6bb024c_0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' >> ~/.bashrc && \
    echo 'source activate virtex' >> ~/.bashrc && \
    $HOME/anaconda/bin/conda clean --all

# CUDA
RUN mkdir -p $HOME/anaconda/pkgs/cudatoolkit-11.0.221-h6bb024c_0/lib64 && \
    mkdir -p $HOME/anaconda/pkgs/cudatoolkit-11.0.221-h6bb024c_0/include
COPY docker/cuda/lib/* /root/anaconda/pkgs/cudatoolkit-11.0.221-h6bb024c_0/lib64/
# COPY docker/cuda/include/* /root/anaconda/pkgs/cudatoolkit-11.0.221-h6bb024c_0/include/

# Virtex
COPY virtex /root/virtex/virtex
COPY setup.py /root/virtex/
COPY req* /root/virtex/
COPY docker/whl /root/virtex/docker/whl
COPY README.md /root/virtex/
RUN cd $HOME/virtex && \
    source ~/.bashrc && \
    python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt && \
    python -m pip install -r requirements_serial.txt && \
    python -m pip install -r requirements_gpu.txt && \
    python setup.py install && \
    cd .. && rm -rf virtex && \
    conda clean --all
