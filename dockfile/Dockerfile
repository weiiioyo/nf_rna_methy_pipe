FROM registry-vpc.cn-beijing.aliyuncs.com/seekgene/jupyter-float-base:v0.0.1

# Install essential Linux utilities
RUN apt-get update && apt-get install -y \
    gawk \
    coreutils \
    grep \
    procps \
    sed \
    util-linux \
    && rm -rf /var/lib/apt/lists/*

# Note: Most of these tools are typically pre-installed in base images:
# - awk (provided by gawk package)
# - date (provided by coreutils package)
# - grep (standalone package)
# - ps (provided by procps package)
# - sed (standalone package)
# - tail (provided by coreutils package)
# - tee (provided by coreutils package)