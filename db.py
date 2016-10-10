from datetime import datetime

from sqlalchemy import create_engine, Table, Column, Integer, String, \
    MetaData, DateTime, Boolean
from sqlalchemy.sql import select

engine = create_engine('sqlite:///aciwc.db', echo=True)

metadata = MetaData()

partner = Table(
    'partner', metadata,
    Column('id', Integer, primary_key=True), 
    Column('logo_url', String, nullable=False),
    Column('html', String, nullable=False),
    Column('published_time', DateTime, nullable=False, default=datetime.now()),
    Column('modified_time', DateTime, nullable=False, default=datetime.now(),
           onupdate=datetime.now()),
    Column('hidden', Boolean, nullable=False, default=False)
)

activity = Table(
    'activity', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String, nullable=False),
    Column('html', String, nullable=False),
    Column('thumbnail', String),
    Column('published_time', DateTime, nullable=False, default=datetime.now()),
    Column('modified_time', DateTime, nullable=False, default=datetime.now(),
           onupdate=datetime.now()),
    Column('hidden', Boolean, nullable=False, default=False)
)

metadata.create_all(engine)


def insert_partner(logo_url: str, html: str):
    conn = engine.connect()
    conn.execute(partner.insert(), logo_url=logo_url, html=html)


def select_partner_all():
    conn = engine.connect()
    stmt = select([partner]).where(partner.c.hidden == False)
    return conn.execute(stmt).fetchall()


def select_partner_by_id(partner_id: int):
    conn = engine.connect()
    stmt = select([partner]).where(partner.c.id == partner_id)
    return conn.execute(stmt).fetchone()


def update_partner(partner_id: int, param: dict):
    conn = engine.connect()
    stmt = partner.update().values(param).where(partner.c.id == partner_id)
    conn.execute(stmt)


def insert_activity(title: str, html: str, thumbnail: str):
    conn = engine.connect()
    conn.execute(activity.insert(), title=title, html=html, thumbnail=thumbnail)


def select_activity_all():
    conn = engine.connect()
    stmt = select([activity]).where(activity.c.hidden == False)
    return conn.execute(stmt).fetchall()


def select_activity_by_id(activity_id: int):
    conn = engine.connect()
    stmt = select([activity]).where(activity.c.id == activity_id)
    return conn.execute(stmt).fetchone()


def update_activity(activity_id: int, param: dict):
    conn = engine.connect()
    stmt = activity.update().values(param).where(activity.c.id == activity_id)
    conn.execute(stmt)
