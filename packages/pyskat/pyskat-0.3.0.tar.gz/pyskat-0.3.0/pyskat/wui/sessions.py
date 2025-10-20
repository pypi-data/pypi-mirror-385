from datetime import datetime
from typing import Annotated
from fastapi import Request, Depends
from fastapi.routing import APIRouter
from sqlmodel import select

from pyskat.wui.jinja import RenderTemplateDep
from pyskat.dependencies import DbSessionDep
from pyskat.data_model import Session, SessionPublic
from pyskat.api.session import raise_not_found
from pyskat.wui.messages import flash_message, Message, MessageCategory


router = APIRouter(prefix="/sessions", tags=["session"])


def get_current_session(db: DbSessionDep, request: Request) -> Session | None:
    current_id = request.session.get("current_session_id", None)
    if current_id:
        try:
            current_id = int(current_id)
        except ValueError:
            flash_message(
                request,
                Message(
                    text="Invalid value stored for current session.",
                    category=MessageCategory.DANGER,
                ),
            )
            return None
        current = db.get(Session, current_id) or raise_not_found(current_id)
        return current

    flash_message(
        request,
        Message(
            text="No current session set.",
            category=MessageCategory.WARNING,
        ),
    )
    return None


def set_current_session(
    db: DbSessionDep, request: Request, session_id: int | None
) -> Session | None:
    session = (
        db.get(Session, session_id) or raise_not_found(session_id)
        if session_id is not None
        else None
    )
    request.session["current_session_id"] = session_id
    return session


CurrentSessionDep = Annotated[Session | None, Depends(get_current_session)]


@router.get("/")
def wui_sessions(
    render_template: RenderTemplateDep,
    db: DbSessionDep,
    request: Request,
    current_session: CurrentSessionDep,
):
    sessions = db.exec(select(Session)).all()
    return render_template(
        "sessions.html",
        sessions=sessions,
        current_session_id=current_session.id if current_session else None,
        now=datetime.today().isoformat(sep=" ", timespec="minutes"),
    )


@router.get("/current", response_model=SessionPublic | None)
def wui_sessions_get_current(db: DbSessionDep, request: Request):
    return get_current_session(db, request)


@router.patch("/current/{session_id}", response_model=SessionPublic)
def wui_sessions_set_current(session_id: int, db: DbSessionDep, request: Request):
    return set_current_session(db, request, session_id)


@router.delete("/current", response_model=SessionPublic | None)
def wui_sessions_delete_current(db: DbSessionDep, request: Request):
    return set_current_session(db, request, None)
