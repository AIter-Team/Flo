import logging
import os

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .directory_config import MEMORY_DIR

logger = logging.getLogger(__name__)


DB_PATH = os.path.join(MEMORY_DIR, "semantic", "userdata.db")
DB_URL = f"sqlite:///{DB_PATH}"

logger.info(f"Database URL configured: {DB_URL}")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def initialize_db(engine: Engine) -> None:
    """Crete all the database tables"""
    Base.metadata.create_all(engine)
