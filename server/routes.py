from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import uuid
import logging
import traceback
from .models import Assistant, Thread, Message, Deployment

logger = logging.getLogger(__name__)

router = APIRouter()

# Storage (to be replaced with database)
assistants: Dict[str, Dict] = {}
threads: Dict[str, Dict] = {}
messages: Dict[str, Dict] = {}
deployments: Dict[str, Dict] = {}

# Create default assistant
default_assistant = Assistant(
    id="asst_default",
    name="Simple Chat Assistant",
    description="A simple chat assistant using LangGraph",
    model="gpt-3.5-turbo",
    metadata={"temperature": 0}
).dict()
assistants[default_assistant["id"]] = default_assistant

@router.get("/v1/assistants")
async def list_assistants():
    logger.info("Listing assistants")
    return {"data": list(assistants.values())}

@router.post("/v1/assistants")
async def create_assistant(assistant: Assistant):
    logger.info(f"Creating assistant: {assistant.id}")
    assistants[assistant.id] = assistant.dict()
    return assistant.dict()

@router.get("/v1/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    logger.info(f"Getting assistant: {assistant_id}")
    if assistant_id not in assistants:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return assistants[assistant_id]

@router.post("/v1/threads")
async def create_thread(thread: Thread):
    logger.info(f"Creating thread: {thread.id}")
    threads[thread.id] = thread.dict()
    return thread.dict()

@router.get("/v1/threads/{thread_id}")
async def get_thread(thread_id: str):
    logger.info(f"Getting thread: {thread_id}")
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    return threads[thread_id]

@router.post("/v1/threads/{thread_id}/messages")
async def create_message(thread_id: str, message: Message):
    logger.info(f"Creating message in thread: {thread_id}")
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    message.thread_id = thread_id
    messages[message.id] = message.dict()
    threads[thread_id]["messages"].append(message.dict())
    return message.dict()

@router.get("/v1/threads/{thread_id}/messages")
async def list_messages(thread_id: str):
    logger.info(f"Listing messages for thread: {thread_id}")
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"data": threads[thread_id]["messages"]}

@router.post("/v1/threads/{thread_id}/runs")
async def create_run(thread_id: str):
    logger.info(f"Creating run for thread: {thread_id}")
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    run_id = f"run_{uuid.uuid4().hex}"
    return {
        "id": run_id,
        "thread_id": thread_id,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }

@router.get("/v1/threads/{thread_id}/runs/{run_id}")
async def get_run(thread_id: str, run_id: str):
    logger.info(f"Getting run {run_id} for thread: {thread_id}")
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {
        "id": run_id,
        "thread_id": thread_id,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }

@router.get("/deployments")
async def list_deployments():
    logger.info("Listing deployments")
    return {"data": list(deployments.values())}

@router.post("/deployments")
async def create_deployment(deployment: Deployment):
    logger.info(f"Creating deployment: {deployment.id}")
    deployments[deployment.id] = deployment.dict()
    return deployment.dict()

@router.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    logger.info(f"Getting deployment: {deployment_id}")
    if deployment_id not in deployments:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployments[deployment_id]

@router.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str):
    logger.info(f"Deleting deployment: {deployment_id}")
    if deployment_id not in deployments:
        raise HTTPException(status_code=404, detail="Deployment not found")
    del deployments[deployment_id]
    return {"status": "success"}
