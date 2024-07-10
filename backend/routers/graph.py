import time
from fastapi import APIRouter, Request

from graph import code

router = APIRouter(tags=["Graph"])


@router.get("/stp-graph")
async def graph_endpoint(request: Request):
    start_total: float = time.time()
    data = code.main()
    end_total: float = time.time() - start_total
    end_total, unit = code.print_execution_time(end_total)

    return {
        "nodes": data.get("nodes"),
        "edges": data.get("edges"),
        "edges_blocked_links": data.get("edges_blocked_links"),
        "elapsed_time": {
            "value": end_total,
            "unit": unit,
        },
    }
