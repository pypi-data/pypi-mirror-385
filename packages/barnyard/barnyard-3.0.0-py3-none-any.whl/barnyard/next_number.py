"""
Function Name: get

Module: next_number

Purpose:
---------
The `get` function persistently generates and tracks the next sequential number within a specified numeric range. 
It reads the last issued number from a file, increments it by a configurable amount, wraps around or stops at the 
upper limit depending on settings, and writes the updated value back to the file. This functionality supports 
use cases like quota management, issuing sequential IDs, batch numbers, or round-robin counters with state 
persistence across multiple runs.

Parameters:
-----------
filename : str  
    The base filename to store the last issued number. If no `.txt` extension is present, it is appended automatically.

max_num : int  
    The exclusive upper bound for the number range. Internally adjusted to be inclusive. Must be provided.

min_num : int, optional (default=0)  
    The inclusive lower bound of the numeric sequence.

increment : int, optional (default=1)  
    The amount by which the sequence increments on each call.

restart_at_end : bool, optional (default=True)  
    Controls behavior when the sequence exceeds `max_num`:  
    - If True, the sequence wraps back to `min_num` (cycling behavior).  
    - If False, the sequence halts and returns None, indicating quota exhaustion.

Internal Logic:
----------------
1. Converts the exclusive `max_num` to an inclusive upper bound by decrementing it by 1.

2. Ensures the filename ends with `.txt` for consistency.

3. Validates that `max_num` is provided; raises `ValueError` if not.

4. Defines a backup file by appending `_backup.txt` to the original filename.

5. Defines an internal helper `read_number(file)` that reads an integer from the given file, 
   returning `None` if the file is missing or contains invalid data.

6. Attempts to read the last number from the main file, falling back to the backup file if necessary.

7. If both files are missing or contain invalid/out-of-bound data, initializes the sequence starting point 
   as `min_num - increment` so the next returned number will be `min_num`.

8. Calculates the next number by adding `increment` to the last number.

9. If the next number exceeds `max_num`:  
   - If `restart_at_end` is True, it wraps the sequence to stay within `[min_num, max_num]`.  
   - Otherwise, it returns `None` to indicate the end of the quota.

10. Writes the last number (before increment) to the backup file to maintain a recovery point.

11. Writes the next number to the main file to persist the updated state.

Return Value:
--------------
Returns the next number as an integer within the inclusive range `[min_num, max_num]`.

Returns `None` if the quota is exhausted and `restart_at_end` is set to False.

Usage Example:
---------------
Calling:

    next_number.get("counter", max_num=5)

When `counter.txt` does not exist, will:
- Initialize files and start sequence from 0.
- Return 0 on first call, then 1, 2, 3, and 4 on subsequent calls.
- On next call after 4:  
  - Wrap back to 0 if `restart_at_end=True`.  
  - Return `None` if `restart_at_end=False`.

"""
#from barnyard.cleandb import main as f
from .cleandb import main as f



def get(txt_name, max_num, min_num=0, increment=1, restart_at_end=True, display=True):
    if max_num is None:
        raise ValueError("max_num must be specified")

    data = f.r(txt_name, set_new=[], notify_new=False)

    # Validate current number
    if data:
        current = int(data[0])
    else:
        if display:
            print(f"🟡 WARNING: Invalid or missing data in '{txt_name}'. Resetting to {min_num}.")
        current = min_num - increment
        f.w(txt_name, [str(current)], is2d=False)

    next_number = current + increment

    if next_number > max_num:
        if restart_at_end:
            range_size = max_num - min_num + 1
            next_number = min_num + (next_number - min_num) % range_size
            if display:
                print(f"🔁 INFO: Sequence reached max_num ({max_num}) and wrapped back to {next_number} within range [{min_num}–{max_num}]")
        else:
            if display:
                print("🔴 END of Quota: Max number reached and restart_at_end=False.")
            return None

    f.w(txt_name, [str(next_number)], is2d=False)

    return next_number