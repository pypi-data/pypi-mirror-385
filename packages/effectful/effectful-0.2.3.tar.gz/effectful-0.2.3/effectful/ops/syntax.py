import collections.abc
import dataclasses
import functools
import inspect
import numbers
import operator
import random
import types
import typing
import warnings
from collections.abc import Callable, Iterable, Mapping
from typing import Annotated, Any, Concatenate

from effectful.ops.types import Annotation, Expr, NotHandled, Operation, Term


@dataclasses.dataclass
class Scoped(Annotation):
    """
    A special type annotation that indicates the relative scope of a parameter
    in the signature of an :class:`Operation` created with :func:`defop` .

    :class:`Scoped` makes it easy to describe higher-order :class:`Operation` s
    that take other :class:`Term` s and :class:`Operation` s as arguments,
    inspired by a number of recent proposals to view syntactic variables
    as algebraic effects and environments as effect handlers.

    As a result, in ``effectful`` many complex higher-order programming constructs,
    such as lambda-abstraction, let-binding, loops, try-catch exception handling,
    nondeterminism, capture-avoiding substitution and algebraic effect handling,
    can be expressed uniformly using :func:`defop` as ordinary :class:`Operation` s
    and evaluated or transformed using generalized effect handlers that respect
    the scoping semantics of the operations.

    .. warning::

        :class:`Scoped` instances are typically constructed using indexing
        syntactic sugar borrowed from generic types like :class:`typing.Generic` .
        For example, ``Scoped[A]`` desugars to a :class:`Scoped` instances
        with ``ordinal={A}``, and ``Scoped[A | B]`` desugars to a :class:`Scoped`
        instance with ``ordinal={A, B}`` .

        However, :class:`Scoped` is not a generic type, and the set of :class:`typing.TypeVar` s
        used for the :class:`Scoped` annotations in a given operation must be disjoint
        from the set of :class:`typing.TypeVar` s used for generic types of the parameters.

    **Example usage**:

    We illustrate the use of :class:`Scoped` with a few case studies of classical
    syntactic variable binding constructs expressed as :class:`Operation` s.

    >>> from typing import Annotated
    >>> from effectful.ops.syntax import Scoped, defop
    >>> from effectful.ops.semantics import fvsof
    >>> x, y = defop(int, name='x'), defop(int, name='y')

    * For example, we can define a higher-order operation :func:`Lambda`
      that takes an :class:`Operation` representing a bound syntactic variable
      and a :class:`Term` representing the body of an anonymous function,
      and returns a :class:`Term` representing a lambda function:

      >>> @defop
      ... def Lambda[S, T, A, B](
      ...     var: Annotated[Operation[[], S], Scoped[A]],
      ...     body: Annotated[T, Scoped[A | B]]
      ... ) -> Annotated[Callable[[S], T], Scoped[B]]:
      ...     raise NotHandled

    * The :class:`Scoped` annotation is used here to indicate that the argument ``var``
      passed to :func:`Lambda` may appear free in ``body``, but not in the resulting function.
      In other words, it is bound by :func:`Lambda`:

      >>> assert x not in fvsof(Lambda(x, x() + 1))

      However, variables in ``body`` other than ``var`` still appear free in the result:

      >>> assert y in fvsof(Lambda(x, x() + y()))

    * :class:`Scoped` can also be used with variadic arguments and keyword arguments.
      For example, we can define a generalized :func:`LambdaN` that takes a variable
      number of arguments and keyword arguments:

      >>> @defop
      ... def LambdaN[S, T, A, B](
      ...     body: Annotated[T, Scoped[A | B]],
      ...     *args: Annotated[Operation[[], S], Scoped[A]],
      ...     **kwargs: Annotated[Operation[[], S], Scoped[A]]
      ... ) -> Annotated[Callable[..., T], Scoped[B]]:
      ...     raise NotHandled

      This is equivalent to the built-in :class:`Operation` :func:`deffn`:

      >>> assert not {x, y} & fvsof(LambdaN(x() + y(), x, y))

    * :class:`Scoped` and :func:`defop` can also express more complex scoping semantics.
      For example, we can define a :func:`Let` operation that binds a variable in
      a :class:`Term` ``body`` to a ``value`` that may be another possibly open :class:`Term` :

      >>> @defop
      ... def Let[S, T, A, B](
      ...     var: Annotated[Operation[[], S], Scoped[A]],
      ...     val: Annotated[S, Scoped[B]],
      ...     body: Annotated[T, Scoped[A | B]]
      ... ) -> Annotated[T, Scoped[B]]:
      ...     raise NotHandled

      Here the variable ``var`` is bound by :func:`Let` in `body` but not in ``val`` :

      >>> assert x not in fvsof(Let(x, y() + 1, x() + y()))

      >>> fvs = fvsof(Let(x, y() + x(), x() + y()))
      >>> assert x in fvs and y in fvs

      This is reflected in the free variables of subterms of the result:

      >>> assert x in fvsof(Let(x, x() + y(), x() + y()).args[1])
      >>> assert x not in fvsof(Let(x, y() + 1, x() + y()).args[2])
    """

    ordinal: collections.abc.Set

    def __class_getitem__(cls, item: typing.TypeVar | typing._SpecialForm):
        assert not isinstance(item, tuple), "can only be in one scope"
        if isinstance(item, typing.TypeVar):
            return cls(ordinal=frozenset({item}))
        elif typing.get_origin(item) is typing.Union and typing.get_args(item):
            return cls(ordinal=frozenset(typing.get_args(item)))
        else:
            raise TypeError(
                f"expected TypeVar or non-empty Union of TypeVars, but got {item}"
            )

    @staticmethod
    def _param_is_var(param: type | inspect.Parameter) -> bool:
        """
        Helper function that checks if a parameter is annotated as an :class:`Operation` .

        :param param: The parameter to check.
        :returns: ``True`` if the parameter is an :class:`Operation` , ``False`` otherwise.
        """
        if isinstance(param, inspect.Parameter):
            param = param.annotation
        if typing.get_origin(param) is Annotated:
            param = typing.get_args(param)[0]
        if typing.get_origin(param) is not None:
            param = typing.cast(type, typing.get_origin(param))
        return isinstance(param, type) and issubclass(param, Operation)

    @classmethod
    def _get_param_ordinal(cls, param: type | inspect.Parameter) -> collections.abc.Set:
        """
        Given a type or parameter, extracts the ordinal from its :class:`Scoped` annotation.

        :param param: The type or signature parameter to extract the ordinal from.
        :returns: The ordinal typevars.
        """
        if isinstance(param, inspect.Parameter):
            return cls._get_param_ordinal(param.annotation)
        elif typing.get_origin(param) is Annotated:
            for a in typing.get_args(param)[1:]:
                if isinstance(a, cls):
                    return a.ordinal
            return set()
        else:
            return set()

    @classmethod
    def _get_root_ordinal(cls, sig: inspect.Signature) -> collections.abc.Set:
        """
        Given a signature, computes the intersection of all :class:`Scoped` annotations.

        :param sig: The signature to check.
        :returns: The intersection of the `ordinal`s of all :class:`Scoped` annotations.
        """
        return set(cls._get_param_ordinal(sig.return_annotation)).intersection(
            *(cls._get_param_ordinal(p) for p in sig.parameters.values())
        )

    @classmethod
    def _get_fresh_ordinal(cls, *, name: str = "RootScope") -> collections.abc.Set:
        return {typing.TypeVar(name)}

    @classmethod
    def _check_has_single_scope(cls, sig: inspect.Signature) -> bool:
        """
        Checks if each parameter has at most one :class:`Scoped` annotation.

        :param sig: The signature to check.
        :returns: True if each parameter has at most one :class:`Scoped` annotation, False otherwise.
        """
        # invariant: at most one Scope annotation per parameter
        return not any(
            len([a for a in p.annotation.__metadata__ if isinstance(a, cls)]) > 1
            for p in sig.parameters.values()
            if typing.get_origin(p.annotation) is Annotated
        )

    @classmethod
    def _check_no_typevar_overlap(cls, sig: inspect.Signature) -> bool:
        """
        Checks if there is no overlap between ordinal typevars and generic ones.

        :param sig: The signature to check.
        :returns: True if there is no overlap between ordinal typevars and generic ones, False otherwise.
        """

        def _get_free_type_vars(
            tp: type | typing._SpecialForm | inspect.Parameter | tuple | list,
        ) -> collections.abc.Set[typing.TypeVar]:
            if isinstance(tp, typing.TypeVar):
                return {tp}
            elif isinstance(tp, tuple | list):
                return set().union(*map(_get_free_type_vars, tp))
            elif isinstance(tp, inspect.Parameter):
                return _get_free_type_vars(tp.annotation)
            elif typing.get_origin(tp) is Annotated:
                return _get_free_type_vars(typing.get_args(tp)[0])
            elif typing.get_origin(tp) is not None:
                return _get_free_type_vars(typing.get_args(tp))
            else:
                return set()

        # invariant: no overlap between ordinal typevars and generic ones
        free_type_vars = _get_free_type_vars(
            (sig.return_annotation, *sig.parameters.values())
        )
        return all(
            free_type_vars.isdisjoint(cls._get_param_ordinal(p))
            for p in (
                sig.return_annotation,
                *sig.parameters.values(),
            )
        )

    @classmethod
    def _check_no_boundvars_in_result(cls, sig: inspect.Signature) -> bool:
        """
        Checks that no bound variables would appear free in the return value.

        :param sig: The signature to check.
        :returns: True if no bound variables would appear free in the return value, False otherwise.

        .. note::

            This is used as a post-condition for :func:`infer_annotations`.
            However, it is not a necessary condition for the correctness of the
            `Scope` annotations of an operation - our current implementation
            merely does not extend to cases where this condition is true.
        """
        root_ordinal = cls._get_root_ordinal(sig)
        return_ordinal = cls._get_param_ordinal(sig.return_annotation)
        return not any(
            root_ordinal < cls._get_param_ordinal(p) <= return_ordinal
            for p in sig.parameters.values()
            if cls._param_is_var(p)
        )

    @classmethod
    def infer_annotations(cls, sig: inspect.Signature) -> inspect.Signature:
        """
        Given a :class:`inspect.Signature` for an :class:`Operation` for which
        only some :class:`inspect.Parameter` s have manual :class:`Scoped` annotations,
        computes a new signature with :class:`Scoped` annotations attached to each parameter,
        including the return type annotation.

        The new annotations are inferred by joining the manual annotations with a
        fresh root scope. The root scope is the intersection of all :class:`Scoped`
        annotations in the resulting :class:`inspect.Signature` object.

        :class`Operation` s in this root scope are free in the result and in all arguments.

        :param sig: The signature of the operation.
        :returns: A new signature with inferred :class:`Scoped` annotations.
        """
        # pre-conditions
        assert cls._check_has_single_scope(sig)
        assert cls._check_no_typevar_overlap(sig)
        assert cls._check_no_boundvars_in_result(sig)

        root_ordinal = cls._get_root_ordinal(sig)
        if not root_ordinal:
            root_ordinal = cls._get_fresh_ordinal()

        # add missing Scoped annotations and join everything with the root scope
        new_annos: list[type | typing._SpecialForm] = []
        for anno in (
            sig.return_annotation,
            *(p.annotation for p in sig.parameters.values()),
        ):
            new_scope = cls(ordinal=cls._get_param_ordinal(anno) | root_ordinal)
            if typing.get_origin(anno) is Annotated:
                new_anno = typing.get_args(anno)[0]
                new_anno = Annotated[new_anno, new_scope]
                for other in typing.get_args(anno)[1:]:
                    if not isinstance(other, cls):
                        new_anno = Annotated[new_anno, other]
            else:
                new_anno = Annotated[anno, new_scope]

            new_annos.append(new_anno)

        # construct a new Signature structure with the inferred annotations
        new_return_anno, new_annos = new_annos[0], new_annos[1:]
        inferred_sig = sig.replace(
            parameters=[
                p.replace(annotation=a)
                for p, a in zip(sig.parameters.values(), new_annos)
            ],
            return_annotation=new_return_anno,
        )

        # post-conditions
        assert cls._get_root_ordinal(inferred_sig) == root_ordinal != set()
        return inferred_sig

    def analyze(self, bound_sig: inspect.BoundArguments) -> frozenset[Operation]:
        """
        Computes a set of bound variables given a signature with bound arguments.

        The :func:`analyze` methods of :class:`Scoped` annotations that appear on
        the signature of an :class:`Operation` are used by :func:`defop` to generate
        implementations of :func:`Operation.__fvs_rule__` underlying alpha-renaming
        in :func:`defterm` and :func:`defdata` and free variable sets in :func:`fvsof` .

        Specifically, the :func:`analyze` method of the :class:`Scoped` annotation
        of a parameter computes the set of bound variables in that parameter's value.
        The :func:`Operation.__fvs_rule__` method generated by :func:`defop` simply
        extracts the annotation of each parameter, calls :func:`analyze` on the value
        given for the corresponding parameter in ``bound_sig`` , and returns the results.

        :param bound_sig: The :class:`inspect.Signature` of an :class:`Operation`
            together with values for all of its arguments.
        :returns: A set of bound variables.
        """
        bound_vars: frozenset[Operation] = frozenset()
        return_ordinal = self._get_param_ordinal(bound_sig.signature.return_annotation)
        for name, param in bound_sig.signature.parameters.items():
            param_ordinal = self._get_param_ordinal(param)
            if param_ordinal <= self.ordinal and not param_ordinal <= return_ordinal:
                param_value = bound_sig.arguments[name]
                param_bound_vars = set()

                if self._param_is_var(param):
                    # Handle individual Operation parameters (existing behavior)
                    if param.kind is inspect.Parameter.VAR_POSITIONAL:
                        # pre-condition: all bound variables should be distinct
                        assert len(param_value) == len(set(param_value))
                        param_bound_vars = set(param_value)
                    elif param.kind is inspect.Parameter.VAR_KEYWORD:
                        # pre-condition: all bound variables should be distinct
                        assert len(param_value.values()) == len(
                            set(param_value.values())
                        )
                        param_bound_vars = set(param_value.values())
                    else:
                        param_bound_vars = {param_value}
                elif param_ordinal:  # Only process if there's a Scoped annotation
                    # We can't use flatten here because we want to be able
                    # to see dict keys
                    def extract_operations(obj):
                        if isinstance(obj, Operation):
                            param_bound_vars.add(obj)
                        elif isinstance(obj, dict):
                            for k, v in obj.items():
                                extract_operations(k)
                                extract_operations(v)
                        elif isinstance(obj, list | set | tuple):
                            for v in obj:
                                extract_operations(v)

                    extract_operations(param_value)

                # pre-condition: all bound variables should be distinct
                if param_bound_vars:
                    assert not bound_vars & param_bound_vars
                    bound_vars |= param_bound_vars

        return bound_vars


