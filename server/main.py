from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.routing import APIRoute
import logging
import traceback
from .routes import router as main_router
from .langsmith import router as langsmith_router
from main import graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorLoggingRoute(APIRoute):
    def get_route_handler(self):
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

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=1800,
)

from .middleware import add_cors_headers, catch_exceptions_middleware

app.middleware("http")(add_cors_headers)
app.middleware("http")(catch_exceptions_middleware)

app.include_router(main_router)
app.include_router(langsmith_router)

@app.get("/")
async def root():
    return {"message": "LangGraph API Server"}

@app.get("/v1/health")
async def health_check():
    return {"status": "healthy"}

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
