from typing import Annotated, Literal, Sequence
from fastapi import Query, Request
from fastapi.routing import APIRouter
from pyskat.wui.jinja import RenderTemplateDep
from pyskat.dependencies import DbSessionDep, SettingsDep
from pyskat.data_model import Session, Match, Player, to_pandas
from pyskat.api.evaluation import evaluate_matches
from pyskat.wui.sessions import get_current_session
import pyskat.api.session as api_session
from sqlmodel import select
import pandas as pd
import plotly.io as pio
import plotly.express as px


router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/")
def wui_evaluation(
    render_template: RenderTemplateDep,
    db: DbSessionDep,
    settings: SettingsDep,
    request: Request,
    sort: Annotated[str, Query()] = "total_score",
    ascending: Annotated[bool, Query()] = False,
):
    matches = db.exec(select(Match)).all()
    return _common(render_template, db, settings, sort, ascending, matches, None)


@router.get("/{session_id}")
def wui_evaluation_session(
    render_template: RenderTemplateDep,
    db: DbSessionDep,
    settings: SettingsDep,
    session_id: Literal["current"] | int,
    request: Request,
    sort: Annotated[str, Query()] = "total_score",
    ascending: Annotated[bool, Query()] = False,
):
    session = (
        get_current_session(db, request)
        if session_id == "current"
        else db.get(Session, session_id) or api_session.raise_not_found(session_id)
    )

    matches = (
        db.exec(select(Match).where(Match.session_id == session.id)).all()
        if session
        else []
    )
    return _common(render_template, db, settings, sort, ascending, matches, session)


def _common(
    render_template,
    db: DbSessionDep,
    settings: SettingsDep,
    sort: Annotated[str, Query()],
    ascending: Annotated[bool, Query()],
    matches: Sequence[Match],
    session: Session | None,
):
    sessions = db.exec(select(Session)).all()
    players = db.exec(select(Player)).all()
    if matches:
        evaluation = evaluate_matches(settings.evaluation, matches)
        evaluation = evaluation.join(
            to_pandas(
                players,
                index_col="id",
                rename_index="player_id",
                rename_columns={"name": "player_name"},
                drop_columns=["active", "remarks"],
            )
        )
        evaluation.reset_index(inplace=True)
        evaluation["player_label"] = (
            evaluation["player_name"]
            + " ("
            + evaluation["player_id"].astype("string")
            + ")"
        )
        evaluation.sort_values(by=sort, inplace=True, ascending=ascending)
        evaluation.reset_index(inplace=True, drop=True)
    else:
        evaluation = pd.DataFrame()

    pio.templates.default = settings.wui.plotly_template
    return render_template(
        "evaluation.html",
        sessions=sessions,
        evaluation_data=evaluation,
        session=session,
        displays=settings.wui.evaluation_displays,
        px=px,
    )
