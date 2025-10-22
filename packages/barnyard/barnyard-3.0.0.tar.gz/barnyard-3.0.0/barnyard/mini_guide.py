def help():
    """
    🐴 Barnyard System: Quick Usage Guide

    ─────────────────────────────────────────────
    📦 Engine Class Usage:
      - Initialize: barn = barnyard.Engine("barn_name")
      - Use barn.next(...) to fetch leads as dict[int, list]
      - Each lead is a list; dict keys are unique integer IDs
      - After processing, delete leads with barn.shed(key)

    ─────────────────────────────────────────────
    📦 next(add, *, batch, calls=1, expire=86400, display=True)
      - add: callable         → Function that returns data to add (list of lists)
      - batch: int            → Number of items per call
      - calls: int            → Number of add() calls (default 1)
      - expire: int           → Time (in seconds) before reinstate (default: 24h)
      - display: bool         → Show console logs (default True)
      - Returns: dict[int, list] mapping integer keys to lead records

    🧹 shed(key, verify=False)
      - key: int              → Integer key to mark for deletion
      - verify: bool          → Check key exists before shedding (slower)

    🔍 find(keys=None, values=None, display=True)
      - keys: int or list     → Search for specific integer keys
      - values: list of lists → Match records with these values
      - display: bool         → Print output or not

    ℹ️ info(display=True)
      - Show barn metadata and contents (active + reinstated)

    📁 listdir(display=True)
      - List all barn names in the system

    ❌ remove(barn, display=True)
      - Permanently delete a barn and its associated data

    🔥 Pro Tip:
      Call `shed()` **only after** a record has completed its work.

    🧠 System Powered by: Syngate + withopen

    ─────────────────────────────────────────────
    """
    print(help.__doc__)

