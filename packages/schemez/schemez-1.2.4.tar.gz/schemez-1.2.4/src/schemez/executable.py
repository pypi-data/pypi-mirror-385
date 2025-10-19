from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable  # noqa: TC003
from typing import TYPE_CHECKING, Any, TypeVar, overload

from schemez.functionschema import FunctionType, create_schema


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from schemez.functionschema import FunctionSchema

T_co = TypeVar("T_co", covariant=True)


class ExecutableFunction[T_co]:
    """Wrapper for executing functions with different calling patterns."""

    def __init__(
        self,
        schema: FunctionSchema,
        func: (
            Callable[..., T_co]
            | Callable[..., Generator[T_co]]
            | Callable[..., AsyncGenerator[T_co]]
            | Callable[..., AsyncIterator[T_co]]
        ),
    ) -> None:
        """Initialize with schema and function.

        Args:
            schema: OpenAI function schema
            func: The actual function to execute
        """
        self.schema = schema
        self.func = func

    def run(self, *args: Any, **kwargs: Any) -> T_co | list[T_co]:  # noqa: PLR0911
        """Run the function synchronously.

        Args:
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Either a single result or list of results for generators
        """
        match self.schema.function_type:
            case FunctionType.SYNC:
                return self.func(*args, **kwargs)  # type: ignore
            case FunctionType.ASYNC:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    return asyncio.run(self.func(*args, **kwargs))  # type: ignore
                else:
                    if loop.is_running():
                        new_loop = asyncio.new_event_loop()
                        try:
                            return new_loop.run_until_complete(
                                self.func(*args, **kwargs),  # type: ignore
                            )
                        finally:
                            new_loop.close()
                    return loop.run_until_complete(
                        self.func(*args, **kwargs),  # type: ignore
                    )
            case FunctionType.SYNC_GENERATOR:
                return list(self.func(*args, **kwargs))  # type: ignore
            case FunctionType.ASYNC_GENERATOR:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    return asyncio.run(self._collect_async_gen(*args, **kwargs))
                else:
                    if loop.is_running():
                        new_loop = asyncio.new_event_loop()
                        try:
                            return new_loop.run_until_complete(
                                self._collect_async_gen(*args, **kwargs),
                            )
                        finally:
                            new_loop.close()
                    return loop.run_until_complete(
                        self._collect_async_gen(*args, **kwargs),
                    )
            case _:
                msg = f"Unknown function type: {self.schema.function_type}"
                raise ValueError(msg)

    async def _collect_async_gen(self, *args: Any, **kwargs: Any) -> list[T_co]:
        """Collect async generator results into a list.

        Args:
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            List of collected results
        """
        return [x async for x in self.func(*args, **kwargs)]  # type: ignore

    async def arun(self, *args: Any, **kwargs: Any) -> T_co | list[T_co]:
        """Run the function asynchronously.

        Args:
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Function result or list of results for generators

        Raises:
            ValueError: If the function type is unknown
        """
        match self.schema.function_type:
            case FunctionType.SYNC:
                return self.func(*args, **kwargs)  # type: ignore
            case FunctionType.ASYNC:
                return await self.func(*args, **kwargs)  # type: ignore
            case FunctionType.SYNC_GENERATOR:
                return list(self.func(*args, **kwargs))  # type: ignore
            case FunctionType.ASYNC_GENERATOR:
                return [x async for x in self.func(*args, **kwargs)]  # type: ignore
            case _:
                msg = f"Unknown function type: {self.schema.function_type}"
                raise ValueError(msg)

    async def astream(self, *args: Any, **kwargs: Any) -> AsyncIterator[T_co]:
        """Stream results from the function.

        Args:
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Yields:
            Individual results as they become available

        Raises:
            ValueError: If the function type is unknown
        """
        match self.schema.function_type:
            case FunctionType.SYNC_GENERATOR:
                for x in self.func(*args, **kwargs):  # type: ignore
                    yield x
            case FunctionType.ASYNC_GENERATOR:
                async for x in self.func(*args, **kwargs):  # type: ignore
                    yield x
            case FunctionType.SYNC:
                yield self.func(*args, **kwargs)  # type: ignore
            case FunctionType.ASYNC:
                yield await self.func(*args, **kwargs)  # type: ignore
            case _:
                msg = f"Unknown function type: {self.schema.function_type}"
                raise ValueError(msg)


@overload
def create_executable[T_co](
    func: Callable[..., T_co],
) -> ExecutableFunction[T_co]: ...


@overload
def create_executable[T_co](
    func: Callable[..., Generator[T_co]],
) -> ExecutableFunction[T_co]: ...


@overload
def create_executable[T_co](
    func: Callable[..., AsyncGenerator[T_co]],
) -> ExecutableFunction[T_co]: ...


def create_executable(
    func: (
        Callable[..., T_co]
        | Callable[..., Generator[T_co]]
        | Callable[..., AsyncGenerator[T_co]]
    ),
) -> ExecutableFunction[T_co]:
    """Create an executable function wrapper with schema.

    Args:
        func: Function to wrap

    Returns:
        Executable wrapper with schema
    """
    schema = create_schema(func)
    return ExecutableFunction(schema, func)


if __name__ == "__main__":
    from typing import Literal

    def get_weather(
        location: str,
        unit: Literal["C", "F"] = "C",
        detailed: bool = False,
    ) -> dict[str, str | float]:
        return {"temp": 22.5, "conditions": "sunny"}

    exe = create_executable(get_weather)
    # Execute the function
    result = exe.run("London", unit="C")
    print("\nFunction Result:")
    print(result)
