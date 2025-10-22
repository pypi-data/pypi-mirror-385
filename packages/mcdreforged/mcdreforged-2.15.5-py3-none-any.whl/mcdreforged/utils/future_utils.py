import asyncio
import contextlib
from concurrent.futures import Future, CancelledError, TimeoutError
from typing import TypeVar, Optional, cast, Any

_T = TypeVar('_T')

__completed_none_future: Future[None] = Future()
__completed_none_future.set_result(None)


def completed(value: _T) -> Future[_T]:
	if value is None:
		return cast(Future[_T], __completed_none_future)
	future: Future[_T] = Future()
	future.set_result(value)
	return future


def wait(future: Future[Any], timeout: Optional[float] = None) -> bool:
	"""
	Wait until the given future is done (result set / exception raised / cancelled).
	No exception will be raised from the future

	:return: true if the future is done, false otherwise
	"""
	with contextlib.suppress(CancelledError, TimeoutError):
		future.exception(timeout)
	return future.done()


def copy_done_state(src: 'asyncio.Future[_T]', dst: 'Future[_T]') -> None:
	if src.cancelled():
		dst.cancel()
	elif (exc := src.exception()) is not None:
		dst.set_exception(exc)
	else:
		dst.set_result(src.result())
