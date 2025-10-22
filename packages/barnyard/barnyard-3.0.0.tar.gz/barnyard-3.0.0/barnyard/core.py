import os
import time
from datetime import datetime
import concurrent.futures

"""
import max_time
import loop_progress
import since_when
import PK_generator
from max_clear import clear_output
import cleandb.main as db
"""
from . import max_time
from . import since_when
from . import PK_generator
from .cleandb import main as db
from . import validations


def log_barn_status(barn, action, len_label, len_value):
    """
    Logs a barn status line with centered columns and status icons (✔️ / ✖️).

    Args:
        barn (str): Barn name.
        action (str): The action being performed.
        len_label (str): Label for the length field.
        len_value (int or str): Value for the length field.
    """
    time_now = f"{datetime.now():%H:%M:%S}"

    # Compose "Barn: Name"
    barn_text = f"Barn: {barn.title()}"
    action_text = f"Action: {action}"

    # Handle ✔️ / ✖️ based on len_value
    len_value_str = str(len_value).strip()
    if len_value_str.isdigit():
        val = int(len_value_str)
        status_icon = "✔️" if val == 0 else "✖️"
        len_text = f"{len_label}: {val} {status_icon}"
    else:
        len_text = f"{len_label}:"

    # Center all columns
    barn_field   = barn_text.center(24)
    action_field = action_text.center(30)
    len_field    = len_text.center(26)

    # Final log output
    print(f"🐴  {barn_field} | {action_field} | {len_field} | 🕒 Time: {time_now}")


def remove_key_match_from_barn(barn, key):
    """
    update after a deletion.
    when an item move to reinstate it get remove from the barn.\
    """
    barn_list = db.r(barn) 
    filtered = [ x for x in barn_list if str(x[2][0]) != str(key) ]
    db.w(barn, filtered)


def remove_key_match_from_reinstate(barn_reinstate, key_id):
    """
     reverse of remove_key_match_from_barn def 
    """ 
    barn_reinstate_items = db.r(barn_reinstate)    
    filtered = [ x for x in barn_reinstate_items if str(x[1][0]) != str(key_id) ]
    db.w(barn_reinstate, filtered)


def remove_duplicate_from_force_stop (barn):
    """
    when a lead is been reinstated and it process isnt completed but the append is alread done
    this helps remove the duplicate before the process starts.
    """
    barn_reinstate = f"{barn}_reinstate"
    
    main= db.r(barn)
    reinstate = db.r(barn_reinstate)

    if reinstate:
        
        all_barn_keys = [x[2][0] for x in main]
        filtered_reinstate = [x for x in reinstate if x[1][0] not in all_barn_keys]
    
        db.w(barn_reinstate, filtered_reinstate)


def fetch_and_add_to_barnyard(barn, add, batch, calls=1, display=True):
    """
    Fetches new leads or reinstates stale ones, then adds them to the barn with timestamps and unique IDs.

    Args:
        barn (str): The name of the barn to add leads to.
        add (callable): A function that returns a list of leads.
        batch (int): Number of leads to process at once.
        call (int, optional): Number of full fetch → add-to-barn cycles. Defaults to 1.
        display (bool, optional): Whether to show progress/logs. Defaults to True.

    Returns:
        list: A list of dictionaries with 'key' (ID) and 'value' (lead).
    """
    key_id_plus_leads = []

    barn_reinstate = f"{barn}_reinstate"
    barn_reinstate_items = db.r(barn_reinstate)
    barn_reinstate_items_len = len(barn_reinstate_items)

    remove_duplicate_from_force_stop(barn)  # Start by cleaning up

    stale_upload = False
    if barn_reinstate_items_len >= batch:
        leads = barn_reinstate_items[:batch]
        stale_upload = True
    else:
        leads = None  # leads will be fetched in loop below

    # Display happens once here
    if display:
        if stale_upload:
            log_barn_status(barn, "Reinstating", "Barn R. len", barn_reinstate_items_len)
        else:
            log_barn_status(barn, "Fetch & Add", "Barn R. len", "0")

    # If using stale leads
    if stale_upload:
        current_time = str(max_time.now())
        for i, lead in enumerate(leads):
            key_id = lead[1][0]
            lead = lead[0]

            if not isinstance(lead, list):
                lead = [lead]

            add_to_BarnYard = [lead, [current_time], [key_id]]
            db.a(barn, [add_to_BarnYard])
            remove_key_match_from_reinstate(barn_reinstate, key_id)

            key_id_plus_leads.append({'key': key_id, 'value': lead})

    # Else, fetch new leads and add them in `call` cycles
    else:
        for c in range(calls):
            try:
                leads = add()
            except Exception as e:
                error_msg = f"❌ Error calling add() at cycle {c + 1}: [{type(e).__name__}] {e}"
                raise RuntimeError(error_msg)

            if not leads:
                continue

            current_time = str(max_time.now())
            for lead in leads:
                key_id = PK_generator.get()

                if not isinstance(lead, list):
                    lead = [lead]

                add_to_BarnYard = [lead, [current_time], [key_id]]
                db.a(barn, [add_to_BarnYard])

                key_id_plus_leads.append({'key': key_id, 'value': lead})

    return key_id_plus_leads


