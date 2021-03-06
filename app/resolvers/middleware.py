from ariadne import ObjectType
from ariadne.types import Extension
from functools import wraps
from starlette.requests import Request
from sqlalchemy.orm import Session

from app.db import SessionMaker


class ContextMiddleware(Extension):
    """ Adds a context instance to the request """
    def request_started(self, info: dict):
        # Add context to the request
        info['context'] = Context(info['request'])

    def request_finished(self, info: dict):
        # Close the context
        info['context'].close()


class Context:
    def __init__(self, request: Request):
        self.db: Session = SessionMaker()
        self.request = request

    def close(self):
        self.db.close()


def resolver_rename_arguments(resolver, update):
    """ Rename arguments passed to a resolver
    if the schema used 'input' as an argument it could renamed by passing:
    {'input': 'new name'}
    """
    @wraps(resolver)
    def wrapper(*args, **kwargs):
        for old_key, new_key in update.items():
            kwargs[new_key] = kwargs.pop(old_key)

        return resolver(*args, **kwargs)

    return wrapper


def resolver_add_context(resolver):
    """ Pull the context instance generated by the ContextMiddleware out """

    @wraps(resolver)
    def wrapper(parent, info, **kwargs):
        ctx = info.context['context']
        return resolver(parent, ctx, **kwargs)

    return wrapper


def resolver_decorator(resolver_function, rename: dict = None):
    """ Add a context instance, and rename argument names """
    if rename is not None:
        resolver_function = resolver_rename_arguments(resolver_function, rename)

    resolver_function = resolver_add_context(resolver_function)

    return resolver_function


class ObjectTypeWithContext:
    """ Extends Ariadne's ObjectType to add a Context instance,
    and update argument names when necessary """

    def __init__(self, name: str):
        self.obj = ObjectType(name)

    def field(self, name: str, rename: dict = None):
        """ Add field to schema using a decorator """

        def decorator(resolver_function):
            new_resolver = resolver_decorator(resolver_function, rename=rename)
            self.obj.field(name)(new_resolver)
            return resolver_function

        return decorator

    def add_field(self, name, resolver_function):
        """ Add field to schema """
        self.obj.field(name)(resolver_function)

    def bind_to_schema(self, schema):
        """ Required by Ariadne library """
        self.obj.bind_to_schema(schema)
