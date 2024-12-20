from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.routers.v1.endpoints import (
    get_patients,
    get_observations,
    get_calculations
)


router_v1 = APIRouter() 


## [GET]: Test
@router_v1.get("", tags=["Test"])
async def test():
    return JSONResponse(status_code=200, content="Here goes the apis")

router_v1.include_router(get_patients.router, prefix="/get-patients", tags=["Get Patients"])
router_v1.include_router(get_observations.router, prefix="/get-observations", tags=["Get Observations"])
router_v1.include_router(get_calculations.router, prefix="/get-calculations", tags=["Get Calculations"])