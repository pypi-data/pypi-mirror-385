# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2025-08-20
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Database error methods.
"""


from typing import Any, NoReturn, TypeVar, Generic
from collections.abc import Callable
from inspect import iscoroutinefunction
from traceback import StackSummary
from functools import wraps as functools_wraps
from reykit.rbase import T, Exit, catch_exc

from . import rengine
from . import rorm
from .rbase import DatabaseBase


__all__ = (
    'DatabaseORMTableError',
    'DatabaseErrorSuper',
    'DatabaseError',
    'DatabaseErrorAsync'
)


DatabaseEngineT = TypeVar('DatabaseEngineT', 'rengine.DatabaseEngine', 'rengine.DatabaseEngineAsync')


class DatabaseORMTableError(rorm.Table):
    """
    Database `error` table ORM model.
    """

    __name__ = 'error'
    __comment__ = 'Error log table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':create_time', not_null=True, index_n=True, comment='Record create time.')
    id: int = rorm.Field(rorm.types_mysql.INTEGER(unsigned=True), key_auto=True, comment='ID.')
    type: str = rorm.Field(rorm.types.VARCHAR(50), not_null=True, index_n=True, comment='Error type.')
    data: str = rorm.Field(rorm.types.JSON, comment='Error data.')
    stack: str = rorm.Field(rorm.types.JSON, comment='Error code traceback stack.')
    note: str = rorm.Field(rorm.types.VARCHAR(500), comment='Error note.')


class DatabaseErrorSuper(DatabaseBase, Generic[DatabaseEngineT]):
    """
    Database error super type.
    Can create database used `self.build_db` method.
    """

    _checked: bool = False


    def __init__(self, engine: DatabaseEngineT) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        engine: Database engine.
        """

        # Build.
        self.engine = engine

        # Build Database.
        if not self._checked:
            if type(self) == DatabaseError:
                self.build_db()
            elif type(self) == DatabaseErrorAsync:
                engine.sync_database.error.build_db()
            self._checked = True


    def handle_build_db(self) -> tuple[list[type[DatabaseORMTableError]], list[dict[str, Any]]]:
        """
        Handle method of check and build database tables.

        Returns
        -------
        Build database parameter.
        """

        # Parameter.
        database = self.engine.database

        ## Table.
        tables = [DatabaseORMTableError]

        ## View stats.
        views_stats = [
            {
                'path': 'stats_error',
                'items': [
                    {
                        'name': 'count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{database}`.`error`'
                        ),
                        'comment': 'Error log count.'
                    },
                    {
                        'name': 'past_day_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{database}`.`error`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) = 0'
                        ),
                        'comment': 'Error log count in the past day.'
                    },
                    {
                        'name': 'past_week_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{database}`.`error`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) <= 6'
                        ),
                        'comment': 'Error log count in the past week.'
                    },
                    {
                        'name': 'past_month_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{database}`.`error`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) <= 29'
                        ),
                        'comment': 'Error log count in the past month.'
                    },
                    {
                        'name': 'last_time',
                        'select': (
                            'SELECT MAX(`create_time`)\n'
                            f'FROM `{database}`.`error`'
                        ),
                        'comment': 'Error log last record create time.'
                    }
                ]
            }
        ]

        return tables, views_stats


    def handle_record(
        self,
        exc: BaseException,
        stack: StackSummary,
        note: str | None = None
    ) -> None:
        """
        Insert exception information into the table of database.

        Parameters
        ----------
        exc : Exception instance.
        stack : Exception traceback stack instance.
        note : Exception note.
        """

        # Parameter.
        exc_type = type(exc).__name__
        exc_data = list(exc.args) or None
        exc_stack = [
            {
                'file': frame.filename,
                'line': frame.lineno,
                'frame': frame.name,
                'code': frame.line
            }
            for frame in stack
        ]
        data = {
            'type': exc_type,
            'data': exc_data,
            'stack': exc_stack,
            'note': note
        }

        return data


