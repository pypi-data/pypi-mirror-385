def help():
    """
    🐴 BarnYard: Quick Usage Guide
    
    next(barn, add, *, batch, duration, expire, calls=1, display=True)
      - barn: string — name of the barn
      - add: callable — function that returns leads
      - batch: int — number of leads per cycle
      - duration: int/float — wait time between calls
      - expire: int/float — time after which leads are reinstated
      - calls: int — number of cycles (default 1)
      - display: bool — show logs (default True)
    
    shed(barn, keys, display=True)
      - keys: str or list — lead keys to permanently remove
    
    info(barn, display=True)
      - Returns all current and reinstated leads
    
    listdir(display=True)
      - Lists all barns
    
    remove(barn, display=True)
      - Deletes barn and reinstate barn
    
    find(barn, keys=None, values=None, display=True)
      - keys: str, list — find by lead key(s)
      - values: list of lists — find by item values
    
    🔥 Pro Tip:
    Always call `shed()` only after a lead has completed its task successfully.
    """
    print(help.__doc__)
