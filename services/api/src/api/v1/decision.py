"""Decision session endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import AppException, ContentSafetyException, NotFoundException
from src.core.logging import get_logger
from src.db.base import get_db
from src.schemas.decision import (
    CreateDecisionSessionRequest,
    DecisionSessionResponse,
    ListDecisionSessionsResponse,
)
from src.services.decision_service import DecisionService
from src.services.openai_client import openai_client

logger = get_logger(__name__)

router = APIRouter()


def get_decision_service(db: AsyncSession = Depends(get_db)) -> DecisionService:
    """Dependency to get decision service instance.

    Args:
        db: Database session

    Returns:
        Decision service instance
    """
    return DecisionService(db_session=db, openai_client=openai_client)


@router.post(
    "/sessions",
    response_model=DecisionSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_decision_session(
    request: CreateDecisionSessionRequest,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionSessionResponse:
    """Create a new decision session.

    Process user's decision through multi-agent system and return Decision Brief.

    Args:
        request: Decision context, options, and stress level
        service: Decision service instance

    Returns:
        Complete decision session with AI-generated brief

    Raises:
        HTTPException: If content fails safety check or processing fails
    """
    try:
        logger.info(
            "api_create_session_request",
            stress_level=request.stress_level,
            context_length=len(request.context),
        )

        session = await service.create_decision_session(request)

        logger.info("api_create_session_success", session_id=session.id)

        return session

    except ContentSafetyException as e:
        logger.warning("api_content_safety_blocked", reason=e.detail)
        raise HTTPException(
            status_code=e.status,
            detail=e.to_dict(),
        )
    except AppException as e:
        logger.error("api_create_session_error", error=e.detail)
        raise HTTPException(
            status_code=e.status,
            detail=e.to_dict(),
        )
    except Exception as e:
        logger.error("api_create_session_unexpected", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "type": "about:blank",
                "title": "Błąd wewnętrzny serwera",
                "status": 500,
                "detail": "Wystąpił nieoczekiwany błąd",
            },
        )


@router.get("/sessions/{session_id}", response_model=DecisionSessionResponse)
async def get_decision_session(
    session_id: UUID,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionSessionResponse:
    """Get a decision session by ID.

    Args:
        session_id: Session UUID
        service: Decision service instance

    Returns:
        Decision session

    Raises:
        HTTPException: If session not found
    """
    try:
        logger.info("api_get_session_request", session_id=session_id)
        session = await service.get_decision_session(session_id)
        return session

    except NotFoundException as e:
        logger.warning("api_session_not_found", session_id=session_id)
        raise HTTPException(
            status_code=e.status,
            detail=e.to_dict(),
        )
    except Exception as e:
        logger.error("api_get_session_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nie udało się pobrać sesji",
        )


@router.get("/sessions", response_model=ListDecisionSessionsResponse)
async def list_decision_sessions(
    user_id: str | None = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    service: DecisionService = Depends(get_decision_service),
) -> ListDecisionSessionsResponse:
    """List decision sessions with pagination.

    Args:
        user_id: Optional user ID filter
        page: Page number (1-indexed)
        page_size: Results per page
        service: Decision service instance

    Returns:
        Paginated list of sessions
    """
    try:
        logger.info(
            "api_list_sessions_request",
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

        sessions = await service.list_decision_sessions(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

        return sessions

    except Exception as e:
        logger.error("api_list_sessions_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nie udało się pobrać listy sesji",
        )
