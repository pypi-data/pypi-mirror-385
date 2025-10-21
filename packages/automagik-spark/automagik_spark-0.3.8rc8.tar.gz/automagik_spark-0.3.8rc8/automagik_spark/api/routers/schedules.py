"""Schedules router for the AutoMagik API."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from ..models import ScheduleCreate, ScheduleResponse, ErrorResponse
from ..dependencies import verify_api_key
from ..dependencies import get_session
from ...core.workflows.manager import WorkflowManager
from ...core.scheduler.manager import SchedulerManager
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/schedules", tags=["schedules"], responses={401: {"model": ErrorResponse}}
)


async def get_workflow_manager(
    session: AsyncSession = Depends(get_session),
) -> WorkflowManager:
    """Get workflow manager instance."""
    return WorkflowManager(session)


async def get_scheduler_manager(
    session: AsyncSession = Depends(get_session),
    workflow_manager: WorkflowManager = Depends(get_workflow_manager),
) -> SchedulerManager:
    """Get scheduler manager instance."""
    return SchedulerManager(session, workflow_manager)


@router.post(
    "", response_model=ScheduleResponse, dependencies=[Depends(verify_api_key)]
)
async def create_schedule(
    schedule: ScheduleCreate,
    scheduler_manager: SchedulerManager = Depends(get_scheduler_manager),
):
    """Create a new schedule."""
    try:
        # Convert flow_id to UUID
        workflow_id = UUID(schedule.workflow_id)
        created_schedule = await scheduler_manager.create_schedule(
            workflow_id=workflow_id,
            schedule_type=schedule.schedule_type,
            schedule_expr=schedule.schedule_expr,
            params=(
                {"value": schedule.input_value}
                if schedule.input_value is not None
                else None
            ),
        )
        if not created_schedule:
            raise HTTPException(status_code=400, detail="Failed to create schedule")
        return ScheduleResponse.model_validate(created_schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "", response_model=List[ScheduleResponse], dependencies=[Depends(verify_api_key)]
)
async def list_schedules(
    scheduler_manager: SchedulerManager = Depends(get_scheduler_manager),
):
    """List all schedules."""
    try:
        schedules = await scheduler_manager.list_schedules()
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    dependencies=[Depends(verify_api_key)],
)
async def get_schedule(
    schedule_id: str,
    scheduler_manager: SchedulerManager = Depends(get_scheduler_manager),
):
    """Get a specific schedule by ID."""
    try:
        schedule_uuid = UUID(schedule_id)
        schedule = await scheduler_manager.get_schedule(schedule_uuid)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return ScheduleResponse.model_validate(schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    dependencies=[Depends(verify_api_key)],
)
async def update_schedule(
    schedule_id: str,
    schedule: ScheduleCreate,
    scheduler_manager: SchedulerManager = Depends(get_scheduler_manager),
):
    """Update a schedule by ID."""
    try:
        schedule_uuid = UUID(schedule_id)
        UUID(schedule.workflow_id)

        # First check if schedule exists
        existing_schedule = await scheduler_manager.get_schedule(schedule_uuid)
        if not existing_schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        # Update schedule expression if changed
        if existing_schedule.schedule_expr != schedule.schedule_expr:
            success = await scheduler_manager.update_schedule_expression(
                schedule_uuid, schedule.schedule_expr
            )
            if not success:
                raise HTTPException(
                    status_code=400, detail="Failed to update schedule expression"
                )

        # Update schedule status if changed
        # Type ignore: ScheduleCreate doesn't have status attribute in schema
        # but it's accessed here for update operations - this is a design choice
        if existing_schedule.status != schedule.status:  # type: ignore[attr-defined]
            action = "resume" if schedule.status == "active" else "pause"  # type: ignore[attr-defined]
            success = await scheduler_manager.update_schedule_status(
                str(schedule_uuid), action
            )
            if not success:
                raise HTTPException(
                    status_code=400, detail="Failed to update schedule status"
                )

        # Get updated schedule
        updated_schedule = await scheduler_manager.get_schedule(schedule_uuid)
        if not updated_schedule:
            raise HTTPException(
                status_code=404, detail="Schedule not found after update"
            )

        return ScheduleResponse.model_validate(updated_schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    dependencies=[Depends(verify_api_key)],
)
async def delete_schedule(
    schedule_id: str,
    scheduler_manager: SchedulerManager = Depends(get_scheduler_manager),
):
    """Delete a schedule by ID."""
    try:
        schedule_uuid = UUID(schedule_id)

        # First get the schedule
        schedule = await scheduler_manager.get_schedule(schedule_uuid)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        # Delete the schedule
        success = await scheduler_manager.delete_schedule(schedule_uuid)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete schedule")

        return ScheduleResponse.model_validate(schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{schedule_id}/enable",
    response_model=ScheduleResponse,
    dependencies=[Depends(verify_api_key)],
)
async def enable_schedule(
    schedule_id: str,
    scheduler_manager: SchedulerManager = Depends(get_scheduler_manager),
):
    """Enable a schedule."""
    try:
        schedule_uuid = UUID(schedule_id)

        # First check if schedule exists
        schedule = await scheduler_manager.get_schedule(schedule_uuid)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        # Enable the schedule
        success = await scheduler_manager.update_schedule_status(
            str(schedule_uuid), "resume"
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to enable schedule")

        # Get updated schedule
        updated_schedule = await scheduler_manager.get_schedule(schedule_uuid)
        if not updated_schedule:
            raise HTTPException(
                status_code=404, detail="Schedule not found after update"
            )

        return ScheduleResponse.model_validate(updated_schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{schedule_id}/disable",
    response_model=ScheduleResponse,
    dependencies=[Depends(verify_api_key)],
)
async def disable_schedule(
    schedule_id: str,
    scheduler_manager: SchedulerManager = Depends(get_scheduler_manager),
):
    """Disable a schedule."""
    try:
        schedule_uuid = UUID(schedule_id)

        # First check if schedule exists
        schedule = await scheduler_manager.get_schedule(schedule_uuid)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        # Disable the schedule
        success = await scheduler_manager.update_schedule_status(
            str(schedule_uuid), "pause"
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to disable schedule")

        # Get updated schedule
        updated_schedule = await scheduler_manager.get_schedule(schedule_uuid)
        if not updated_schedule:
            raise HTTPException(
                status_code=404, detail="Schedule not found after update"
            )

        return ScheduleResponse.model_validate(updated_schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
