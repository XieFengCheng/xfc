# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    the class of base model
    db connection session

usage:
    

------------------------------------------------
"""
import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from deploy.config import DB_LINK
from deploy.utils.logger import logger as LOG

DBSession = None


if not DB_LINK:
    LOG.critical('DB configuration is unavail')
    sys.exit(1)

db_link = DB_LINK

ModelBase = declarative_base()


def init_database_engine():
    return create_engine(
        db_link,
        echo=False,
        pool_recycle=800,
        pool_size=100
    )


def get_session():
    global DBSession
    if not DBSession:
        dbengine_databus = init_database_engine()
        DBSession = sessionmaker(bind=dbengine_databus,
                                 autocommit=True)
    return DBSession()

