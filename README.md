# llmops-fastapi

# LLM-FastPI

# uvicorn app.main:app --reload

## Test the app locla mcahine 

- run =  uvicorn app.main:app --reload

## Docker Image Build & Run

# Image build 
- docker build -t llmops-fastapi .

# Run 
- docker run -p 8000:8000 llmops-fastapi

## Kubernetes  deploy

- minikube start
- kubectl apply -f deployment.yaml

Deployment status check:

- kubectl get pods
- kubectl get svc

## Browser oen and run
- minikube service llmops-fastapi-service
