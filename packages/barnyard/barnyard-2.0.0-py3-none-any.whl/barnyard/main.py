from . import core
from .cleandb import main as db
from . import others

from . import syngate
from . import validations
from . import mini_guide 

"""
import core
from max_clear import clear_output
import cleandb.main as db
import others 

import syngate
import validations
"""

db.hide("*",display=False)
db.warning(False)


def _next(barn, add, *, batch, duration, expire, calls=1, display=True):
    """
    Orchestrates fetching and adding leads to barnyard with reinstate and logging.

    Args:
        barn (str): Barn name.
        add (callable): Function returning list of leads.
        batch (int): Number of leads to process at once.
        duration (int|float): Pulse duration (time).
        expire (int|float): Expiry time (time).
        calls (int, optional): Number of fetch-add cycles. Defaults to 1.
        display (bool, optional): Whether to show logs. Defaults to True.

    Returns:
        list: List of dicts with 'key' and 'value' for added leads.

    Note:
        Parameters batch, duration, expire, calls, and display must be passed as keyword arguments.
    """

    validations.validate_next_params(barn, add, batch, duration, expire, calls, display)

    if display:
        print("🐴  ENTER  |  Barnyard System  |  ⚡ Powered by Syngate + withopen \n")

    syngate.enter(barn, pulse=duration, display=display)

    if display:
        print("")

    new_next = core.fetch_and_add_to_barnyard(barn, add, batch, calls=calls, display=display)
    core.reinstate_barn(barn, batch, expire, display=display)
    syngate.done(barn)

    return new_next


def next_wrapper(barn, add, *args, **kwargs):
    if args:
        raise TypeError(
            "❌ Invalid call to 'next' function:\n\n"
            "The parameters 'batch', 'duration', 'expire', 'calls', and 'display' "
            "must be passed as keyword arguments, not positional arguments.\n\n"
            "Correct function signature:\n"
            "  next(barn, add, *, batch, duration, expire, calls=1, display=True)\n\n"
            "Example usage:\n"
            "  next(barn, add, batch=10, duration=20, expire=30, calls=2, display=True)\n"
        )
    return _next(barn, add, **kwargs)


# Alias so users call next_wrapper transparently via 'next'
next = next_wrapper


def shed (barn, keys, display = True):
    # when a lead finally complete it course successfully it is remove from barnyard   
    if not others.filter_main_by_key(barn, keys,display = display):
        if not others.filter_reinstate_by_keys(barn, keys, display = display):
            if display:
                print(f"🐴  Barn: {barn}  |  Action: Shed Barn  |  ⚠️ Verify Barn name: No matches found")
            else:
                raise ValueError(f"No matches found in barn '{barn}'. Please verify the barn name.")


def read_barn_records(barn_name):
    try:
        return [[x[0], x[2]] for x in db.r(barn_name)]
    except Exception as e:
        print(f"❌ Failed to read barn '{barn_name}': {e}")
        return []

def read_reinstate_records(barn_name):
    reinstate_barn = f"{barn_name}_reinstate"
    try:
        return [x for x in db.r(reinstate_barn)]
    except Exception as e:
        print(f"⚠️ No reinstate records for '{barn_name}': {e}")
        return []

def format_key(key):
    if isinstance(key, (list, tuple)) and len(key) == 1:
        return key[0]
    return key

def display_records(records, main_count, barn_name):
    reinstate_count = len(records) - main_count

    print("\n🐴  BarnYard Viewer")
    print("==========================\n")
    print(f"Barn Name            : {barn_name}")
    print(f"Total Records        : {len(records)}\n")
    print(f"🟩 Main Barn Count     : {main_count}")
    print(f"🟨 Reinstate Count     : {reinstate_count}")
    print("--------------------------\n")

    index_col_width = 4    # Total width reserved for 🟩index
    key_indent_column = 8  # Fixed column where the key starts

    for i, (item, key) in enumerate(records):
        try:
            is_main = i < main_count
            emoji = "🟩" if is_main else "🟨"
            display_index = i + 1 if is_main else i - main_count + 1

            # Format index with fixed width, right-aligned
            index_str = f"{emoji}{display_index}".ljust(index_col_width)

            # First line: emoji+index and item
            print(f" {index_str} {item}")

            # Second line: key aligned to fixed column
            print(f"{' ' * key_indent_column}{format_key(key)}\n")

        except Exception as e:
            print(f"Index: {i + 1} ⚠️ Failed to parse record: {e}")
            

