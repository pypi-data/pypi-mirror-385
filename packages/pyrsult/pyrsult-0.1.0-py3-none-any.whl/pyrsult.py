"""
这是一个让你能够在python里面使用类似于Rust的Result类型的库

by: fexcode| https://github.com/fexcode/
at: 2025-10-18
on: https://github.com/fexcode/pyrsult
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union, overload, Any, Callable

T = TypeVar("T")
E = TypeVar("E")


class Result(ABC, Generic[T, E]):
    """抽象基类：统一 Success / Failure 的公共接口"""

    __slots__ = ("_value",)

    def __init__(self, value: Any) -> None:
        self._value: Any = value

    # --------------- 判别函数 ---------------
    @abstractmethod
    def is_ok(self) -> bool: ...
    @abstractmethod
    def is_err(self) -> bool: ...

    # --------------- 取值函数 ---------------
    @abstractmethod
    def unwrap(self) -> T: ...
    @abstractmethod
    def unwrap_err(self) -> E: ...
    @abstractmethod
    def unwrap_or(self, default: T) -> T: ...
    @abstractmethod
    def expect(self, msg: str) -> T: ...
    @abstractmethod
    def unwarp_or_else(self, func: Callable[[E], T]) -> T: ...

    # --------------- 工厂函数 ---------------
    @staticmethod
    def Success(value: T) -> Result[T, Any]:  # type: ignore
        return Success(value)  # type: ignore

    @staticmethod
    def Failure(error: E) -> Result[Any, E]:  # type: ignore
        return Failure(error)  # type: ignore


class Success(Result[T, Any]):
    """成功分支"""

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self._value

    def unwrap_err(self) -> Any:
        raise ValueError("Called unwrap_err on an Ok value")

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwarp_or_else(self, func: Callable[[E], T]) -> T:
        return self._value

    def expect(self, msg: str) -> T:
        return self._value

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"


class Failure(Result[Any, E]):
    """失败分支"""

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise ValueError(f"Unwrap failed | {self._value}")

    def unwrap_err(self) -> E:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return default

    def unwarp_or_else(self, func: Callable[[E], T]) -> T:
        return func(self._value)

    def expect(self, msg: str) -> T:
        raise ValueError(msg)

    def __repr__(self) -> str:
        return f"Err({self._value!r})"


# ------------------- 业务代码 -------------------
def foo(x: int) -> Result[int, str]:
    return Result.Success(x) if x > 0 else Result.Failure("x should be positive")


if __name__ == "__main__":
    ok = foo(5)
    print(ok.unwrap())  # -> 5
    print(ok.unwrap_or(0))  # -> 5

    err = foo(-5)
    print(err.unwrap_or(0))  # -> 0
    # err.expect("custom msg")  # => ValueError: custom msg