class DatabaseError(DatabaseErrorSuper['rengine.DatabaseEngine']):
    """
    Database error type.
    Can create database used `self.build_db` method.
    """


    def build_db(self) -> None:
        """
        Check and build database tables.
        """

        # Parameter.
        tables, views_stats = self.handle_build_db()

        # Build.
        self.engine.build.build(tables=tables, views_stats=views_stats, skip=True)


    def record(
        self,
        exc: BaseException,
        stack: StackSummary,
        note: str | None = None
    ) -> None:
        """
        Insert exception information into the table of database.

        Parameters
        ----------
        exc : Exception instance.
        stack : Exception traceback stack instance.
        note : Exception note.
        """

        # Parameter.
        data = self.handle_record(exc, stack, note)

        # Insert.
        self.engine.execute.insert(
            'error',
            data=data
        )


    __call__ = record


    def record_catch(
        self,
        note: str | None = None,
        filter_type : BaseException | tuple[BaseException, ...] = Exit
    ) -> NoReturn:
        """
        Catch and insert exception information into the table of database and throw exception, must used in except syntax.

        Parameters
        ----------
        note : Exception note.
        filter_type : Exception types of not insert, but still throw exception.
        """

        # Parameter.
        _, exc, stack = catch_exc()

        # Filter.
        for type_ in filter_type:
            if isinstance(exc, type_):
                break

        # Record.
        else:
            self.record(exc, stack, note)

        # Throw exception.
        raise


    def wrap(
        self,
        func: Callable[..., T] | None = None,
        note: str | None = None,
        filter_type : BaseException | tuple[BaseException, ...] = Exit
    ) -> T | Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator, insert exception information into the table of database and throw exception.

        Parameters
        ----------
        func : Function.
        note : Exception note.
        filter_type : Exception types of not insert, but still throw exception.

        Returns
        -------
        Decorated function or decorator with parameter.

        Examples
        --------
        Method one.
        >>> @wrap
        >>> def func(*args, **kwargs): ...

        Method two.
        >>> @wrap(*wrap_args, **wrap_kwargs)
        >>> def func(*args, **kwargs): ...

        Method three.
        >>> def func(*args, **kwargs): ...
        >>> func = wrap(func, *wrap_args, **wrap_kwargs)

        Method four.
        >>> def func(*args, **kwargs): ...
        >>> wrap = wrap(*wrap_args, **wrap_kwargs)
        >>> func = wrap(func)

        >>> func(*args, **kwargs)
        """

        # Parameter.
        if issubclass(filter_type, BaseException):
            filter_type = (filter_type,)


        def _wrap(func_: Callable[..., T]) -> Callable[..., T]:
            """
            Decorator, insert exception information into the table of database.

            Parameters
            ----------
            _func : Function.

            Returns
            -------
            Decorated function.
            """


            @functools_wraps(func_)
            def _func(*args, **kwargs) -> Any:
                """
                Decorated function.

                Parameters
                ----------
                args : Position arguments of function.
                kwargs : Keyword arguments of function.

                Returns
                -------
                Function return.
                """

                # Try execute.
                try:
                    result = func_(*args, **kwargs)

                # Record.
                except BaseException:
                    self.record_catch(note, filter_type)

                return result


            return _func


        # Decorator.
        if func is None:
            return _wrap

        # Decorated function.
        else:
            _func = _wrap(func)
            return _func


class DatabaseErrorAsync(DatabaseErrorSuper['rengine.DatabaseEngineAsync']):
    """
    Asynchronous database error type.
    Can create database used `self.build_db` method.
    """


    async def build_db(self) -> None:
        """
        Asynchronous check and build database tables.
        """

        # Parameter.
        tables, views_stats = self.handle_build_db()

        # Build.
        await self.engine.build.build(tables=tables, views_stats=views_stats, skip=True)


    async def record(
        self,
        exc: BaseException,
        stack: StackSummary,
        note: str | None = None
    ) -> None:
        """
        Asynchronous insert exception information into the table of database.

        Parameters
        ----------
        exc : Exception instance.
        stack : Exception traceback stack instance.
        note : Exception note.
        """

        # Parameter.
        data = self.handle_record(exc, stack, note)

        # Insert.
        await self.engine.execute.insert(
            'error',
            data=data
        )


    __call__ = record


    async def record_catch(
        self,
        note: str | None = None,
        filter_type : BaseException | tuple[BaseException, ...] = Exit
    ) -> NoReturn:
        """
        Asynchronous catch and insert exception information into the table of database and throw exception, must used in except syntax.

        Parameters
        ----------
        note : Exception note.
        filter_type : Exception types of not insert, but still throw exception.
        """

        # Parameter.
        _, exc, stack = catch_exc()

        # Filter.
        for type_ in filter_type:
            if isinstance(exc, type_):
                break

        # Record.
        else:
            await self.record(exc, stack, note)

        # Throw exception.
        raise


    def wrap(
        self,
        func: Callable[..., T] | None = None,
        *,
        note: str | None = None,
        filter_type : BaseException | tuple[BaseException, ...] = Exit
    ) -> T | Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Asynchronous decorator, insert exception information into the table of database, throw exception.

        Parameters
        ----------
        func : Function.
        note : Exception note.
        filter_type : Exception types of not insert, but still throw exception.

        Returns
        -------
        Decorated function or decorator with parameter.

        Examples
        --------
        Method one.
        >>> @wrap
        >>> [async ]def func(*args, **kwargs): ...

        Method two.
        >>> @wrap(**wrap_kwargs)
        >>> [async ]def func(*args, **kwargs): ...

        Method three.
        >>> [async ]def func(*args, **kwargs): ...
        >>> func = wrap(func, *wrap_args, **wrap_kwargs)

        Method four.
        >>> [async ]def func(*args, **kwargs): ...
        >>> wrap = wrap(*wrap_args, **wrap_kwargs)
        >>> func = wrap(func)

        Must asynchronous execute.
        >>> await func(*args, **kwargs)
        """

        # Parameter.
        if issubclass(filter_type, BaseException):
            filter_type = (filter_type,)


        def _wrap(func_: Callable[..., T]) -> Callable[..., T]:
            """
            Decorator, insert exception information into the table of database.

            Parameters
            ----------
            _func : Function.

            Returns
            -------
            Decorated function.
            """


            @functools_wraps(func_)
            async def _func(*args, **kwargs) -> Any:
                """
                Decorated function.

                Parameters
                ----------
                args : Position arguments of function.
                kwargs : Keyword arguments of function.

                Returns
                -------
                Function return.
                """

                # Try execute.
                try:
                    if iscoroutinefunction(func_):
                        result = await func_(*args, **kwargs)
                    else:
                        result = func_(*args, **kwargs)

                # Record.
                except BaseException:
                    await self.record_catch(note, filter_type)

                return result


            return _func


        # Decorator.
        if func is None:
            return _wrap

        # Decorated function.
        else:
            _func = _wrap(func)
            return _func
