import os
from datetime import datetime

import yaml
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

CWD = os.path.dirname(__file__)
with open(os.path.join(CWD, 'config.yml'), 'r') as config_file:
    cfg = yaml.load(config_file)

ENGINE = create_engine('sqlite:///' + os.path.join(CWD, cfg['sqlite']['db']), echo=True)

Base = declarative_base()


class Partner(Base):
    __tablename__ = 'partner'
    id = Column(Integer, primary_key=True)
    logo_url = Column(String, nullable=False)
    html = Column(String, nullable=False)
    published_time = Column(DateTime, nullable=False, default=datetime.now())
    modified_time = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    hidden = Column(Boolean, nullable=False, default=False)


class Activity(Base):
    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    html = Column(String, nullable=False)
    thumbnail = Column(String)
    activity_time = Column(DateTime, nullable=False)
    published_time = Column(DateTime, nullable=False, default=datetime.now())
    modified_time = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    hidden = Column(Boolean, nullable=False, default=False)
    is_link = Column(Boolean, nullable=False, default=False)
    link = Column(String, default=None)


class Hero(Base):
    __tablename__ = 'hero'
    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)
    description = Column(String, nullable=True)


class Link(Base):
    __tablename__ = 'link'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)


class Misc(Base):
    __tablename__ = 'misc'
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)


Base.metadata.create_all(ENGINE)
Session = sessionmaker(bind=ENGINE)


def insert_partner(logo_url: str, html: str):
    session = Session()
    partner = Partner(logo_url=logo_url, html=html)
    session.add(partner)
    session.commit()


def select_partner_all(hidden=False):
    session = Session()
    query = session.query(Partner)
    if hidden is not None:
        query = query.filter_by(hidden=hidden)
    return query.all()


def select_partner_by_id(partner_id: int):
    session = Session()
    return session.query(Partner).get(partner_id)


def update_partner(partner_id: int, param: dict):
    session = Session()
    session.query(Partner).filter_by(id=partner_id).update(param)
    session.commit()


def toggle_partner(partner_id: int):
    session = Session()
    partner = session.query(Partner).get(partner_id)
    partner.hidden = not partner.hidden
    session.commit()


def remove_partner(partner_id: int):
    session = Session()
    session.query(Partner).filter_by(id=partner_id).delete()
    session.commit()


def insert_activity(title: str, html: str, thumbnail: str, activity_time: str):
    session = Session()
    activity = Activity(title=title, html=html, thumbnail=thumbnail, activity_time=activity_time)
    session.add(activity)
    session.commit()


def select_activity_all(hidden=False):
    session = Session()
    query = session.query(Activity)
    if hidden is not None:
        query = query.filter_by(hidden=hidden)
    return query.order_by(Activity.activity_time.desc()).all()


def select_activity_limit(limit=4):
    session = Session()
    return session.query(Activity).filter_by(hidden=False).order_by(Activity.activity_time.desc())[:limit]


def select_activity_by_id(activity_id: int):
    session = Session()
    return session.query(Activity).get(activity_id)


def update_activity(activity_id: int, param: dict):
    session = Session()
    session.query(Activity).filter_by(id=activity_id).update(param)
    session.commit()


def toggle_activity(activity_id: int):
    session = Session()
    activity = session.query(Activity).get(activity_id)
    activity.hidden = not activity.hidden
    session.commit()


def remove_activity(activity_id: int):
    session = Session()
    session.query(Activity).filter_by(id=activity_id).delete()
    session.commit()


def insert_hero(image_url: str, description: str):
    session = Session()
    hero = Hero(image_url=image_url, description=description)
    session.add(hero)
    session.commit()


def select_hero_all():
    session = Session()
    return session.query(Hero).all()


def remove_hero(hero_id: int):
    session = Session()
    session.query(Hero).filter_by(id=hero_id).delete()
    session.commit()


def select_link_all():
    session = Session()
    return session.query(Link).all()


def remove_link(link_id: int):
    session = Session()
    session.query(Link).filter_by(id=link_id).delete()
    session.commit()


def insert_link(name: str, url: str):
    session = Session()
    link = Link(name=name, url=url)
    session.add(link)
    session.commit()


def get_misc(key: str):
    session = Session()
    item = session.query(Misc).filter_by(key=key).first()
    if item:
        return item.value
    return ''


def set_misc(key: str, value: str):
    session = Session()
    item = session.query(Misc).filter_by(key=key).first()
    if item:
        item.value = value
    else:
        item = Misc(key=key, value=value)
        session.add(item)
    session.commit()
