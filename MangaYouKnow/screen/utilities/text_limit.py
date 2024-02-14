def limit_text(text: str, lenght: int) -> str:
    return text[:lenght - 3] + '...' if len(text) > lenght else text
