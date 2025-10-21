import contextlib
import dataclasses
import functools
from collections.abc import Callable, Mapping

from effectful.ops.syntax import defop
from effectful.ops.types import Interpretation, Operation


@dataclasses.dataclass
class Runtime[S, T]:
    interpretation: "Interpretation[S, T]"


@functools.lru_cache(maxsize=1)
def get_runtime() -> Runtime:
    return Runtime(interpretation={})


def get_interpretation():
    return get_runtime().interpretation


@contextlib.contextmanager
def interpreter(intp: "Interpretation"):
    r = get_runtime()
    old_intp = r.interpretation
    try:
        old_intp, r.interpretation = r.interpretation, dict(intp)
        yield intp
    finally:
        r.interpretation = old_intp


@defop
def _get_args() -> tuple[tuple, Mapping]:
    return ((), {})


def _restore_args[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(fn)
    def _cont_wrapper(*a: P.args, **k: P.kwargs) -> T:
        a, k = (a, k) if a or k else _get_args()  # type: ignore
        return fn(*a, **k)

    return _cont_wrapper


def _save_args[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
    from effectful.ops.semantics import handler

    @functools.wraps(fn)
    def _cont_wrapper(*a: P.args, **k: P.kwargs) -> T:
        with handler({_get_args: lambda: (a, k)}):
            return fn(*a, **k)

    return _cont_wrapper


def _set_prompt[**P, T](
    prompt: Operation[P, T], cont: Callable[P, T], body: Callable[P, T]
) -> Callable[P, T]:
    from effectful.ops.semantics import handler

    @functools.wraps(body)
    def bound_body(*a: P.args, **k: P.kwargs) -> T:
        next_cont = get_interpretation().get(prompt, prompt.__default_rule__)
        with handler({prompt: handler({prompt: next_cont})(cont)}):
            return body(*a, **k)

    return bound_body
