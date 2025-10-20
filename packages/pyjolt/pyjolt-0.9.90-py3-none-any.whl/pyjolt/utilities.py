"""
Utility methods for PyJolt
"""
import importlib
import importlib.util
import os
import re
import sys
import inspect
import asyncio
import mimetypes
import aiofiles
from asyncio import Task, Future
from typing import Callable, Any, Optional

from .exceptions import StaticAssetNotFound

def import_module(import_string: str):
    module_path, obj_name = import_string.split(":")
    try:
        module = importlib.import_module(module_path)
    except Exception as e:
        raise
    return getattr(module, obj_name)


def get_app_root_path(import_name: str) -> str:
    """
    Finds the root path of the application package on the file system or
    uses the current working directory
    """
    # First, check if the module is already imported and has a __file__ attribute.
    mod = sys.modules.get(import_name)
    if mod is not None and hasattr(mod, "__file__"):
        return os.path.dirname(os.path.abspath(mod.__file__)) # type: ignore

    # Tries to load the modules loader
    loader = importlib.util.find_spec(import_name)
    if loader is None or import_name == "__main__":
        return os.getcwd()

    # Checks if loader has a filename
    filepath = None
    if hasattr(loader, "get_filename"):
        filepath = loader.get_filename(import_name) # type: ignore

    # Tries to lookup the loaders path attribute
    if not filepath and hasattr(loader, "path"):
        filepath = loader.path # type: ignore

    if filepath is None:
        #Current working directory fallback
        return os.getcwd()

    # Return the directory name of the absolute path where the module resides.
    return os.path.dirname(os.path.abspath(filepath))

async def run_sync_or_async(func: Callable, *args, **kwargs):
    """
    Support for sync or async methods
    Runs async method directly or a sync method in a threadpool
    """
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: func(*args, **kwargs)
    )

def run_in_background(func: Callable[..., Any], *args, executor = None, **kwargs) -> Task|Future:
    """
    Fire-and-forget a function (async or sync) without awaiting its result.
    Useful for sending emails or other longer running tasks that do not
    need to wait for the result.
    """

    # current running event loop
    loop = asyncio.get_running_loop()

    if asyncio.iscoroutinefunction(func):
        # Schedule the async function to run
        return loop.create_task(func(*args, **kwargs))

    # If it's a sync function, run it in the default thread pool executor
    return loop.run_in_executor(executor, func, *args, **kwargs)

async def get_file(path: str, filename: Optional[str] = None, content_type: Optional[str] = None):
    """
    Asynchronously opens the file at `path`.
    - `filename` is optional (used for Content-Disposition).
    - `content_type` is optional (guess using `mimetypes` if not provided).
    
    Returns a tuple (status_code, headers, body_bytes).
    """

    # Guess the MIME type if none is provided
    guessed_type, _ = mimetypes.guess_type(path)
    content_type = content_type or (guessed_type or "application/octet-stream")

    headers = {
        "Content-Type": content_type
    }
    if filename:
        # For file download if filename is provided
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    try:
        async with aiofiles.open(path, mode="rb") as f:
            data = await f.read()
    except FileNotFoundError:
        # pylint: disable-next=W0707,E0710
        raise StaticAssetNotFound()

    return 200, headers, data

async def get_range_file(res, file_path: str, range_header: str, content_type: str):
    """Returns a ranged response"""
    total = os.path.getsize(file_path)
    m = re.match(r"bytes=(\d+)-(\d*)", range_header)
    if not m:
        start, end, status = 0, total - 1, 200
    else:
        start = int(m.group(1))
        end   = int(m.group(2)) if m.group(2) else total - 1
        end   = min(end, total - 1)
        if start > end:
            raise StaticAssetNotFound()
        status = 206

    length = end - start + 1
    headers = {
        "Content-Type":   content_type,
        "Accept-Ranges":  "bytes",
        "Content-Length": str(length),
        "Cache-Control":  "public, max-age=300",
        "ETag": f'"{os.path.getmtime(file_path):.0f}-{length}"'
    }
    if status == 206:
        headers["Content-Range"] = f"bytes {start}-{end}/{total}"

    # **Don’t** read the bytes here.  Just stash info on `res`.  
    res.status(status)
    # merge headers onto res.headers
    res.headers.update(headers)
    # mark zero-copy parameters
    res.set_zero_copy({
        "file_path": file_path,
        "start":      start,
        "length":     length
    })
    return res
