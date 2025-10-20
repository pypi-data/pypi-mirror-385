from typing import Annotated, Generator
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import URL
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
)
from pathlib import Path

import sqlalchemy
import sqlmodel


class EvaluationSettings(BaseModel):
    won_score: int = 50
    lost_score: int = -50
    opponent_lost_scores: dict[int, int] = {
        4: 30,
        3: 40,
    }
    game_score_multiplier: int = 1

    def get_opponent_lost_score(self, match_size: int):
        result = self.opponent_lost_scores.get(match_size, None)

        if result is None:
            raise ValueError(
                f"Opponent lost score for a match size of {match_size} has not been configured."
            )

        return result


class WuiSettings(BaseModel):
    theme: str = "darkly"
    plotly_template: str | dict = "seaborn"
    additional_template_dirs: list[Path] = []
    evaluation_displays: list[str] = [
        "evaluation_displays/table.html",
        "evaluation_displays/plot_scores.html",
    ]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PYSKAT_",
        env_nested_delimiter="__",
        toml_file="pyskat.toml",
    )

    database_url: str | URL = "sqlite:///pyskat.db"
    session_secret: str = "CHANGE_ME"

    wui: WuiSettings = WuiSettings()
    evaluation: EvaluationSettings = EvaluationSettings()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


settings = Settings()


def get_settings() -> Settings:
    return settings


SettingsDep = Annotated[Settings, Depends(get_settings)]


def _create_engine(settings: Settings):
    engine = sqlalchemy.create_engine(
        settings.database_url, connect_args=dict(check_same_thread=False)
    )
    sqlmodel.SQLModel.metadata.create_all(engine)
    return engine


_engine = _create_engine(settings)
_database_hash = hash(settings.database_url)


def get_db_engine(settings: SettingsDep) -> sqlalchemy.Engine:
    global _database_hash
    global _engine
    db_hash = hash(settings.database_url)
    if db_hash != _database_hash:
        _engine = _create_engine(settings)
        _database_hash = db_hash
    return _engine


DbEngineDep = Annotated[sqlalchemy.Engine, Depends(get_db_engine)]


def get_db_session(engine: DbEngineDep) -> Generator[sqlmodel.Session, None, None]:
    with sqlmodel.Session(engine) as session:
        yield session


DbSessionDep = Annotated[sqlmodel.Session, Depends(get_db_session)]