@functools.singledispatch
def defop[**P, T](
    t: Callable[P, T], *, name: str | None = None, freshening=list[int] | None
) -> Operation[P, T]:
    """Creates a fresh :class:`Operation`.

    :param t: May be a type, callable, or :class:`Operation`. If a type, the
              operation will have no arguments and return the type. If a callable,
              the operation will have the same signature as the callable, but with
              no default rule. If an operation, the operation will be a distinct
              copy of the operation.
    :param name: Optional name for the operation.
    :returns: A fresh operation.

    .. note::

      The result of :func:`defop` is always fresh (i.e. ``defop(f) != defop(f)``).

    **Example usage**:

    * Defining an operation:

      This example defines an operation that selects one of two integers:

      >>> @defop
      ... def select(x: int, y: int) -> int:
      ...     return x

      The operation can be called like a regular function. By default, ``select``
      returns the first argument:

      >>> select(1, 2)
      1

      We can change its behavior by installing a ``select`` handler:

      >>> from effectful.ops.semantics import handler
      >>> with handler({select: lambda x, y: y}):
      ...     print(select(1, 2))
      2

    * Defining an operation with no default rule:

      We can use :func:`defop` and the
      :exc:`NotHandled` exception to define an
      operation with no default rule:

      >>> @defop
      ... def add(x: int, y: int) -> int:
      ...     raise NotHandled
      >>> print(str(add(1, 2)))
      add(1, 2)

      When an operation has no default rule, the free rule is used instead, which
      constructs a term of the operation applied to its arguments. This feature
      can be used to conveniently define the syntax of a domain-specific language.

    * Defining free variables:

      Passing :func:`defop` a type is a handy way to create a free variable.

      >>> from effectful.ops.semantics import evaluate
      >>> x = defop(int, name='x')
      >>> y = x() + 1

      ``y`` is free in ``x``, so it is not fully evaluated:

      >>> print(str(y))
      __add__(x(), 1)

      We bind ``x`` by installing a handler for it:

      >>> with handler({x: lambda: 2}):
      ...     print(evaluate(y))
      3

      .. note::

        Because the result of :func:`defop` is always fresh, it's important to
        be careful with variable identity.

        Two operations with the same name that come from different calls to
        ``defop`` are not equal:

        >>> x1 = defop(int, name='x')
        >>> x2 = defop(int, name='x')
        >>> x1 == x2
        False

        This means that to correctly bind a variable, you must use the same
        operation object. In this example, ``scale`` returns a term with a free
        variable ``x``:

        >>> x = defop(float, name='x')
        >>> def scale(a: float) -> float:
        ...     return x() * a

        Binding the variable ``x`` as follows does not work:

        >>> term = scale(3.0)
        >>> fresh_x = defop(float, name='x')
        >>> with handler({fresh_x: lambda: 2.0}):
        ...     print(str(evaluate(term)))
        __mul__(x(), 3.0)

        Only the original operation object will work:

        >>> from effectful.ops.semantics import fvsof
        >>> with handler({x: lambda: 2.0}):
        ...     print(evaluate(term))
        6.0

    * Defining a fresh :class:`Operation`:

      Passing :func:`defop` an :class:`Operation` creates a fresh operation with
      the same name and signature, but no default rule.

      >>> fresh_select = defop(select)
      >>> print(str(fresh_select(1, 2)))
      select(1, 2)

      The new operation is distinct from the original:

      >>> with handler({select: lambda x, y: y}):
      ...     print(select(1, 2), fresh_select(1, 2))
      2 select(1, 2)

      >>> with handler({fresh_select: lambda x, y: y}):
      ...     print(select(1, 2), fresh_select(1, 2))
      1 2

    """
    raise NotImplementedError(f"expected type or callable, got {t}")


