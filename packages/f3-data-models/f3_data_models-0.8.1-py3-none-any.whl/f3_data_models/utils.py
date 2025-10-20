import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generic, List, Optional, Tuple, Type, TypeVar  # noqa

import sqlalchemy
from sqlalchemy import Select, and_, inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import class_mapper, joinedload, sessionmaker
from sqlalchemy.orm.collections import InstrumentedList

from f3_data_models.models import Base


@dataclass
class DatabaseField:
    name: str
    value: object = None


GLOBAL_ENGINE = None
GLOBAL_SESSION = None


def get_engine(echo=False) -> Engine:
    host = os.environ["DATABASE_HOST"]
    user = os.environ["DATABASE_USER"]
    passwd = os.environ["DATABASE_PASSWORD"]
    database = os.environ["DATABASE_SCHEMA"]

    if os.environ.get("USE_GCP", "False") == "False":
        db_url = f"postgresql://{user}:{passwd}@{host}:5432/{database}"
        engine = sqlalchemy.create_engine(db_url, echo=echo)
    else:
        engine: Engine = None
        # connector = Connector()

        # def get_connection():
        #     conn: pg8000.dbapi.Connection = connector.connect(
        #         instance_connection_string=host,
        #         driver="pg8000",
        #         user=user,
        #         password=passwd,
        #         db=database,
        #         ip_type=IPTypes.PUBLIC,
        #     )
        #     return conn

        # engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=get_connection, echo=echo)
    return engine


GLOBAL_ENGINE = get_engine(echo=os.environ.get("SQL_ECHO", "False") == "True")
GLOBAL_SESSION = sessionmaker(bind=GLOBAL_ENGINE)


def get_session():
    return GLOBAL_SESSION()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


T = TypeVar("T")


def _joinedloads(cls: T, query: Select, joinedloads: list | str = None) -> Select:
    if joinedloads is None:
        return query
    if joinedloads == "all":
        joinedloads = [getattr(cls, relationship.key) for relationship in cls.__mapper__.relationships]
    return query.options(*[joinedload(load) for load in joinedloads])


