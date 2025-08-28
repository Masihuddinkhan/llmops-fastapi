# AI-Powered Dataset Management & Search System

##  Overview
An intelligent FastAPI-based platform that enables seamless dataset upload, extraction, and LLM-powered search capabilities. Built for scalable deployment with Kubernetes orchestration.

##  Key Features
- **Dataset Upload & Management**: Automated zip file processing and server-side extraction
- **Dynamic File Structure Visualization**: Interactive web UI displaying organized folder hierarchy  
- **LLM-Powered Search**: Natural language queries for dataset exploration and analysis
- **Smart Analytics**: Class-based filtering, statistical counts, and intelligent data insights
- **Scalable Architecture**: Kubernetes-ready deployment for high-performance operations

##  Tech Stack
- **Backend**: Python, FastAPI, Uvicorn
- **AI/ML**: LLM Integration (OpenAI/Hugging Face), NLP
- **Frontend**: HTML, CSS, JavaScript
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **File Processing**: Python File System Libraries

##  Architecture

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