def reinstate_barn(barn, batch, expiry, display=True):
    """
    Moves expired entries from the barn to the reinstate list based on the provided expiry time.

    Args:
        barn (str): The barn key to check for expired leads.
        batch (int): Batch size, used only for display purposes.
        expiry (int): Expiry time in seconds; leads older than this will be moved.
        display (bool, optional): Whether to show progress/logs. Defaults to True.
    """
    barn_reinstate = f"{barn}_reinstate"
    tidy_list = db.r(barn)
    len_tidy_list = len(tidy_list)
    
    if display:
        barn_len = max(0, len(db.r(barn)) - batch)  # safer to reread for length
        action = "Filtering"
        len_label = "Barn Len"
        len_value = barn_len
    
        log_barn_status(barn, action, len_label, len_value)

    for i, lead in enumerate(tidy_list):
        time_diff = since_when.get(lead[1][0], 's')
        if time_diff > expiry:
            lead_data = lead[0]
            key = lead[2][0]
            db.a(barn_reinstate, [[lead_data,[key]]])
            remove_key_match_from_barn(barn, key)

"""
def deleted_leads(barn):  
    #get all deleted_keys
    all_deleted_keys = []
    for i in range(12):
        console_delete_file = f'_{i}_{barn}_'
        del_keys  = db.r(console_delete_file)
        all_deleted_keys.extend(del_keys)
    return set(all_deleted_keys)
    

def read_barn_records(barn):

    #current leads while removing the actual deleted leads

    active_deleted_leads = [str(x) for x in deleted_leads(barn)]
    pre_del_leads = [[x[0], x[2]] for x in db.r(barn)]
    return [lead for lead in pre_del_leads if str(lead[1][0]) not in active_deleted_leads ]


def read_reinstate_records(barn):

    #current _reinstate leads while removing the actual deleted leads
    
    reinstate_barn = f"{barn}_reinstate"
    active_deleted_leads = [str(x) for x in deleted_leads(barn)]
    pre_del_leads = [x for x in db.r(reinstate_barn)]
    return [lead for lead in pre_del_leads if str(lead[1][0]) not in active_deleted_leads ]
"""

def fetch_deleted_keys(i, barn):
    console_delete_file = f'__{i}_{barn}__'
    return db.r(console_delete_file)

def deleted_leads(barn):
    # Get all deleted keys in parallel
    all_deleted_keys = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_deleted_keys, i, barn) for i in range(12)]
        for future in concurrent.futures.as_completed(futures):
            all_deleted_keys.extend(future.result())
    return set(all_deleted_keys)

def read_barn_records(barn):
    active_deleted_leads = [str(x) for x in deleted_leads(barn)]
    pre_del_leads = [[x[0], x[2]] for x in db.r(barn)]
    return [lead for lead in pre_del_leads if str(lead[1][0]) not in active_deleted_leads]

def read_reinstate_records(barn):
    reinstate_barn = f"{barn}_reinstate"
    active_deleted_leads = [str(x) for x in deleted_leads(barn)]
    pre_del_leads = [x for x in db.r(reinstate_barn)]
    return [lead for lead in pre_del_leads if str(lead[1][0]) not in active_deleted_leads]

    

