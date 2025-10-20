import os
import time
from datetime import datetime

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
          