@defop.register(typing.cast(type[collections.abc.Callable], collections.abc.Callable))
class _BaseOperation[**Q, V](Operation[Q, V]):
    __signature__: inspect.Signature
    __name__: str

    _default: Callable[Q, V]

    def __init__(
        self,
        default: Callable[Q, V],
        *,
        name: str | None = None,
        freshening: list[int] | None = None,
    ):
        functools.update_wrapper(self, default)
        self._default = default
        self.__name__ = name or default.__name__
        self._freshening = freshening or []
        self.__signature__ = inspect.signature(default)

    def __eq__(self, other):
        if not isinstance(other, Operation):
            return NotImplemented
        return self is other

    def __lt__(self, other):
        if not isinstance(other, Operation):
            return NotImplemented
        return id(self) < id(other)

    def __hash__(self):
        return hash(self._default)

    def __default_rule__(self, *args: Q.args, **kwargs: Q.kwargs) -> "Expr[V]":
        try:
            try:
                return self._default(*args, **kwargs)
            except NotImplementedError:
                warnings.warn(
                    "Operations should raise effectful.ops.types.NotHandled instead of NotImplementedError.",
                    DeprecationWarning,
                )
                raise NotHandled
        except NotHandled:
            return typing.cast(
                Callable[Concatenate[Operation[Q, V], Q], Expr[V]], defdata
            )(self, *args, **kwargs)

    def __fvs_rule__(self, *args: Q.args, **kwargs: Q.kwargs) -> inspect.BoundArguments:
        sig = Scoped.infer_annotations(self.__signature__)
        bound_sig = sig.bind(*args, **kwargs)
        bound_sig.apply_defaults()

        result_sig = sig.bind(
            *(frozenset() for _ in bound_sig.args),
            **{k: frozenset() for k in bound_sig.kwargs},
        )
        for name, param in sig.parameters.items():
            if typing.get_origin(param.annotation) is typing.Annotated:
                for anno in typing.get_args(param.annotation)[1:]:
                    if isinstance(anno, Scoped):
                        param_bound_vars = anno.analyze(bound_sig)
                        if param.kind is inspect.Parameter.VAR_POSITIONAL:
                            result_sig.arguments[name] = tuple(
                                param_bound_vars for _ in bound_sig.arguments[name]
                            )
                        elif param.kind is inspect.Parameter.VAR_KEYWORD:
                            for k in bound_sig.arguments[name]:
                                result_sig.arguments[name][k] = param_bound_vars
                        else:
                            result_sig.arguments[name] = param_bound_vars

        return result_sig

    def __type_rule__(self, *args: Q.args, **kwargs: Q.kwargs) -> type[V]:
        from effectful.internals.unification import (
            freetypevars,
            nested_type,
            substitute,
            unify,
        )

        return_anno = self.__signature__.return_annotation
        if typing.get_origin(return_anno) is typing.Annotated:
            return_anno = typing.get_args(return_anno)[0]

        if return_anno is inspect.Parameter.empty:
            return typing.cast(type[V], object)
        elif return_anno is None:
            return type(None)  # type: ignore
        elif not freetypevars(return_anno):
            return return_anno

        type_args = tuple(nested_type(a) for a in args)
        type_kwargs = {k: nested_type(v) for k, v in kwargs.items()}
        bound_sig = self.__signature__.bind(*type_args, **type_kwargs)
        return substitute(return_anno, unify(self.__signature__, bound_sig))  # type: ignore

    def __repr__(self):
        return f"_BaseOperation({self._default}, name={self.__name__}, freshening={self._freshening})"

    def __str__(self):
        return self.__name__

    def __get__(self, instance, owner):
        if instance is not None:
            # This is an instance-level operation, so we need to bind the instance
            return functools.partial(self, instance)
        else:
            # This is a static operation, so we return the operation itself
            return self


