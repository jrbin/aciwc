from datetime import datetime

import yaml
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.types import DateTime, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    birthday = Column(DateTime)
    sending_email = Column(Boolean, nullable=False, default=True)
    date_added = Column(DateTime, nullable=False, default=datetime.now())
    date_modified = Column(DateTime, nullable=False, default=datetime.now(),
                           onupdate=datetime.now())
    organization = relationship('Organization', back_populates='people')


class Organization(Base):
    __tablename__ = 'organization'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String)
    email = Column(String)
    phone = Column(String)
    date_added = Column(DateTime, nullable=False, default=datetime.now())
    date_modified = Column(DateTime, nullable=False, default=datetime.now(),
                           onupdate=datetime.now())
    people = relationship('Person', back_populates='organization')


with open("config.yml", 'r') as config_file:
    cfg = yaml.load(config_file)

db = cfg['postgres']
engine = create_engine('postgresql://%s:%s@%s/%s' %
                       (db['username'], db['password'], db['host'], db['db']),
                       echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
