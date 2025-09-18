!/bin/bash
docker stop pos && docker rm pos
docker run -d --restart=always --name pos --network=host -it \
-p 11500:11500 \
-v $(pwd):/app/testProblem/ \
public-opinion-service:v1 \
sh -c "cd /app/testProblem/ && uvicorn testmain:app --host 0.0.0.0 --port 11500"

docker stop pos-ui && docker rm pos-ui
docker run -d --restart=always --name pos-ui --network=host -it \
-p 7866:7866 \
-v $(pwd):/app/testProblem/ \
public-opinion-service:v1 \
sh -c "cd /app/testProblem/web && python app.py"