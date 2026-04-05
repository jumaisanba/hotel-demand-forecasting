from fastapi import APIRouter
from pydantic import BaseModel

from auth.api.dependencies import UoWDep
from auth.application.use_cases.manage_access import assign_owner

router = APIRouter(prefix="/internal/access", tags=["internal-access"])


class AssignOwnerIn(BaseModel):
    user_id: int
    hotel_id: int


@router.post("/assign-owner")
async def assign_owner_endpoint(data: AssignOwnerIn, uow: UoWDep):
    await assign_owner(uow=uow, user_id=data.user_id, hotel_id=data.hotel_id)
    return {"status": "ok"}
