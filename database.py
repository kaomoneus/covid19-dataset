import json
import re

from dateutil.parser import parse
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine

from datasource import RegionsCollection


class Base(object):
    @declared_attr
    def __tablename__(cls):
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', cls.__name__).lower()

    id = Column(Integer, primary_key=True, index=True)

Base = declarative_base(cls=Base)

def _get_or_add(session: Session, cls, **kwargs):
    try:
        session.flush()
        return session.query(cls).filter_by(**kwargs)
    except NoResultFound:
        t = cls(**kwargs)
        session.add(t)
        return t


class Date(Base):
    datetime = Column(DateTime)

    @classmethod
    def get(cls, session: Session, yy_mm_dd: str):
        date = parse(yy_mm_dd)
        return _get_or_add(session, cls, datetime=date)


class Request(Base):
    url = Column(String(1024))

    @classmethod
    def get(cls, session: Session, url: str):
        return _get_or_add(session, cls, url=url)


class AreasCollection(Base):
    name = Column(String(128))

    @classmethod
    def get(cls, session: Session, name: str):
        return _get_or_add(session, cls, name=name)


class Area(Base):
    parent_id = Column(ForeignKey(AreasCollection.id))
    parent = relationship(AreasCollection)

    name = Column(String(128))

    @classmethod
    def get(cls, session: Session, name: str):
        return _get_or_add(session, cls, name=name)


class DailyStats(Base):
    date_id = Column(ForeignKey(Date.id))
    date = relationship(Date)

    request_id = Column(ForeignKey(Request.id))
    request = relationship(Request)

    area_id = Column(ForeignKey(Area.id))
    area = relationship(Area)

    cases = Column(Integer)
    cured = Column(Integer)
    deaths = Column(Integer)

    @classmethod
    def get(cls, session: Session, date: Date, request: Request, area: Area):
        return _get_or_add(session, cls, date=Date, request=request, area=area)


def connect(dburl: str):
    engine = create_engine(dburl, echo = False)
    connection = engine.connect()

    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    ))

    return engine, Session


def consume_stats_version_0(
    session,
    request: Request,
    data: dict,
    name: str
):
    area = RegionsCollection(data, name)

    for r in area.regions:
        area = Area.get(session, r.name)

        dates = [Date.get(session, d) for d in area.dates]
        daily_stats = area.daily_stats(r.id)

        for i in range(0, len(dates)):
            date = dates[i]
            d = daily_stats[i]
            daily = DailyStats.get(session, date, request, area)
            daily.deaths = d.deaths.x
            daily.cases = d.cases.x
            daily.cured = d.cured.x

    session.flush()


def consume_data_verion_0(db: str, path: str):

    try:
        request_url = f'sqlite:///{db}'
        e, sm = connect(request_url)
        session = sm()

        with open(path) as json_file:
            data = json.load(json_file)

            request = Request.get(session, request_url)

            consume_stats_version_0(
                session=session,
                request=request,
                data=data['russia_stat_struct'],
                name="Россия"
            )

            consume_stats_version_0(
                session=session,
                request=request,
                data=data['world_stat_struct'],
                name="Мир"
            )

            session.commit()

    except Exception as e:
        ValueError("Failed consume data")

