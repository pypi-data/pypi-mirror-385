import time
import functools
import asyncio
from typing import Callable, Any

from datetime import datetime, timezone, timedelta
from functools import wraps

def memoize_first_call_with_reset(func):
    cached_result = None
    has_been_called = False
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal cached_result, has_been_called
        
        # 检查是否需要重置缓存
        reset = kwargs.pop('_reset', False)
        if reset:
            cached_result = None
            has_been_called = False
        
        if not has_been_called:
            cached_result = func(*args, **kwargs)
            has_been_called = True
        
        return cached_result
    
    # 添加重置方法
    def reset():
        nonlocal cached_result, has_been_called
        cached_result = None
        has_been_called = False
        
    wrapper.reset = reset
    return wrapper

@memoize_first_call_with_reset
def O_D (td: int = 0, tz: timezone = None):
    if tz is not None:
        return datetime.now(tz)
    if td != 0:
        tz = timezone(timedelta(hours=td))
        return datetime.now(tz)
    now = datetime.now()
    return now.astimezone()


def o_d(td:int=0, tz:timezone=None):
    if tz is not None:
        return datetime.now(tz)
    if td !=0:
        tz = timezone(datetime.timedelta(hours=td))
        return datetime.now(tz)
    now = datetime.now()
    return now.astimezone()


def timer(func: Callable) -> Callable:
    """
    极简版计时装饰器，支持同步和异步函数
    """
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.perf_counter()
            print(f"函数 {func.__name__} 执行耗时: {end - start:.4f} 秒")
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            end = time.perf_counter()
            print(f"函数 {func.__name__} 执行耗时: {end - start:.4f} 秒")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


if __name__ == "__main__":
    @timer
    def sync_function(x: int) -> int:
        time.sleep(x)
        return x * 2

    @timer
    async def async_function(x: int) -> int:
        await asyncio.sleep(x)
        return x * 3

    # 测试同步函数
    print(sync_function(2))

    # 测试异步函数
    print(asyncio.run(async_function(2)))
    
