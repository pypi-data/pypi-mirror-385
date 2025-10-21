import datetime as dt
import logging
import os
import enum
import pathlib
import sys
from typing import Union, ClassVar, Any

import dotenv
import pandas as pd
import pytz
import sqlalchemy.orm
import sqlalchemy.event
import sqlalchemy.exc
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
from pydantic import BaseModel, Field, model_validator
from logging.config import dictConfig

try:
    import uvicorn.logging
    api_modules_available = True
except ModuleNotFoundError:
    # API dependencies are not installed, log only to standard output, no file.
    api_modules_available = False

dotenv.load_dotenv()

ROOT_DIR = os.path.abspath(pathlib.Path(__file__).parent.parent)
log_dir = os.path.join(ROOT_DIR, 'logs')
log_fname = os.path.join(log_dir, 'server.log')

API_LOCAL_BASE_URL = "http://127.0.0.1:8000/"
API_TOKEN = "harvestIT"

ORMBase = declarative_base()

ORMBase.metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_`%(constraint_name)s`",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})


async def handle_api_exceptions(caller: str, error_message: str, exception):
    print(f"[handle_api_exceptions] /!\\ An exception ocurred in {caller}. Preparing API and LOG entries...")

    err_type, err_obj, traceback = sys.exc_info()

    # details_dict = {"error_message": error_message, "exception_info": exception.}


class MissingEnvVar(Exception):
    def __init__(self, key):
        super().__init__("Value not found. This information should be stored in env variable " +
                         key + ". use: os.environ['" + key + "'] = <values>")


class LogConfig(BaseModel):
    """
    Logging configuration to be set for the server.

    Notes
    -----
    Modified code snipped originally by "Yash Nag" taken from:
    https://stackoverflow.com/questions/63510041/adding-python-logging-to-fastapi-endpoints-hosted-on-docker-doesnt-display-api

    """

    # Class constants (not fields) - use ClassVar to prevent Pydantic from treating them as model fields
    FILE_LOG_FORMAT: ClassVar[str] = "|%(asctime)s| [%(levelname)s -> %(module)s] : %(message)s"
    STD_OUT_LOG_FORMAT: ClassVar[str] = "%(levelprefix)s |%(asctime)s| %(message)s"
    LOG_LEVEL: ClassVar[str] = "DEBUG"

    # Logging config - all fields need type annotations for Pydantic v2
    version: int = Field(default=1)
    disable_existing_loggers: bool = Field(default=False)
    formatters: dict[str, Any] = Field(default_factory=dict)
    handlers: dict[str, Any] = Field(default_factory=dict)
    loggers: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='before')
    @classmethod
    def setup_logging_config(cls, data: Any) -> Any:
        """Set up formatters, handlers, and loggers based on api_modules_available."""
        # Create log directory if it does not exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Use class-level constants
        FILE_FMT = "|%(asctime)s| [%(levelname)s -> %(module)s] : %(message)s"
        STD_OUT_FMT = "%(levelprefix)s |%(asctime)s| %(message)s"
        LEVEL = "DEBUG"

        # Set up formatters based on whether API modules are available
        if api_modules_available:
            data['formatters'] = {
                "std_out": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": STD_OUT_FMT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "file_out": {
                    "format": FILE_FMT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            }
        else:
            # Use standard Python logging format (without uvicorn-specific %(levelprefix)s)
            data['formatters'] = {
                "std_out": {
                    "format": FILE_FMT,  # Use FILE_FMT which doesn't have %(levelprefix)s
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            }

        # Set up handlers
        data['handlers'] = {
            "default": {
                "formatter": "std_out",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            }
        }

        # Set up loggers
        data['loggers'] = {"sp_logger": {"handlers": ["default"], "level": LEVEL}}

        # Add file handler and logger if API modules are available
        if api_modules_available:
            data['handlers']["file"] = {
                "formatter": "file_out",
                "class": "logging.FileHandler",
                "level": "WARNING",
                "filename": log_fname
            }
            data['loggers'] = {"sp_logger": {"handlers": ["default", "file"], "level": LEVEL}}

        return data


def get_env(name):
    try:
        value = os.environ[name]
    except KeyError:
        raise MissingEnvVar(name)
    return value


def get_db_conection_string():
    db_type = os.environ.get('HIT_DB_TYPE', 'postgresql')
    host = os.environ.get('HIT_DB_HOST', 'localhost:5432')
    user = os.environ.get('HIT_DB_USER')
    pw = os.environ.get('HIT_DB_PW')
    db_name = os.environ.get('HIT_DB_NAME', 'harvestit')
    dialects = {'postgresql': 'postgresql+psycopg', 'sqlite': 'sqlite'}

    db_str = '{}://'.format(dialects[db_type])
    if user is not None and db_type != 'sqlite':
        db_str = db_str + user
    if pw is not None and db_type != 'sqlite':
        db_str = db_str + ':{}@'.format(pw)
    db_str = '{}{}'.format(db_str, host)
    if db_type != 'sqlite':
        db_str = '{}/{}'.format(db_str, db_name)

    return db_str


S = None
db_engine = None


def create_db_engine():
    global S
    global db_engine
    try:
        if os.environ.get('HIT_DB_TYPE', 'postgresql') == 'sqlite':
            db_engine = sqlalchemy.create_engine(get_db_conection_string(), pool_pre_ping=True,
                                                 connect_args={'timeout': 15, 'check_same_thread': False})
        else:
            db_engine = sqlalchemy.create_engine(get_db_conection_string(), pool_pre_ping=True)
        S = sqlalchemy.orm.sessionmaker(db_engine)
    except (ModuleNotFoundError, sqlalchemy.exc.ArgumentError):
        db_engine = None
        S = None


# @sqlalchemy.event.listens_for(db_engine, "connect")
# def connect(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute(f"SET TIME ZONE utc;")
#     cursor.close()


# logger
dictConfig(LogConfig().model_dump())
sp_logger = logging.getLogger("sp_logger")
create_db_engine()


class VerifyValidateMode(str, enum.Enum):
    validate = 'validate'
    verify = 'verify'


class DatetimeTemplates(enum.Enum):
    year_month_day = "year_month_day"
    day_month_year = "day_month_year"
    month_day_year = "month_day_year"


# Timestamp-related utilities

def to_utc(ds: str) -> dt.datetime:
    """Return timezone-aware datetime in UTC from ISO format datetime string
    """
    return pytz.utc.localize(dt.datetime.fromisoformat(ds))


def to_unix_str(ds: str) -> str:
    """Return UNIX ms timestamp from ISO format datetime string.
    """
    return str(int(1000 * to_utc(ds).timestamp()))


def utc_str(x: Union[str, dt.datetime, pd.Timestamp]) -> str:
    """Return ISO string from datetime or UNIX ms timestamp (given as string).
    """
    fmt = "%Y-%m-%d %H:%M:%S"
    if isinstance(x, (dt.datetime, pd.Timestamp)):
        return x.strftime(fmt)
    return dt.datetime.utcfromtimestamp(int(x) / 1000).strftime(fmt)


def json_to_df(j: dict) -> pd.DataFrame:
    """Convert json data returned by get-sensor-data API endpoint to DataFrame with UTC index.
    """
    df = pd.DataFrame(
        list(j.items()), columns=["unix_timestamps_ms", "values"], dtype=float
    )
    df.index = pd.to_datetime(df["unix_timestamps_ms"], unit="ms")
    df.index.name = "utc"
    return df
