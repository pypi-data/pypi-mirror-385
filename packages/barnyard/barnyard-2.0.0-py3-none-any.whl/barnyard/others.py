from . import days_ago
from .cleandb import main as db

"""
import days_ago
import cleandb.main as db
"""

def display_record(index, record, label="Record"):
    """
    Display a single record in a consistent format.

    Parameters
    ----------
    index : int
        The index of the record.

    record : list
        The record in format [lead, [timestamp], [key]].

    label : str
        A label describing the search type.
    """
    lead = record[0]
    timestamp = record[1][0]
    key = record[2][0]
    ago = days_ago.get(timestamp)

    #print(f"          🐴 BarnYard  [ {label} Search ]")
    print(f"\n🔎 Record at index {index}:")
    print(f"🧾 Lead:      {lead}")
    print(f"🕒 Timestamp: {timestamp} ({ago} ago)")
    print(f"🔑 Key:       {key}")


def filter_main_by_key(barn, exclude_keys, display=True):
    """
    Filter out records from the barn that have keys listed in exclude_keys.

    Parameters
    ----------
    barn : str
        The barn (database) to read from.

    exclude_keys : list of str or int
        Keys to exclude from the result.

    display : bool, optional
        If True, prints how many records were excluded. Default is True.

    Returns
    -------
    bool
        True if records were excluded and written back, False otherwise.
    """
    if not isinstance(exclude_keys, list):
        exclude_keys = [exclude_keys]

    try:
        records = db.r(barn)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to read from barn '{barn}': {e}")

    exclude_set = set(str(k) for k in exclude_keys)
    total_before = len(records)

    filtered = [x for x in records if str(x[2][0]) not in exclude_set]

    total_after = len(filtered)
    excluded_count = total_before - total_after

    if excluded_count > 0:
        if display:
            print(f"🐴 Barn: {barn.title()} | Action: Shed Barn ✅ ({excluded_count} record(s) removed)")
        db.w(barn, filtered)
        return True

    return False


def filter_reinstate_by_keys(barn, exclude_keys, display=True):
    """
    Return all records from the barn, excluding those with specific keys.

    Parameters
    ----------
    barn : str
        The barn (database) to read from.

    exclude_keys : list of str or int
        Keys to exclude from the result.

    display : bool, optional
        If True, prints how many records were excluded. Default is True.

    Returns
    -------
    bool
        True if records were excluded and written back, otherwise False.
    """
    barn_reinstate = f"{barn}_reinstate"

    if not isinstance(exclude_keys, list):
        exclude_keys = [exclude_keys]

    try:
        records = db.r(barn_reinstate)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to read from barn '{barn}': {e}")

    exclude_set = set(str(k) for k in exclude_keys)
    total_before = len(records)

    filtered = [
        record for record in records
        if str(record[1][0]) not in exclude_set
    ]

    total_after = len(filtered)
    excluded_count = total_before - total_after

    if excluded_count > 0:
        if display:
            print(f"🐴  Barn: {barn.title()}  | Action: Shed Barn ✅  | Shed: {excluded_count}")
        db.w(barn_reinstate, filtered)
        return True

    return False