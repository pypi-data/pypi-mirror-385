from typing import Callable, Iterable, Any, Union
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def for_loop_decorator(data_list):
    """
    A decorator that calls the decorated function with each element
    from the provided list or tuple.

    Args:
        data_list: A list or tuple of data to iterate over.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for item in data_list:
                func(item, *args, **kwargs)

        return wrapper

    return decorator


def threaded_for_loop(
    data_list: Iterable, max_workers: int = None, thread_safe: bool = True
):
    """
    A decorator that executes the decorated function in parallel threads
    for each element in the provided iterable.

    Args:
        data_list: The list of items to process
        max_workers: Maximum number of threads to use
        thread_safe: Whether to use thread-safe execution
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Thread-safe lock for shared resources if needed
            lock = threading.Lock() if thread_safe else None

            def thread_safe_func(item, *inner_args, **inner_kwargs):
                """Wrapper function that applies thread safety if enabled"""
                if lock:
                    with lock:
                        return func(item, *inner_args, **inner_kwargs)
                else:
                    return func(item, *inner_args, **inner_kwargs)

            # Use ThreadPoolExecutor for better thread management
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks to the thread pool
                future_to_item = {
                    executor.submit(thread_safe_func, item, *args, **kwargs): item
                    for item in data_list
                }

                # Wait for all tasks to complete
                results = []
                for future in as_completed(future_to_item):
                    item = future_to_item[future]
                    try:
                        result = future.result()
                        results.append((item, result))
                    except Exception as e:
                        print(f"Error processing item {item}: {e}")
                        results.append((item, None))

                return results

        return wrapper

    return decorator


# Simple version matching your pattern
def simple_threaded_for_loop(data_list: Iterable, max_workers: int = None):
    """
    A simpler decorator that executes the function in parallel without
    collecting results or handling errors in detail.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            threads = []

            for item in data_list:
                thread = threading.Thread(
                    target=func, args=(item, *args), kwargs=kwargs
                )
                threads.append(thread)
                thread.start()

                # Limit concurrent threads
                if max_workers and len(threads) >= max_workers:
                    threads[0].join()
                    threads.pop(0)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

        return wrapper

    return decorator
