#!/bin/bash
docker stop pos && docker rm pos
docker run -d --restart=always --name pos --network=host -it \
-p 11500:11500 \
-v $(pwd):/app/testProblem/ \
public-opinion-service:v1 \
sh -c "cd /app/testProblem/ && uvicorn testmain:app --host 0.0.0.0 --port 11500"
