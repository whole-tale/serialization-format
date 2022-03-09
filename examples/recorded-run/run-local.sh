#!/bin/sh

# Use repo2docker to build the image from the workspace
docker run  \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "`pwd`/data/workspace:/WholeTale/workspace" \
  -v "`pwd`/metadata/environment.json:/WholeTale/workspace/.wholetale/environment.json" \
  --privileged=true \
  -e DOCKER_HOST=unix:///var/run/docker.sock \
  wholetale/repo2docker_wholetale:latest \
  jupyter-repo2docker \
    --config=/wholetale/repo2docker_config.py \
    --target-repo-dir=/WholeTale/workspace \
    --user-id=1000 --user-name=jovyan \
    --no-clean --no-run --debug \
    --image-name wholetale/tale_602d7a21b80f3feb48a9e6b6 \
    /WholeTale/workspace

docker run --rm \
    -v "`pwd`:/bag" \
    -ti wholetale/repo2docker_wholetale:latest bdbag --resolve-fetch all /bag

echo "========================================================================"
echo " Open your browser and go to: http://localhost:8888/?token=wholetale "
echo "========================================================================"

# Run the built image
docker run -p 8888:8888 \
  -v "`pwd`/data/data:/WholeTale/data" \
  -v "`pwd`/data/workspace:/WholeTale/workspace" \
  wholetale/tale_602d7a21b80f3feb48a9e6b6 jupyter notebook --no-browser --port 8888 --ip=0.0.0.0 --NotebookApp.token=wholetale --NotebookApp.base_url=/ --NotebookApp.port_retries=0

