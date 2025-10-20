from fastapi import Request
from fastapi.routing import APIRouter
from sqlmodel import select
from typing import Literal

from pyskat.wui.jinja import RenderTemplateDep
from pyskat.dependencies import DbSessionDep
from pyskat.data_model import Match, Session, Result


router = APIRouter(prefix="/results", tags=["result"])


@router.get("/")
def wui_results(
    render_template: RenderTemplateDep,
    db: DbSessionDep,
    request: Request,
):
    actual_session_id = request.session.get("current_session_id", None)
    matches = db.exec(select(Match)).all()
    results = db.exec(select(Result)).all()
    sessions = db.exec(select(Session)).all()
    return render_template(
        "results.html",
        matches=matches,
        results={(r.match_id, r.player_id): r for r in results},
        sessions=sessions,
        session=db.get(Session, actual_session_id),
        filtered_for_session=False,
    )


@router.get("/{session_id}")
def wui_results_session(
    render_template: RenderTemplateDep,
    db: DbSessionDep,
    request: Request,
    session_id: Literal["current"] | int,
):
    actual_session_id = (
        request.session.get("current_session_id", None)
        if session_id == "current"
        else session_id
    )
    print(type(actual_session_id))
    matches = db.exec(
        select(Match).where(Match.session_id == actual_session_id)
        if actual_session_id
        else select(Match)
    ).all()
    results = db.exec(select(Result)).all()
    sessions = db.exec(select(Session)).all()
    return render_template(
        "results.html",
        matches=matches,
        results={(r.match_id, r.player_id): r for r in results},
        sessions=sessions,
        session=db.get(Session, actual_session_id),
        filtered_for_session=True,
    )