@defop.register(Operation)
def _[**P, T](t: Operation[P, T], *, name: str | None = None) -> Operation[P, T]:
    @functools.wraps(t)
    def func(*args, **kwargs):
        raise NotHandled

    if name is None:
        name = getattr(t, "__name__", str(t))
    freshening = getattr(t, "_freshening", []) + [random.randint(0, 1 << 32)]

    return defop(func, name=name, freshening=freshening)


@defop.register(type)
@defop.register(typing.cast(type, types.GenericAlias))
@defop.register(typing.cast(type, typing._GenericAlias))  # type: ignore
@defop.register(typing.cast(type, types.UnionType))
def _[T](t: type[T], *, name: str | None = None) -> Operation[[], T]:
    def func() -> t:  # type: ignore
        raise NotHandled

    freshening = []
    if name is None:
        name = t.__name__
        freshening = [random.randint(0, 1 << 32)]

    return typing.cast(
        Operation[[], T],
        defop(func, name=name, freshening=freshening),
    )


@defop.register(types.BuiltinFunctionType)
def _[**P, T](t: Callable[P, T], *, name: str | None = None) -> Operation[P, T]:
    @functools.wraps(t)
    def func(*args, **kwargs):
        from effectful.ops.semantics import fvsof

        if not fvsof((args, kwargs)):
            return t(*args, **kwargs)
        else:
            raise NotHandled

    return defop(func, name=name)


@defop.register(classmethod)
def _[**P, S, T](  # type: ignore
    t: classmethod, *, name: str | None = None
) -> Operation[Concatenate[type[S], P], T]:
    raise NotImplementedError("classmethod operations are not yet supported")


@defop.register(staticmethod)
class _StaticMethodOperation[**P, S, T](_BaseOperation[P, T]):
    def __init__(self, default: staticmethod, **kwargs):
        super().__init__(default=default.__func__, **kwargs)

    def __get__(self, instance: S, owner: type[S] | None = None) -> Callable[P, T]:
        return self


@defop.register(property)
class _PropertyOperation[S, T](_BaseOperation[[S], T]):
    def __init__(self, default: property, **kwargs):  # type: ignore
        assert not default.fset, "property with setter is not supported"
        assert not default.fdel, "property with deleter is not supported"
        super().__init__(default=typing.cast(Callable[[S], T], default.fget), **kwargs)

    @typing.overload
    def __get__(
        self, instance: None, owner: type[S] | None = None
    ) -> "_PropertyOperation[S, T]": ...

    @typing.overload
    def __get__(self, instance: S, owner: type[S] | None = None) -> T: ...

    def __get__(self, instance, owner: type[S] | None = None):
        if instance is not None:
            return self(instance)
        else:
            return self


