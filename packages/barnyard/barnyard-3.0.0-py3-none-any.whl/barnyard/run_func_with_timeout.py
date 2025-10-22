#import max_thread
#max_thread.get(my_function, 5, arg1, arg2)


# Function: get
# Description:
#     Runs a given function with arguments in a separate thread, enforcing a timeout.
#     If the function does not complete within the specified timeout, it returns "R".
#
# How to use:
#     result = get(my_function, 5, arg1, arg2)
#     This runs `my_function(arg1, arg2)` and waits up to 5 seconds for it to complete.
#
# When to use:
#     Use this when calling a function that may hang or take too long to complete,
#     and you want to prevent blocking your main program. The return value "R" signals a timeout.



import threading

def run(func, timeout, *args, **kwargs):
    result = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            result[0] = e  # Store the exception if it occurs

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        #print(f"Timeout for {args} {kwargs}")
        return "R"
    if isinstance(result[0], Exception):
        raise result[0]  # Re-raise if the function errored
    return result[0]




