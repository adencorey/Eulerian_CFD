from datetime import datetime

def get_now(sec=True) -> str:
    """get current time with format"""
    
    now = datetime.now()
    ref = ":%S" if sec else ""
    return now.strftime(f"%d-%m-%Y %H:%M{ref}")