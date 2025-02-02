from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
import uvicorn
from main import graph
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import logging
import traceback
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                logger.info(f"Processing request: {request.method} {request.url.path}")
                response = await original_route_handler(request)
                return response
            except Exception as ex:
                logger.error(f"Request failed: {request.method} {request.url.path}")
                logger.error(f"Error details: {str(ex)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

        return custom_route_handler

app = FastAPI()
app.router.route_class = ErrorLoggingRoute

# 添加可信主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=1800,
)

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Error handling request: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )

# LangSmith API 端点
@app.get("/tenants")
async def get_tenants():
    return {
        "data": [{
            "id": "default",
            "name": "Default Tenant",
            "created_at": datetime.utcnow().isoformat()
        }]
    }

@app.get("/tenants/current/usage_limits")
async def get_usage_limits():
    return {
        "has_exceeded_limit": False,
        "limits": {}
    }

@app.get("/workspaces/current/tags")
async def get_workspace_tags():
    return {
        "data": [],
        "has_more": False
    }

@app.get("/workspaces/current/stats")
async def get_workspace_stats():
    return {
        "total_runs": 0,
        "total_tokens": 0,
        "total_successful_runs": 0,
        "total_error_runs": 0
    }

@app.get("/workspaces")
async def get_workspaces():
    return {
        "data": [{
            "id": "default",
            "name": "Default Workspace",
            "created_at": datetime.utcnow().isoformat()
        }]
    }

@app.get("/orgs/current/info")
async def get_org_info():
    return {
        "id": "default",
        "name": "Default Organization",
        "created_at": datetime.utcnow().isoformat(),
        "settings": {
            "allow_token_sharing": True
        }
    }

# 模型定义
class Assistant(BaseModel):
    id: str = Field(default_factory=lambda: f"asst_{uuid.uuid4().hex}")
    name: str
    description: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Thread(BaseModel):
    id: str = Field(default_factory=lambda: f"thread_{uuid.uuid4().hex}")
    assistant_id: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    messages: List[Dict[str, Any]] = []

class Message(BaseModel):
    id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex}")
    thread_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Deployment(BaseModel):
    id: str = Field(default_factory=lambda: f"deployment_{uuid.uuid4().hex}")
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "active"

# 内存存储
assistants: Dict[str, Dict] = {}
threads: Dict[str, Dict] = {}
messages: Dict[str, Dict] = {}
deployments: Dict[str, Dict] = {}

# 创建默认助手
default_assistant = Assistant(
    id="asst_default",
    name="Simple Chat Assistant",
    description="A simple chat assistant using LangGraph",
    model="gpt-3.5-turbo",
    metadata={"temperature": 0}
).dict()
assistants[default_assistant["id"]] = default_assistant

@app.get("/")
async def root():
    return {"message": "LangGraph API Server"}

@app.get("/v1/assistants")
async def list_assistants():
    logger.info("Listing assistants")
    return {"data": list(assistants.values())}

@app.post("/v1/assistants")
async def create_assistant(assistant: Assistant):
    logger.info(f"Creating assistant: {assistant.id}")
    assistants[assistant.id] = assistant.dict()
    return assistant.dict()

@app.get("/v1/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    logger.info(f"Getting assistant: {assistant_id}")
    if assistant_id not in assistants:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return assistants[assistant_id]

@app.post("/v1/threads")
async def create_thread(thread: Thread):
    logger.info(f"Creating thread: {thread.id}")
    threads[thread.id] = thread.dict()
    return thread.dict()

@app.get("/v1/threads/{thread_id}")
async def get_thread(thread_id: str):
    logger.info(f"Getting thread: {thread_id}")
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    return threads[thread_id]

@app.post("/v1/threads/{thread_id}/messages")
async def create_message(thread_id: str, message: Message):
    logger.info(f"Creating message in thread: {thread_id}")
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    message.thread_id = thread_id
    messages[message.id] = message.dict()
    threads[thread_id]["messages"].append(message.dict())
    return message.dict()

@app.get("/v1/threads/{thread_id}/messages")
async def list_messages(thread_id: str):
    logger.info(f"Listing messages for thread: {thread_id}")
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"data": threads[thread_id]["messages"]}

@app.post("/v1/threads/{thread_id}/runs")
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

@app.get("/v1/threads/{thread_id}/runs/{run_id}")
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

@app.post("/v1/invoke")
async def invoke(data: dict):
    logger.info("Invoking graph")
    try:
        result = graph.invoke(data)
        return result
    except Exception as e:
        logger.error(f"Error in invoke: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/deployments")
async def list_deployments():
    logger.info("Listing deployments")
    return {"data": list(deployments.values())}

@app.post("/deployments")
async def create_deployment(deployment: Deployment):
    logger.info(f"Creating deployment: {deployment.id}")
    deployments[deployment.id] = deployment.dict()
    return deployment.dict()

@app.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    logger.info(f"Getting deployment: {deployment_id}")
    if deployment_id not in deployments:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployments[deployment_id]

@app.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str):
    logger.info(f"Deleting deployment: {deployment_id}")
    if deployment_id not in deployments:
        raise HTTPException(status_code=404, detail="Deployment not found")
    del deployments[deployment_id]
    return {"status": "success"}

@app.post("/deployments/{deployment_id}/invoke")
async def invoke_deployment(deployment_id: str, request: Dict[str, Any]):
    logger.info(f"Invoking deployment: {deployment_id}")
    if deployment_id not in deployments:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # 这里我们使用之前定义的 graph 来处理请求
    try:
        result = graph(request)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error invoking deployment: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run(
        app,
        host="139.59.244.95",
        port=8123,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