class DbManager:
    @staticmethod
    def get(cls: Type[T], id: int, joinedloads: list | str = None) -> T:
        with session_scope() as session:
            query = select(cls).filter(cls.id == id)
            query = _joinedloads(cls, query, joinedloads)
            record = session.scalars(query).unique().one()
            session.expunge(record)
            return record

    @staticmethod
    def find_records(cls: T, filters: Optional[List], joinedloads: List | str = None) -> List[T]:
        with session_scope() as session:
            query = select(cls)
            query = _joinedloads(cls, query, joinedloads)
            query = query.filter(*filters)
            records = session.scalars(query).unique().all()
            for r in records:
                session.expunge(r)
            return records

    @staticmethod
    def find_first_record(cls: T, filters: Optional[List], joinedloads: List | str = None) -> T:
        with session_scope() as session:
            query = select(cls)
            query = _joinedloads(cls, query, joinedloads)
            query = query.filter(*filters)
            record = session.scalars(query).unique().first()
            if record:
                session.expunge(record)
            return record

    @staticmethod
    def find_join_records2(left_cls: T, right_cls: T, filters) -> List[Tuple[T]]:
        with session_scope() as session:
            result = session.execute(select(left_cls, right_cls).join(right_cls).filter(and_(*filters)))
            records = result.all()
            session.expunge_all()
            return records

    @staticmethod
    def find_join_records3(left_cls: T, right_cls1: T, right_cls2: T, filters, left_join=False) -> List[Tuple[T]]:
        with session_scope() as session:
            result = session.execute(
                select(left_cls, right_cls1, right_cls2)
                .select_from(left_cls)
                .join(right_cls1, isouter=left_join)
                .join(right_cls2, isouter=left_join)
                .filter(and_(*filters))
            )
            records = result.all()
            session.expunge_all()
            return records

    @staticmethod
    def update_record(cls: T, id, fields):
        with session_scope() as session:
            record = session.get(cls, id)
            if not record:
                raise ValueError(f"Record with id {id} not found in {cls.__name__}")

            mapper = class_mapper(cls)
            relationships = mapper.relationships.keys()
            for attr, value in fields.items():
                key = attr if isinstance(attr, str) else attr.key
                print(f"key: {key}, value: {value}")
                if hasattr(cls, key) and key not in relationships:
                    setattr(record, key, value)
                elif key in relationships:
                    # Handle relationships separately
                    relationship = mapper.relationships[key]
                    related_class = relationship.mapper.class_
                    # find mapping of related_class
                    og_primary_key = None
                    for k in related_class.__table__.foreign_keys:
                        if k.references(cls.__table__):
                            og_primary_key = k.constraint.columns[0].name
                            break

                    if isinstance(value, list) and og_primary_key:
                        # Delete existing related records
                        related_class = relationship.mapper.class_
                        related_relationships = class_mapper(related_class).relationships.keys()
                        session.query(related_class).filter(getattr(related_class, og_primary_key) == id).delete()
                        # Add new related records
                        items = [item.__dict__ for item in value]
                        for related_item in items:
                            update_dict = {
                                k: v
                                for k, v in related_item.items()
                                if hasattr(related_class, k) and k not in related_relationships
                            }
                            related_record = related_class(**{og_primary_key: id, **update_dict})
                            session.add(related_record)

    @staticmethod
    def update_records(cls, filters, fields):
        with session_scope() as session:
            objects = session.scalars(select(cls).filter(and_(*filters))).all()

            # Get the list of valid attributes for the class
            valid_attributes = {attr.key for attr in inspect(cls).mapper.column_attrs}
            valid_relationships = {rel.key for rel in inspect(cls).mapper.relationships}

            for obj in objects:
                # Update simple fields
                for attr, value in fields.items():
                    key = attr if isinstance(attr, str) else attr.key
                    if key in valid_attributes and not isinstance(value, InstrumentedList):
                        setattr(obj, key, value)

                # Update relationships separately
                for attr, value in fields.items():
                    key = attr if isinstance(attr, str) else attr.key
                    if key in valid_relationships:
                        # Handle relationships separately
                        relationship = inspect(cls).mapper.relationships[key]
                        related_class = relationship.mapper.class_
                        # find mapping of related_class
                        og_primary_key = None
                        for k in related_class.__table__.foreign_keys:
                            if k.references(cls.__table__):
                                og_primary_key = k.constraint.columns[0].name
                                break

                        if isinstance(value, list) and og_primary_key:
                            # Delete existing related records
                            related_class = relationship.mapper.class_
                            related_relationships = class_mapper(related_class).relationships.keys()
                            session.query(related_class).filter(
                                getattr(related_class, og_primary_key) == obj.id
                            ).delete()
                            # Add new related records
                            items = [item.__dict__ for item in value]
                            for related_item in items:
                                update_dict = {
                                    k: v
                                    for k, v in related_item.items()
                                    if hasattr(related_class, k) and k not in related_relationships
                                }
                                related_record = related_class(**{og_primary_key: obj.id, **update_dict})
                                session.add(related_record)

            session.flush()

    @staticmethod
    def create_record(record: Base) -> Base:
        with session_scope() as session:
            session.add(record)
            session.flush()
            session.expunge(record)
            return record  # noqa

    @staticmethod
    def create_records(records: List[Base]):
        with session_scope() as session:
            session.add_all(records)
            session.flush()
            session.expunge_all()
            return records  # noqa

    @staticmethod
    def create_or_ignore(cls: T, records: List[Base]):
        with session_scope() as session:
            for record in records:
                record_dict = {k: v for k, v in record.__dict__.items() if k != "_sa_instance_state"}
                stmt = insert(cls).values(record_dict).on_conflict_do_nothing()
                session.execute(stmt)
            session.flush()

    @staticmethod
    def upsert_records(cls, records):
        with session_scope() as session:
            for record in records:
                record_dict = {k: v for k, v in record.__dict__.items() if k != "_sa_instance_state"}
                stmt = insert(cls).values(record_dict)
                update_dict = {c.name: getattr(record, c.name) for c in cls.__table__.columns}
                stmt = stmt.on_conflict_do_update(
                    index_elements=[cls.__table__.primary_key.columns.keys()],
                    set_=update_dict,
                )
                session.execute(stmt)
            session.flush()

    @staticmethod
    def delete_record(cls: T, id):
        with session_scope() as session:
            session.query(cls).filter(cls.id == id).delete()
            session.flush()

    @staticmethod
    def delete_records(cls: T, filters, joinedloads: List | str = None):
        with session_scope() as session:
            query = select(cls)
            query = _joinedloads(cls, query, joinedloads)
            query = query.filter(*filters)
            records = session.scalars(query).unique().all()
            for r in records:
                session.delete(r)
            session.flush()

    @staticmethod
    def execute_sql_query(sql_query):
        with session_scope() as session:
            records = session.execute(sql_query)
            return records


def create_diagram():
    from pydot import Dot
    from sqlalchemy_schemadisplay import create_schema_graph

    graph: Dot = create_schema_graph(
        engine=get_engine(),
        metadata=Base.metadata,
        show_datatypes=True,
        show_indexes=True,
        rankdir="LR",
        show_column_keys=True,
    )
    graph.write_png("docs/_static/schema_diagram.png")


if __name__ == "__main__":
    create_diagram()
