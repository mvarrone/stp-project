import time
from fastapi import APIRouter, HTTPException, status

from graph import code

router = APIRouter(tags=["Graph"])


@router.get("/stp-graph")
async def graph_endpoint():
    start_total: float = time.time()
    data = code.main()
    end_total: float = time.time() - start_total
    end_total, unit = code.print_execution_time(end_total)
    elapsed_time = {"value": end_total, "unit": unit}

    if data.get("error"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=data.get("error_description"),
        )

    return {
        "nodes": data.get("nodes"),
        "edges": data.get("edges"),
        "edges_with_blocked_links": data.get("edges_with_blocked_links"),
        "blocked_interfaces": data.get("blocked_interfaces"),
        "results": data.get("results"),
        "elapsed_time": elapsed_time,
    }
