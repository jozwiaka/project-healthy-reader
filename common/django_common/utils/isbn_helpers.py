# -----------------------------
# ISBN helpers
# -----------------------------
def clean_isbn(isbn: str) -> str:
    return isbn.replace("-", "").replace(" ", "").replace('"', "").strip()

def is_valid_isbn10(isbn: str) -> bool:
    if len(isbn) != 10 or not isbn[:-1].isdigit():
        return False
    total = sum((i + 1) * int(x) for i, x in enumerate(isbn[:-1]))
    check = isbn[-1]
    if check.upper() == "X":
        total += 10 * 10
    elif check.isdigit():
        total += 10 * int(check)
    else:
        return False
    return total % 11 == 0

def is_valid_isbn13(isbn: str) -> bool:
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = sum((int(num) * (1 if i % 2 == 0 else 3)) for i, num in enumerate(isbn[:-1]))
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(isbn[-1])

def is_valid_isbn(isbn: str) -> bool:
    isbn = clean_isbn(isbn)
    return is_valid_isbn10(isbn) or is_valid_isbn13(isbn)