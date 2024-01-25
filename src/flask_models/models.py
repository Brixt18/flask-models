import logging
import secrets
from datetime import datetime
from sqlite3 import IntegrityError
from typing import TypeVar, Union

from flask import abort
from flask_sqlalchemy.query import Query
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Any

from .const import *

try:
    from flask_login import current_user

except ImportError:
    logging.warning(
        "Could not import 'flask_login'. Any 'check_auth' will be True.")

T = TypeVar("T")


class CRUD:
    __abstract__ = True

    @staticmethod
    def _check_auth(check_auth: bool) -> bool:
        """
        Check the current user's authentication status.

        PARAMS
        ------
        check_auth: bool - Indicates whether the current user's authentication status should be checked. Default is True.

        RETURNS
        -------
        bool - False if the user is not authenticated and check_auth is True, True otherwise.
        """
        try:
            if (check_auth) and (not current_user.is_authenticated):
                return False

        except:
            pass

        return True

    def _exist_token(self, token: str) -> bool:
        """
        Check if the given token already exists in the database

        PARAMS
        ------
        token: str - token to check if exists

        RETURNS
        -------
        bool - True if the token already exists in the database, False otherwise.
        """
        query = self.get_by_token(token)

        if (query is None) or (query.id == self.id):
            return False

        return True

    def generate_token(self, length: int = 15) -> str:
        """
        Generates a token for the current object, if the object does not have one already. It is assumed that the 'token' field is unique in the database.

        PARAMS
        ------
        length: int - The length of the token to be generated. Default is 15.

        RETURNS
        -------
        str - The generated token.
        """
        if not self.token:
            self.token = secrets.token_hex(length)

        while self._exist_token(self.token):
            self.token = secrets.token_hex(length)

        return self.token

    def save(self: T, check_auth: bool = True, generate_token: bool = True, hash_password: bool = True) -> T:
        """
        Save the current object to the database.

        PARAMS
        ------
        check_auth: bool - Indicates whether the current user's authentication status should be checked before saving the object. Default is True.
        generate_token: bool - Indicates whether a token should be generated for each object before saving. Default is True.
        hash_password: bool - Indicates whether the password should be hashed before saving the object, if the model has the attribute "password" otherwise will be ignored. Default is True.

        RETURNS
        -------
        self - The current object itself.
        """
        if self._check_auth(check_auth):
            db.session.begin_nested()  # create checkpoint
            db.session.add(self)

            if generate_token:
                self.generate_token()

            if (hash_password) and (hasattr(self, "password")) and (isinstance(self.password, str)):
                self.password = generate_password_hash(self.password)

            # commit
            try:
                db.session.commit()

            except Exception as e:
                logging.exception(e)
                db.session.rollback()

        return self

    def delete(self, soft: bool = True, check_auth: bool = True) -> None:
        """
        Delete the current object from the database.

        PARAMS
        ------
        check_auth: bool - Indicates whether the current user's authentication status should be checked before deleting the object. Default is True.
        soft: bool, optional
                If True, performs a soft delete by marking the object as inactive instead of physically removing it from the database. For soft-deletes it is necessary to set `self.is_active` field (included in the `Model`).
                If False, performs a hard delete by permanently removing the object from the database. Default is True.

        RETURNS
        -------
        None - The method does not return any value.
        """
        if self._check_auth(check_auth):
            db.session.begin_nested()
            try:
                if soft:
                    self.update({"is_active": False})

                else:
                    db.session.delete(self)

                db.session.commit()

            except Exception as e:
                logging.exception(e)
                db.session.rollback()

    def update(self: T, data: dict, check_auth: bool = True) -> T:
        """
        Update the current object with the given data.

        PARAMS
        ------
        data: dict - A dictionary containing the data to update the current object with.
        check_auth: bool - Indicates whether the current user's authentication status should be checked before updating the object. Default is True.

        RETURNS
        -------
        self - The current object itself.
        """
        if self._check_auth(check_auth):
            db.session.begin_nested()
            try:
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

                if hasattr(self, "updated_at"):
                    self.updated_at = datetime.utcnow()

                db.session.commit()

            except Exception as e:
                logging.exception(e)
                db.session.rollback()

        return self

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the hashed password of the current object.

        PARAMS
        ------
        password: str - The plain text password to check.

        RETURNS
        -------
        bool - Returns True if the provided password matches the hashed password of the current object, False otherwise.
        """
        return check_password_hash(self.password, password)

    @classmethod
    def bulk_save(cls, objects: list, check_auth: bool = True, generate_token: bool = True) -> None:
        """
        Save multiple objects to the database in a single transaction.

        PARAMS
        ------
        objects: list - A list of objects to be saved.
        check_auth: bool - Indicates whether the current user's authentication status should be checked before saving the objects. Default is True.
        generate_token: bool - Indicates whether a token should be generated for each object before saving. Default is True.

        RETURNS
        -------
        None - The method does not return any value.
        """
        if cls._check_auth(check_auth):
            db.session.begin_nested()

            if generate_token:
                for obj in objects:
                    obj.generate_token()

            try:
                db.session.add_all(objects)
                db.session.commit()

            except Exception as e:
                logging.exception(e)
                db.session.rollback()

    @classmethod
    def get_by_id(cls: T, id: Any, or_404: bool = False) -> Union[T, None]:
        """
        Retrieves a record from the class's model by its primary key (`db.Column(..., primary_key=True)`).

        PARAMS
        ------
        id: Any - id of the record to retrieve.
        or_404: bool - Indicates whether a 404 error should be raised if the record is not found. Default is False.

        RETURNS
        -------
        object | None - The object representing the record, or None if not found and or_404 is False.
        """
        query = cls.query.get(id)

        if (not query) and (or_404):
            abort(404)

        return query

    @classmethod
    def get_by_token(cls: T, token: str, or_404: bool = False) -> Union[T, None]:
        """
        Retrieves a record from the class's model by its token. It is assumed that the 'token' field is unique in the database.

        PARAMS
        ------
        token: str - Token of the record to retrieve.
        or_404: bool - Indicates whether a 404 error should be raised if the record is not found. Default is False.

        RETURNS
        -------
        object | None - The object representing the record, or None if not found and or_404 is False.
        """
        query = cls.query.filter_by(token=token).first()

        if (not query) and (or_404):
            abort(404)

        return query

    @classmethod
    def get_all(cls: T, limit: int = None, basequery: bool = False) -> Union[list[T], Query]:
        """
        Retrieves all the records from the class's model, applying an optional limit and returning either the query or the query results.

        PARAMS
        ------
        limit: int - Maximum number of records to be returned. If not provided, no limit will be applied.
        basequery: bool - Indicates whether the query object should be returned or the query results. Default is False.

        RETURNS
        -------
        list | Query - A list of the query results or the query object, depending on the value of the "basequery" parameter.
        """
        query = cls.query.limit(limit)

        return query if basequery else query.all()


class Model(db.Model, CRUD):
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
