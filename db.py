from datetime import datetime

import yaml
from sqlalchemy import create_engine, Table, Column, Integer, String, \
    MetaData, DateTime, Boolean
from sqlalchemy.sql import select, text


with open("config.yml", 'r') as config_file:
    cfg = yaml.load(config_file)

engine = create_engine('sqlite:///' + cfg['sqlite']['db'], echo=True)

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
    Column('activity_time', DateTime, nullable=False),
    Column('published_time', DateTime, nullable=False, default=datetime.now()),
    Column('modified_time', DateTime, nullable=False, default=datetime.now(),
           onupdate=datetime.now()),
    Column('hidden', Boolean, nullable=False, default=False)
)

hero = Table(
    'hero', metadata,
    Column('id', Integer, primary_key=True),
    Column('image_url', String, nullable=False),
    Column('description', String, nullable=True),
)

link = Table(
    'link', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('url', String, nullable=False),
)

misc = Table(
    'misc', metadata,
    Column('id', Integer, primary_key=True),
    Column('key', String, nullable=False, unique=True),
    Column('value', String, nullable=False),
)


metadata.create_all(engine)


def insert_partner(logo_url: str, html: str):
    conn = engine.connect()
    conn.execute(partner.insert(), logo_url=logo_url, html=html)


def select_partner_all(hidden=False):
    conn = engine.connect()
    stmt = select([partner])
    if hidden is not None:
        stmt = stmt.where(partner.c.hidden == hidden)
    return conn.execute(stmt).fetchall()


def select_partner_by_id(partner_id: int):
    conn = engine.connect()
    stmt = select([partner]).where(partner.c.id == partner_id)
    return conn.execute(stmt).fetchone()


def update_partner(partner_id: int, param: dict):
    conn = engine.connect()
    stmt = partner.update().values(param).where(partner.c.id == partner_id)
    conn.execute(stmt)


def toggle_partner(partner_id: int):
    conn = engine.connect()
    stmt = text("UPDATE partner SET hidden = NOT hidden WHERE id = :partner_id")
    stmt = stmt.bindparams(partner_id=partner_id)
    conn.execute(stmt)


def remove_partner(partner_id: int):
    conn = engine.connect()
    stmt = partner.delete().where(partner.c.id == partner_id)
    conn.execute(stmt)


def insert_activity(title: str, html: str, thumbnail: str, activity_time: str):
    conn = engine.connect()
    conn.execute(activity.insert(), title=title, html=html, thumbnail=thumbnail,
                 activity_time=activity_time)


def select_activity_all(hidden=False):
    conn = engine.connect()
    stmt = select([activity])
    if hidden is not None:
        stmt = stmt.where(activity.c.hidden == hidden)
    return conn.execute(stmt).fetchall()


def select_activity_by_id(activity_id: int):
    conn = engine.connect()
    stmt = select([activity]).where(activity.c.id == activity_id)
    return conn.execute(stmt).fetchone()


def update_activity(activity_id: int, param: dict):
    conn = engine.connect()
    stmt = activity.update().values(param).where(activity.c.id == activity_id)
    conn.execute(stmt)


def toggle_activity(activity_id: int):
    conn = engine.connect()
    stmt = text("UPDATE activity SET hidden = NOT hidden "
                "WHERE id = :activity_id")
    stmt = stmt.bindparams(activity_id=activity_id)
    conn.execute(stmt)


def remove_activity(activity_id: int):
    conn = engine.connect()
    stmt = activity.delete().where(activity.c.id == activity_id)
    conn.execute(stmt)


def insert_hero(image_url: str, description: str):
    conn = engine.connect()
    conn.execute(hero.insert(), image_url=image_url, description=description)


def select_hero_all():
    conn = engine.connect()
    stmt = select([hero])
    return conn.execute(stmt).fetchall()


def remove_hero(hero_id: int):
    conn = engine.connect()
    stmt = hero.delete().where(hero.c.id == hero_id)
    conn.execute(stmt)


def select_link_all():
    conn = engine.connect()
    stmt = select([link])
    return conn.execute(stmt).fetchall()


def remove_link(link_id: int):
    conn = engine.connect()
    stmt = link.delete().where(link.c.id == link_id)
    conn.execute(stmt)


def insert_link(name: str, url: str):
    conn = engine.connect()
    conn.execute(link.insert(), name=name, url=url)


def get_misc(key: str):
    conn = engine.connect()
    stmt = select([misc]).where(misc.c.key == key)
    item = conn.execute(stmt).fetchone()
    if item:
        return item['value']
    conn.execute(misc.insert(), key=key, value='')
    return ''


def set_misc(key: str, value: str):
    conn = engine.connect()
    stmt = misc.update().values(dict(value=value)).where(misc.c.key == key)
    conn.execute(stmt)
