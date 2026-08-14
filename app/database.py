from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import config


def _create_engine():
    if config.DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        if "mode=memory" in config.DATABASE_URL:
            connect_args["uri"] = True
        return create_engine(config.DATABASE_URL, connect_args=connect_args)

    return create_engine(config.DATABASE_URL)


engine = _create_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