@defop.register(functools.singledispatchmethod)
class _SingleDispatchMethodOperation[**P, S, T](_BaseOperation[Concatenate[S, P], T]):
    _default: Callable[Concatenate[S, P], T]

    def __init__(self, default: functools.singledispatchmethod, **kwargs):  # type: ignore
        if isinstance(default.func, classmethod):
            raise NotImplementedError("Operations as classmethod are not yet supported")

        @functools.wraps(default.func)
        def _wrapper(obj: S, *args: P.args, **kwargs: P.kwargs) -> T:
            return default.__get__(obj)(*args, **kwargs)

        self._registry: functools.singledispatchmethod = default
        super().__init__(_wrapper, **kwargs)

    @typing.overload
    def __get__(
        self, instance: None, owner: type[S] | None = None
    ) -> "_SingleDispatchMethodOperation[P, S, T]": ...

    @typing.overload
    def __get__(self, instance: S, owner: type[S] | None = None) -> Callable[P, T]: ...

    def __get__(self, instance, owner: type[S] | None = None):
        if instance is not None:
            return functools.partial(self, instance)
        else:
            return self

    @property
    def register(self):
        return self._registry.register

    @property
    def __isabstractmethod__(self):
        return self._registry.__isabstractmethod__


class _SingleDispatchOperation[**P, S, T](_BaseOperation[Concatenate[S, P], T]):
    _default: "functools._SingleDispatchCallable[T]"

    @property
    def register(self):
        return self._default.register

    @property
    def dispatch(self):
        return self._default.dispatch


if typing.TYPE_CHECKING:
    defop.register(functools._SingleDispatchCallable)(_SingleDispatchOperation)
else:

    @typing.runtime_checkable
    class _SingleDispatchCallable(typing.Protocol):
        registry: types.MappingProxyType[object, Callable]

        def dispatch(self, cls: type) -> Callable: ...
        def register(self, cls: type, func: Callable | None = None) -> Callable: ...
        def _clear_cache(self) -> None: ...
        def __call__(self, /, *args, **kwargs): ...

    defop.register(_SingleDispatchCallable)(_SingleDispatchOperation)


@defop
def deffn[T, A, B](
    body: Annotated[T, Scoped[A | B]],
    *args: Annotated[Operation, Scoped[A]],
    **kwargs: Annotated[Operation, Scoped[A]],
) -> Annotated[Callable[..., T], Scoped[B]]:
    """An operation that represents a lambda function.

    :param body: The body of the function.
    :param args: Operations representing the positional arguments of the function.
    :param kwargs: Operations representing the keyword arguments of the function.
    :returns: A callable term.

    :func:`deffn` terms are eliminated by the :func:`call` operation, which
    performs beta-reduction.

    **Example usage**:

    Here :func:`deffn` is used to define a term that represents the function
    ``lambda x, y=1: 2 * x + y``:

    >>> import random
    >>> random.seed(0)

    >>> x, y = defop(int, name='x'), defop(int, name='y')
    >>> term = deffn(2 * x() + y(), x, y=y)
    >>> print(str(term))  # doctest: +ELLIPSIS
    deffn(...)
    >>> term(3, y=4)
    10

    .. note::

      In general, avoid using :func:`deffn` directly. Instead, use
      :func:`defterm` to convert a function to a term because it will
      automatically create the right free variables.

    """
    raise NotHandled


class _CustomSingleDispatchCallable[**P, **Q, S, T]:
    def __init__(
        self, func: Callable[Concatenate[Callable[[type], Callable[Q, S]], P], T]
    ):
        self.func = func
        self._registry = functools.singledispatch(func)
        functools.update_wrapper(self, func)

    @property
    def dispatch(self):
        return self._registry.dispatch

    @property
    def register(self):
        return self._registry.register

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(self.dispatch, *args, **kwargs)


@defop.register(_CustomSingleDispatchCallable)
class _CustomSingleDispatchOperation[**P, **Q, S, T](_BaseOperation[P, T]):
    _default: _CustomSingleDispatchCallable[P, Q, S, T]

    def __init__(self, default: _CustomSingleDispatchCallable[P, Q, S, T], **kwargs):
        super().__init__(default, **kwargs)
        self.__signature__ = inspect.signature(functools.partial(default.func, None))  # type: ignore

    @property
    def dispatch(self):
        return self._registry.dispatch

    @property
    def register(self):
        return self._registry.register


@_CustomSingleDispatchCallable
def defterm[T](__dispatch: Callable[[type], Callable[[T], Expr[T]]], value: T):
    """Convert a value to a term, using the type of the value to dispatch.

    :param value: The value to convert.
    :returns: A term.
    """
    if isinstance(value, Term):
        return value
    else:
        return __dispatch(type(value))(value)