def format_key(key):
    if isinstance(key, (list, tuple)) and len(key) == 1:
        return key[0]
    return key


def _find(barn, keys=None, values=None, display=True):
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
    records = _info(barn, display=False)  # Get all records

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

    """
    elif values is not None:
        # Convert `values` to a 2D list if necessary
        if isinstance(values, (int, str)):
            values = [[values]]
        elif isinstance(values, list):
            if not values or not isinstance(values[0], list):
                values = [values]  # make it 2D only if not already
            
        values_set = set(tuple(v) for v in values)
        matched = [record for record in records if tuple(record[0]) in values_set]

        results = [record[1] for record in matched]
    """
    if values is not None:
        # Normalize values once (int/str → [[val]], list → [val] or leave if already 2D)
        if isinstance(values, (int, str)):
            values = [[values]]
        elif isinstance(values, list) and (not values or not isinstance(values[0], list)):
            values = [values]

        for _ in range(2):
            values_set = set(tuple(v) for v in values)
            results = [record[1] for record in records if tuple(record[0]) in values_set]
            if results:
                break
            # Retry: flatten and wrap each element
            if len(values) == 1:
                values = [[v] for v in values[0]]

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
            

def _info(barn, display=True):
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
    if not isinstance(display, bool):
        raise ValueError(f"'display' must be a boolean (True or False), got {type(display).__name__}")

    records = read_barn_records(barn)
    reinstate_records = read_reinstate_records(barn)
    combined_records = records + reinstate_records

    if display:
        display_records(combined_records, len(records), barn)

    # Prepare final output
    return [[item, format_key(key)] for item, key in combined_records]



def _listdir(display=True):
    """
    Lists all main barns (excluding reinstate barns and barns
    surrounded by underscores) from the directory.

    Parameters
    ----------
    display : bool, optional (default=True)
        If True, prints the list of barns.

    Returns
    -------
    list of str
        List of barn names (excluding reinstate barns and those 
        with names starting and ending with underscores).
    """
    if not isinstance(display, bool):
        raise ValueError(f"'display' must be a boolean (True or False), got {type(display).__name__}")
        
    all_barns = db.listdir(display=False)  # Get all entries silently

    # Filter out barns that end with '_reinstate' or start and end with '_'
    main_barns = [
        barn for barn in all_barns
        if not barn.endswith('_reinstate') and not (barn.startswith('__') and barn.endswith('__'))
    ]

    if display:
        print("       🐴 BarnYard [ Directory ]\n")
        for i, barn in enumerate(main_barns):
            print(f"{i:<3} : {barn}")

    return main_barns


def _remove(barn, display=True):
    """
    Deletes a main barn, its reinstate barn, all related console folders,
    and its named console folder.

    Parameters
    ----------
    barn : str
        The name of the barn to remove. Must be a main barn (not a reinstate barn).

    display : bool, optional (default=True)
        If True, prints deletion messages.
    """
    if not isinstance(display, bool):
        raise ValueError(f"'display' must be a boolean (True or False), got {type(display).__name__}")
        
    if display:
        print("                🐴 BarnYard  [ Deletion ]\n")

    # Get all current entries once
    all_barns = db.listdir(display=False)

    # 1. Delete main barn
    if barn in all_barns:
        db.remove(barn, display=display)
    else:
        if display:
            print(f"❓ Main barn '{barn}' not found.")

    # 2. Delete corresponding reinstate barn
    reinstate_barn = f"{barn}_reinstate"
    if reinstate_barn in all_barns:
        db.remove(reinstate_barn, display=False)
        if display:
            print(f"🗑️ Removed reinstate barn: '{reinstate_barn}'")

    # 3. Delete 12 related console folders: __{i}_{barn}__
    for i in range(12):
        console_folder = f"__{i}_{barn}__"
        if console_folder in all_barns:
            db.remove(console_folder, display=False)
            if display:
                print(f"🧹 Removed console folder: '{console_folder}'")

    # 4. Delete barn_console folder
    console_name = f"{barn}_console"
    if console_name in all_barns:
        db.remove(console_name, display=False)
        if display:
            print(f"🧼 Removed barn console: '{console_name}'")

