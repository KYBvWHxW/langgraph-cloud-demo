from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/tenants")
async def get_tenants():
    return {
        "data": [{
            "id": "default",
            "name": "Default Tenant",
            "created_at": datetime.utcnow().isoformat()
        }]
    }

@router.get("/tenants/current/usage_limits")
async def get_usage_limits():
    return {
        "has_exceeded_limit": False,
        "limits": {}
    }

@router.get("/workspaces/current/tags")
async def get_workspace_tags():
    return {
        "data": [],
        "has_more": False
    }

@router.get("/workspaces/current/stats")
async def get_workspace_stats():
    return {
        "total_runs": 0,
        "total_tokens": 0,
        "total_successful_runs": 0,
        "total_error_runs": 0
    }

@router.get("/workspaces")
async def get_workspaces():
    return {
        "data": [{
            "id": "default",
            "name": "Default Workspace",
            "created_at": datetime.utcnow().isoformat()
        }]
    }

@router.get("/orgs/current/info")
async def get_org_info():
    return {
        "id": "default",
        "name": "Default Organization",
        "created_at": datetime.utcnow().isoformat(),
        "settings": {
            "allow_token_sharing": True
        }
    }
