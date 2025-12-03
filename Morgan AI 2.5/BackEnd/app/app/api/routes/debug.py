import os
import platform
import psutil
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, db_service

router = APIRouter()

@router.get("/status")
async def debug_status(request: Request, db: AsyncSession = Depends(get_db)):
    """Comprehensive system + service diagnostics for debugging without modifying UI."""
    # Basic platform info
    sys_info = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "process_id": os.getpid(),
        "cwd": os.getcwd(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Memory / CPU snapshot
    proc = psutil.Process(os.getpid())
    mem_info = proc.memory_info()
    resources = {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_rss_mb": round(mem_info.rss / (1024*1024), 2),
        "memory_vms_mb": round(mem_info.vms / (1024*1024), 2)
    }

    # Database health + counts
    db_health = {
        "initialized": hasattr(request.app.state, 'db')
    }
    try:
        db_health["healthy"] = await db_service.health_check()
        if db_health["healthy"]:
            db_health["table_counts"] = await db_service.get_table_counts()
    except Exception as e:
        db_health["healthy"] = False
        db_health["error"] = str(e)

    # OpenAI / Pinecone status
    services = {}
    services["openai_available"] = hasattr(request.app.state, 'openai')
    services["pinecone_available"] = hasattr(request.app.state, 'pinecone')

    # Active tasks (top level asyncio tasks)
    tasks = []
    try:
        for t in asyncio.all_tasks():
            if t is not asyncio.current_task():
                tasks.append({
                    "task": str(t),
                    "done": t.done()
                })
    except Exception:
        pass

    return {
        "system": sys_info,
        "resources": resources,
        "database": db_health,
        "services": services,
        "active_tasks": tasks[:25]  # cap length
    }