def info(barn, display=True):
    """
    Returns all barn records, and optionally displays them.

    Parameters
    ----------
    barn : str
        The name of the barn to read from.

    display : bool, optional
        If True, prints records vertically.

    Returns
    -------
    list
        A combined list of main and reinstate barn records with unpacked keys.
    """
    records = read_barn_records(barn)
    reinstate_records = read_reinstate_records(barn)
    combined_records = records + reinstate_records

    if display:
        display_records(combined_records, len(records), barn)

    # Prepare final output
    return [[item, format_key(key)] for item, key in combined_records]


def listdir(display=True):
    """
    Lists all main barns (excluding reinstate barns) from the directory.

    Parameters
    ----------
    display : bool, optional (default=True)
        If True, prints the list of barns.

    Returns
    -------
    list of str
        List of barn names (excluding reinstate barns)
    """
    all_barns = db.listdir(display=False)  # Get all entries silently
    main_barns = [barn for barn in all_barns if not barn.endswith('_reinstate')]

    if display:
        print("       🐴 BarnYard [ Directory ]\n")
        for i, barn in enumerate(main_barns):
            print(f"{i:<3} : {barn}")

    return main_barns


def remove(barn, display=True):
    """
    Deletes a main barn and its reinstate barn (if present).

    Parameters
    ----------
    barn : str
        The name of the barn to remove. Must be a main barn (not a reinstate barn).

    display : bool, optional (default=True)
        If True, prints deletion messages.
    """
    if barn.endswith("_reinstate"):
        if display:
            print(f"⚠️ Skipped deletion: '{barn}' is a reinstate barn. Delete the main barn to remove both.")
        return

    if display:
        print("                🐴 BarnYard  [ Deletion ]\n")

    # Delete main barn
    db.remove(barn, display=display)

    # Delete corresponding reinstate barn, if it exists
    reinstate_barn = f"{barn}_reinstate"
    all_barns = db.listdir(display=False)
    if reinstate_barn in all_barns:
        db.remove(reinstate_barn, display=False)
        if display:
            print(f"🗑️ Also removed reinstate barn: '{reinstate_barn}'")



def find(barn, keys=None, values=None, display=True):
    """
    Search for barn records by keys or values and optionally display the results.

    Parameters
    ----------
    barn : str
        The name of the barn to search records in.
    keys : list, set, tuple, or single key, optional
        One or more keys to find matching records. Mutually exclusive with `values`.
    values : list of lists or single list, optional
        One or more value lists (items) to find matching records. Mutually exclusive with `keys`.
    display : bool, optional
        If True, prints the found records with numbering. Default is True.

    Returns
    -------
    list
        If searching by `keys`, returns a list of matched item records (lists).
        If searching by `values`, returns a list of matched keys.
        If neither `keys` nor `values` is provided, returns all records as `[item, key]` pairs.

    Raises
    ------
    ValueError
        If both `keys` and `values` are provided simultaneously.
        If `barn` is not a non-empty string.
        If `display` is not a boolean.
    """
    validations.validate_find_params(barn, keys, values, display)
    records = info(barn, display=False)  # Get all records

    matched = []

    if keys is not None:
        if not isinstance(keys, (list, set, tuple)):
            keys = [keys]
        keys = set(str(k) for k in keys)
        matched = [record for record in records if str(record[1]) in keys]

        results = [record[0] for record in matched]

        if display:
            count = len(results)
            print(f"\n🐴 Found {count} matching record{'s' if count != 1 else ''}:\n" + "-"*40)
            for i, item in enumerate(results, start=1):
                print(f"{i}. {item}")
            print("-"*40)

    elif values is not None:
        if not isinstance(values, (list, set, tuple)) or (isinstance(values, list) and len(values) > 0 and not isinstance(values[0], list)):
            values = [values]
        values_set = set(tuple(v) for v in values)
        matched = [record for record in records if tuple(record[0]) in values_set]

        results = [record[1] for record in matched]

        if display:
            count = len(results)
            print(f"\n🐴 Found {count} matching record{'s' if count != 1 else ''}:\n" + "-"*40)
            for i, key in enumerate(results, start=1):
                print(f"{i}. {key}")
            print("-"*40)

    else:
        # If no keys or values, return all records as [item, key]
        results = records
        if display:
            count = len(results)
            print(f"\nAll {count} records:\n" + "-"*40)
            for i, rec in enumerate(results, start=1):
                print(f"{i}. {rec}")
            print("-"*40)

    return results


def help():

    # helper function to read the documentation summary
    
    mini_guide.help()
