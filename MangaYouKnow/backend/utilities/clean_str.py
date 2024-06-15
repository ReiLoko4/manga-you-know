import re

def clean_str(s: str) -> str:
    return re.sub(
        r'-+', 
        '-', 
        re.sub(
            r'[^a-z0-9-]', 
            '-', 
            s.lower()
        ).strip('-')
    )
