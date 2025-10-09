# README

## 从头构建镜像

1. 更新provider中的api key

    ```python
    model_id_key = "xx-xxxxxxxxxxxxxxxx"
    dashscope_api_key = "xx-xxxxxxxxxxxxxxxx"
    ```

2. Dockerfile中添加自定义内容
3. 构建

    ```shell
    docker build -t xyz:v0.0.1 .
    ```

4. 使用，也参考test/run.sh和test/cmd.sh
    - 启动容器：`docker run --rm -ti -p 8888:8888 /bin/bash xyz:v0.0.1`
    - 容器内启动jupyter：`jupyter lab --ip 0.0.0.0 --port 8888 --AiExtension.allowed_providers=ali_embeddings_provider --AiExtension.allowed_providers=ali_tongyi --ServerApp.terminado_settings="shell_command=['/bin/bash']"
   `

## 基于已有镜像构建

1. 更改Dockerfile中的基础镜像

    ```Dockerfile
    FROM registry-vpc.cn-beijing.aliyuncs.com/seekgene/jupyter-float-base:v0.0.1
    ```

2. Dockerfile添加自定义内容

3. 构建

    ```shell
    docker build -t xyz:v0.0.1 .
    ```

4. 使用，也参考test/run.sh和test/cmd.sh

    - 启动容器：`docker run --rm -ti -p 8888:8888 /bin/bash xyz:v0.0.1`
    - 容器内启动jupyter：`jupyter lab --ip 0.0.0.0 --port 8888 --AiExtension.allowed_providers=ali_embeddings_provider --AiExtension.allowed_providers=ali_tongyi --ServerApp.terminado_settings="shell_command=['/bin/bash']"
   `

