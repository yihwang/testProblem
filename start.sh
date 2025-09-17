#!/bin/bash
docker stop pos && docker rm pos
docker run -d --restart=always --name pos --network=host -it \
-p 11500:11500 \
-v $(pwd)/testmain.py:/app/testmain.py \
public-opinion-service:v1
