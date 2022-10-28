import secrets
from datetime import datetime
from sqlite3 import IntegrityError

from flask import abort
from flask_login import current_user

from .const import *


class BaseQuery:
    pass


def _generate_token(number=10):
	return secrets.token_hex(number)


class _CRUD:
    __abstract__ = True

    def _check_auth(self, check_auth):
        if (check_auth) and (not current_user.is_authenticated):
            return False

        return True

    def save(self, check_auth: bool = True):
        if self._check_auth(check_auth):
            db.session.begin_nested()  # create checkpoint
            db.session.add(self)

            #  generate token
            if not self.token:
                self.token = _generate_token(15)

            while self._exist_token(self.token):
                self.token = _generate_token(15)

            # commit
            try:
                db.session.commit()

            except IntegrityError:
                db.session.rollback()

    def delete(self, check_auth: bool = True):
        if self._check_auth(check_auth):
            db.session.begin_nested()
            try:
                db.session.delete(self)

                db.session.commit()

            except IntegrityError:
                db.session.rollback()

    def update(self, data: dict, check_auth: bool = True):
        if self._check_auth(check_auth):
            db.session.begin_nested()
            try:
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

                if hasattr(self, "updated_at"):
                    self.updated_at = datetime.utcnow()

                db.session.commit()

            except IntegrityError as e:
                db.session.rollback()

    def _exist_token(self, token):
        query = self.get_by_token(token)

        if (query is None) or (query.id == self.id):
            return False

        return True

    @classmethod
    def get_by_id(cls, id, or_404: bool = False, _abort: bool = True) -> "object|None":
        if not hasattr(cls, "id"):
            raise ValueError(f"{cls.__name__} has no 'id' attribute.")

        query = cls.query.filter_by(id=id).first()

        if (not query) and (or_404):
            if _abort:
                abort(404)

            return {}, 404

        return query

    @classmethod
    def get_by_token(cls, token, or_404=False, _abort: bool = True) -> "object|None":
        if not hasattr(cls, "token"):
            raise ValueError(f"{cls.__name__} has no 'token' attribute.")

        query = cls.query.filter_by(token=token).first()

        if (not query) and (or_404):
            if _abort:
                abort(404)

            return {}, 404

        return query

    @classmethod
    def get_all(cls, limit: int = None, basequery: bool = False) -> "list|BaseQuery":
        query = cls.query

        if hasattr(cls, "id_user"):
            query = query.filter_by(id_user=current_user.id)

        query = query.limit(limit)

        return query if basequery else query.all()


class Model(db.Model, _CRUD):
    __abstract__ = True

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    token = COLUMN(STRING(32), unique=True, nullable=False)

    created_at = COLUMN(DATETIME, nullable=False, default=datetime.utcnow())
    updated_at = COLUMN(DATETIME, nullable=False,
                        default=datetime.utcnow(), onupdate=datetime.utcnow())
    is_active = COLUMN(BOOLEAN, nullable=False, default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