@_CustomSingleDispatchCallable
def defdata[T](
    __dispatch: Callable[[type], Callable[..., Expr[T]]],
    op: Operation[..., T],
    *args,
    **kwargs,
) -> Expr[T]:
    """Constructs a Term that is an instance of its semantic type.

    :returns: An instance of ``T``.
    :rtype: Expr[T]

    This function is the only way to construct a :class:`Term` from an :class:`Operation`.

    .. note::

      This function is not likely to be called by users of the effectful
      library, but they may wish to register implementations for additional
      types.

    **Example usage**:

    This is how callable terms are implemented:

    .. code-block:: python

      @defdata.register(collections.abc.Callable)
      class _CallableTerm[**P, T](Term[collections.abc.Callable[P, T]]):
          def __init__(
              self,
              op: Operation[..., T],
              *args: Expr,
              **kwargs: Expr,
          ):
              self._op = op
              self._args = args
              self._kwargs = kwargs

          @property
          def op(self):
              return self._op

          @property
          def args(self):
              return self._args

          @property
          def kwargs(self):
              return self._kwargs

          @defop
          def __call__(self: collections.abc.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
              ...

    When an Operation whose return type is `Callable` is passed to :func:`defdata`,
    it is reconstructed as a :class:`_CallableTerm`, which implements the :func:`__call__` method.
    """
    from effectful.internals.product_n import _unpack, productN
    from effectful.internals.runtime import interpreter
    from effectful.ops.semantics import _simple_type, apply, evaluate

    # If this operation binds variables, we need to rename them in the
    # appropriate parts of the child term.
    bindings: inspect.BoundArguments = op.__fvs_rule__(*args, **kwargs)
    renaming = {
        var: defop(var)
        for bound_vars in (*bindings.args, *bindings.kwargs.values())
        for var in bound_vars
    }

    # Analysis for type computation and term reconstruction
    typ = defop(object, name="typ")
    cast = defop(object, name="cast")

    def apply_type(op, *args, **kwargs):
        assert isinstance(op, Operation)
        tp = op.__type_rule__(*args, **kwargs)
        return tp

    def apply_cast(op, *args, **kwargs):
        assert isinstance(op, Operation)
        full_type = typ()
        dispatch_type = _simple_type(full_type)
        return __dispatch(dispatch_type)(op, *args, **kwargs)

    analysis = productN({typ: {apply: apply_type}, cast: {apply: apply_cast}})

    def evaluate_with_renaming(expr, ctx):
        """Evaluate an expression with renaming applied."""
        renaming_ctx = {
            old_var: new_var for old_var, new_var in renaming.items() if old_var in ctx
        }

        # Note: coproduct cannot be used to compose these interpretations
        # because evaluate will only do operation replacement when the handler
        # is operation typed, which coproduct does not satisfy.
        with interpreter(analysis | renaming_ctx):
            result = evaluate(expr)

        return result

    renamed_args = op.__signature__.bind(*args, **kwargs)
    renamed_args.apply_defaults()

    args_ = [
        evaluate_with_renaming(arg, bindings.args[i])
        for (i, arg) in enumerate(renamed_args.args)
    ]
    kwargs_ = {
        k: evaluate_with_renaming(v, bindings.kwargs[k])
        for (k, v) in renamed_args.kwargs.items()
    }

    # Build the final term with type analysis
    with interpreter(analysis):
        result = op(*args_, **kwargs_)

    return _unpack(result, cast)


@defterm.register(object)
@defterm.register(Operation)
@defterm.register(Term)
@defterm.register(type)
@defterm.register(types.BuiltinFunctionType)
def _[T](value: T) -> T:
    return value


@defdata.register(object)
class _BaseTerm[T](Term[T]):
    _op: Operation[..., T]
    _args: collections.abc.Sequence[Expr]
    _kwargs: collections.abc.Mapping[str, Expr]

    def __init__(
        self,
        op: Operation[..., T],
        *args: Expr,
        **kwargs: Expr,
    ):
        self._op = op
        self._args = args
        self._kwargs = kwargs

    def __eq__(self, other) -> bool:
        from effectful.ops.syntax import syntactic_eq

        return syntactic_eq(self, other)

    @property
    def op(self):
        return self._op

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs


@defdata.register(collections.abc.Callable)
class _CallableTerm[**P, T](_BaseTerm[collections.abc.Callable[P, T]]):
    @defop
    def __call__(
        self: collections.abc.Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        from effectful.ops.semantics import evaluate, fvsof, handler

        if isinstance(self, Term) and self.op is deffn:
            body: Expr[Callable[P, T]] = self.args[0]
            argvars: tuple[Operation, ...] = self.args[1:]
            kwvars: dict[str, Operation] = self.kwargs
            subs = {
                **{v: functools.partial(lambda x: x, a) for v, a in zip(argvars, args)},
                **{
                    kwvars[k]: functools.partial(lambda x: x, kwargs[k]) for k in kwargs
                },
            }
            with handler(subs):
                return evaluate(body)
        elif not fvsof((self, args, kwargs)):
            return self(*args, **kwargs)
        else:
            raise NotHandled


def trace[**P, T](value: Callable[P, T]) -> Callable[P, T]:
    """Convert a callable to a term by calling it with appropriately typed free variables.

    **Example usage**:

    :func:`trace` can be passed a function, and it will convert that function to
    a term by calling it with appropriately typed free variables:

    >>> def incr(x: int) -> int:
    ...     return x + 1
    >>> term = trace(incr)

    >>> print(str(term))
    deffn(__add__(int(), 1), int)

    >>> term(2)
    3

    """
    from effectful.internals.runtime import interpreter
    from effectful.ops.semantics import apply

    call = defdata.dispatch(collections.abc.Callable).__call__
    assert isinstance(call, Operation)

    assert not isinstance(value, Term)

    try:
        sig = inspect.signature(value)
    except ValueError:
        return value

    for name, param in sig.parameters.items():
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            raise ValueError(f"cannot unembed {value}: parameter {name} is variadic")

    bound_sig = sig.bind(
        **{name: defop(param.annotation) for name, param in sig.parameters.items()}
    )
    bound_sig.apply_defaults()

    with interpreter({apply: defdata, call: call.__default_rule__}):
        body = value(
            *[a() for a in bound_sig.args],
            **{k: v() for k, v in bound_sig.kwargs.items()},
        )

    return deffn(body, *bound_sig.args, **bound_sig.kwargs)


@defop
def defstream[S, T, A, B](
    body: Annotated[T, Scoped[A | B]],
    streams: Annotated[Mapping[Operation[[], S], Iterable[S]], Scoped[B]],
) -> Annotated[Iterable[T], Scoped[A]]:
    """A higher-order operation that represents a for-expression."""
    raise NotHandled


@defdata.register(collections.abc.Iterable)
class _IterableTerm[T](_BaseTerm[collections.abc.Iterable[T]]):
    @defop
    def __iter__(self: collections.abc.Iterable[T]) -> collections.abc.Iterator[T]:
        if not isinstance(self, Term):
            return iter(self)
        else:
            raise NotHandled


@defdata.register(collections.abc.Iterator)
class _IteratorTerm[T](_IterableTerm[T]):
    @defop
    def __next__(self: collections.abc.Iterator[T]) -> T:
        if not isinstance(self, Term):
            return next(self)
        else:
            raise NotHandled


iter_ = _IterableTerm.__iter__
next_ = _IteratorTerm.__next__


@_CustomSingleDispatchCallable
def syntactic_eq(
    __dispatch: Callable[[type], Callable[[Any, Any], bool]], x, other
) -> bool:
    """Syntactic equality, ignoring the interpretation of the terms.

    :param x: A term.
    :param other: Another term.
    :returns: ``True`` if the terms are syntactically equal and ``False`` otherwise.
    """
    if (
        dataclasses.is_dataclass(x)
        and not isinstance(x, type)
        and dataclasses.is_dataclass(other)
        and not isinstance(other, type)
    ):
        return type(x) == type(other) and syntactic_eq(
            {field.name: getattr(x, field.name) for field in dataclasses.fields(x)},
            {
                field.name: getattr(other, field.name)
                for field in dataclasses.fields(other)
            },
        )
    else:
        return __dispatch(type(x))(x, other)


@syntactic_eq.register
def _(x: Term, other) -> bool:
    if not isinstance(other, Term):
        return False

    op, args, kwargs = x.op, x.args, x.kwargs
    op2, args2, kwargs2 = other.op, other.args, other.kwargs
    return (
        op == op2
        and len(args) == len(args2)
        and set(kwargs) == set(kwargs2)
        and all(syntactic_eq(a, b) for a, b in zip(args, args2))
        and all(syntactic_eq(kwargs[k], kwargs2[k]) for k in kwargs)
    )


@syntactic_eq.register
def _(x: collections.abc.Mapping, other) -> bool:
    return isinstance(other, collections.abc.Mapping) and all(
        k in x and k in other and syntactic_eq(x[k], other[k])
        for k in set(x) | set(other)
    )


@syntactic_eq.register
def _(x: collections.abc.Sequence, other) -> bool:
    if (
        isinstance(x, tuple)
        and hasattr(x, "_fields")
        and all(hasattr(x, f) for f in x._fields)
    ):
        return type(other) == type(x) and all(
            syntactic_eq(getattr(x, f), getattr(other, f)) for f in x._fields
        )
    else:
        return (
            isinstance(other, collections.abc.Sequence)
            and len(x) == len(other)
            and all(syntactic_eq(a, b) for a, b in zip(x, other))
        )


@syntactic_eq.register(object)
@syntactic_eq.register(str | bytes)
def _(x: object, other) -> bool:
    return x == other


class ObjectInterpretation[T, V](collections.abc.Mapping):
    """A helper superclass for defining an ``Interpretation`` of many
    :class:`~effectful.ops.types.Operation` instances with shared state or behavior.

    You can mark specific methods in the definition of an
    :class:`ObjectInterpretation` with operations using the :func:`implements`
    decorator. The :class:`ObjectInterpretation` object itself is an
    ``Interpretation`` (mapping from :class:`~effectful.ops.types.Operation` to :class:`~typing.Callable`)

    >>> from effectful.ops.semantics import handler
    >>> @defop
    ... def read_box():
    ...     pass
    ...
    >>> @defop
    ... def write_box(new_value):
    ...     pass
    ...
    >>> class StatefulBox(ObjectInterpretation):
    ...     def __init__(self, init=None):
    ...         super().__init__()
    ...         self.stored = init
    ...     @implements(read_box)
    ...     def whatever(self):
    ...         return self.stored
    ...     @implements(write_box)
    ...     def write_box(self, new_value):
    ...         self.stored = new_value
    ...
    >>> first_box = StatefulBox(init="First Starting Value")
    >>> second_box = StatefulBox(init="Second Starting Value")
    >>> with handler(first_box):
    ...     print(read_box())
    ...     write_box("New Value")
    ...     print(read_box())
    ...
    First Starting Value
    New Value
    >>> with handler(second_box):
    ...     print(read_box())
    Second Starting Value
    >>> with handler(first_box):
    ...     print(read_box())
    New Value

    """

    # This is a weird hack to get around the fact that
    # the default meta-class runs __set_name__ before __init__subclass__.
    # We basically store the implementations here temporarily
    # until __init__subclass__ is called.
    # This dict is shared by all `Implementation`s,
    # so we need to clear it when we're done.
    _temporary_implementations: dict[Operation[..., T], Callable[..., V]] = dict()
    implementations: dict[Operation[..., T], Callable[..., V]] = dict()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.implementations = ObjectInterpretation._temporary_implementations.copy()

        for sup in cls.mro():
            if issubclass(sup, ObjectInterpretation):
                cls.implementations = {**sup.implementations, **cls.implementations}

        ObjectInterpretation._temporary_implementations.clear()

    def __iter__(self):
        return iter(self.implementations)

    def __len__(self):
        return len(self.implementations)

    def __getitem__(self, item: Operation[..., T]) -> Callable[..., V]:
        return self.implementations[item].__get__(self, type(self))


class _ImplementedOperation[**P, **Q, T, V]:
    impl: Callable[Q, V] | None
    op: Operation[P, T]

    def __init__(self, op: Operation[P, T]):
        self.op = op
        self.impl = None

    def __get__(
        self, instance: ObjectInterpretation[T, V], owner: type
    ) -> Callable[..., V]:
        assert self.impl is not None

        return self.impl.__get__(instance, owner)

    def __call__(self, impl: Callable[Q, V]):
        self.impl = impl
        return self

    def __set_name__(self, owner: ObjectInterpretation[T, V], name):
        assert self.impl is not None
        assert self.op is not None
        owner._temporary_implementations[self.op] = self.impl


def implements[**P, V](op: Operation[P, V]):
    """Marks a method in an :class:`ObjectInterpretation` as the implementation of a
    particular abstract :class:`Operation`.

    When passed an :class:`Operation`, returns a method decorator which installs
    the given method as the implementation of the given :class:`Operation`.

    """
    return _ImplementedOperation(op)


@defdata.register(numbers.Number)
@functools.total_ordering
class _NumberTerm[T: numbers.Number](_BaseTerm[T], numbers.Number):
    def __hash__(self):
        return id(self)

    def __complex__(self) -> complex:
        raise ValueError("Cannot convert term to complex number")

    def __float__(self) -> float:
        raise ValueError("Cannot convert term to float")

    def __int__(self) -> int:
        raise ValueError("Cannot convert term to int")

    def __bool__(self) -> bool:
        raise ValueError("Cannot convert term to bool")

    @defop  # type: ignore[prop-decorator]
    @property
    def real(self) -> float:
        if not isinstance(self, Term):
            return self.real
        else:
            raise NotHandled

    @defop  # type: ignore[prop-decorator]
    @property
    def imag(self) -> float:
        if not isinstance(self, Term):
            return self.imag
        else:
            raise NotHandled

    @defop
    def conjugate(self) -> complex:
        if not isinstance(self, Term):
            return self.conjugate()
        else:
            raise NotHandled

    @defop  # type: ignore[prop-decorator]
    @property
    def numerator(self) -> int:
        if not isinstance(self, Term):
            return self.numerator
        else:
            raise NotHandled

    @defop  # type: ignore[prop-decorator]
    @property
    def denominator(self) -> int:
        if not isinstance(self, Term):
            return self.denominator
        else:
            raise NotHandled

    @defop
    def __abs__(self) -> float:
        """Return the absolute value of the term."""
        if not isinstance(self, Term):
            return self.__abs__()
        else:
            raise NotHandled

    @defop
    def __neg__(self: T) -> T:
        if not isinstance(self, Term):
            return self.__neg__()  # type: ignore
        else:
            raise NotHandled

    @defop
    def __pos__(self: T) -> T:
        if not isinstance(self, Term):
            return self.__pos__()  # type: ignore
        else:
            raise NotHandled

    @defop
    def __trunc__(self) -> int:
        if not isinstance(self, Term):
            return self.__trunc__()
        else:
            raise NotHandled

    @defop
    def __floor__(self) -> int:
        if not isinstance(self, Term):
            return self.__floor__()
        else:
            raise NotHandled

    @defop
    def __ceil__(self) -> int:
        if not isinstance(self, Term):
            return self.__ceil__()
        else:
            raise NotHandled

    @defop
    def __round__(self, ndigits: int | None = None) -> numbers.Real:
        if not isinstance(self, Term) and not isinstance(ndigits, Term):
            return self.__round__(ndigits)
        else:
            raise NotHandled

    @defop
    def __invert__(self) -> int:
        if not isinstance(self, Term):
            return self.__invert__()
        else:
            raise NotHandled

    @defop
    def __index__(self) -> int:
        if not isinstance(self, Term):
            return self.__index__()
        else:
            raise NotHandled

    @defop
    def __eq__(self, other) -> bool:  # type: ignore[override]
        if not isinstance(self, Term) and not isinstance(other, Term):
            return self.__eq__(other)
        else:
            return syntactic_eq(self, other)

    @defop
    def __lt__(self, other) -> bool:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return self.__lt__(other)
        else:
            raise NotHandled

    @defop
    def __add__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__add__(self, other)
        else:
            raise NotHandled

    def __radd__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__add__(self)
        elif not isinstance(other, Term):
            return type(self).__add__(other, self)
        else:
            return NotImplemented

    @defop
    def __sub__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__sub__(self, other)
        else:
            raise NotHandled

    def __rsub__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__sub__(self)
        elif not isinstance(other, Term):
            return type(self).__sub__(other, self)
        else:
            return NotImplemented

    @defop
    def __mul__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__mul__(self, other)
        else:
            raise NotHandled

    def __rmul__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__mul__(self)
        elif not isinstance(other, Term):
            return type(self).__mul__(other, self)
        else:
            return NotImplemented

    @defop
    def __truediv__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__truediv__(self, other)
        else:
            raise NotHandled

    def __rtruediv__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__truediv__(self)
        elif not isinstance(other, Term):
            return type(self).__truediv__(other, self)
        else:
            return NotImplemented

    @defop
    def __floordiv__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__floordiv__(self, other)
        else:
            raise NotHandled

    def __rfloordiv__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__floordiv__(self)
        elif not isinstance(other, Term):
            return type(self).__floordiv__(other, self)
        else:
            return NotImplemented

    @defop
    def __mod__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__mod__(self, other)
        else:
            raise NotHandled

    def __rmod__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__mod__(self)
        elif not isinstance(other, Term):
            return type(self).__mod__(other, self)
        else:
            return NotImplemented

    @defop
    def __pow__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__pow__(self, other)
        else:
            raise NotHandled

    def __rpow__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__pow__(self)
        elif not isinstance(other, Term):
            return type(self).__pow__(other, self)
        else:
            return NotImplemented

    @defop
    def __lshift__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__lshift__(self, other)
        else:
            raise NotHandled

    def __rlshift__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__lshift__(self)
        elif not isinstance(other, Term):
            return type(self).__lshift__(other, self)
        else:
            return NotImplemented

    @defop
    def __rshift__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__rshift__(self, other)
        else:
            raise NotHandled

    def __rrshift__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__rshift__(self)
        elif not isinstance(other, Term):
            return type(self).__rshift__(other, self)
        else:
            return NotImplemented

    @defop
    def __and__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__and__(self, other)
        else:
            raise NotHandled

    def __rand__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__and__(self)
        elif not isinstance(other, Term):
            return type(self).__and__(other, self)
        else:
            return NotImplemented

    @defop
    def __xor__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__xor__(self, other)
        else:
            raise NotHandled

    def __rxor__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__xor__(self)
        elif not isinstance(other, Term):
            return type(self).__xor__(other, self)
        else:
            return NotImplemented

    @defop
    def __or__(self, other: T) -> T:
        if not isinstance(self, Term) and not isinstance(other, Term):
            return operator.__or__(self, other)
        else:
            raise NotHandled

    def __ror__(self, other):
        if isinstance(other, Term) and isinstance(other, type(self)):
            return other.__or__(self)
        elif not isinstance(other, Term):
            return type(self).__or__(other, self)
        else:
            return NotImplemented


@defdata.register(numbers.Complex)
@numbers.Complex.register
class _ComplexTerm[T: numbers.Complex](_NumberTerm[T]):
    pass


@defdata.register(numbers.Real)
@numbers.Real.register
class _RealTerm[T: numbers.Real](_ComplexTerm[T]):
    pass


@defdata.register(numbers.Rational)
@numbers.Rational.register
class _RationalTerm[T: numbers.Rational](_RealTerm[T]):
    pass


@defdata.register(numbers.Integral)
@numbers.Integral.register
class _IntegralTerm[T: numbers.Integral](_RationalTerm[T]):
    pass


@defdata.register(bool)
class _BoolTerm[T: bool](_IntegralTerm[T]):  # type: ignore
    pass
