
from flask import Flask, render_template, request
import secrets
import string

app = Flask(__name__)


def get_number(value, minimum, maximum, name):
    try:
        number = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Please enter a valid number for {name}.")

    if not minimum <= number <= maximum:
        raise ValueError(
            f"{name} must be between {minimum} and {maximum}."
        )

    return number


def generate_password(letters, numbers, symbols):
    characters = []

    characters.extend(
        secrets.choice(string.ascii_letters)
        for _ in range(letters)
    )
    characters.extend(
        secrets.choice(string.digits)
        for _ in range(numbers)
    )
    characters.extend(
        secrets.choice(string.punctuation)
        for _ in range(symbols)
    )

    secrets.SystemRandom().shuffle(characters)
    return "".join(characters)


@app.route("/", methods=["GET", "POST"])
def home():
    data = {
        "password_type": request.form.get("password_type", "1"),
        "length": request.form.get("length", "12"),
        "method": request.form.get("method", "2"),
        "letters": request.form.get("letters", "6"),
        "numbers": request.form.get("numbers", "3"),
        "symbols": request.form.get("symbols", "0"),
        "fill_choice": request.form.get("fill_choice", ""),
        "add_letters": request.form.get("add_letters", "0"),
        "add_numbers": request.form.get("add_numbers", "0"),
        "count": request.form.get("count", "1"),
    }

    error = None
    passwords = []
    settings = None
    remaining = 0
    show_remaining = False
    exited = False

    if request.method == "POST":
        try:
            if data["password_type"] == "4":
                exited = True
            else:
                if data["password_type"] not in ("1", "2", "3"):
                    raise ValueError("Choose password type 1, 2, or 3.")

                length = get_number(
                    data["length"], 4, 128, "Password length"
                )
                count = get_number(
                    data["count"], 1, 20, "Number of passwords"
                )

                if data["method"] not in ("1", "2"):
                    raise ValueError("Choose manual or automatic creation.")

                if data["method"] == "1":
                    letters = get_number(
                        data["letters"], 0, length, "Alphabets"
                    )
                    numbers = get_number(
                        data["numbers"], 0, length, "Numbers"
                    )
                    symbols = get_number(
                        data["symbols"], 0, length, "Special symbols"
                    )

                    total = letters + numbers + symbols

                    if total > length:
                        raise ValueError(
                            f"Your counts total {total}, but your "
                            f"password length is {length}. Enter the counts again."
                        )

                    remaining = length - total

                    if remaining > 0:
                        choice = data["fill_choice"]

                        if not choice:
                            show_remaining = True
                        elif choice == "letters":
                            letters += remaining
                        elif choice == "numbers":
                            numbers += remaining
                        elif choice == "symbols":
                            symbols += remaining
                        elif choice == "custom":
                            add_letters = get_number(
                                data["add_letters"], 0, remaining,
                                "Additional alphabets"
                            )
                            left = remaining - add_letters

                            add_numbers = get_number(
                                data["add_numbers"], 0, left,
                                "Additional numbers"
                            )

                            letters += add_letters
                            numbers += add_numbers
                            symbols += left - add_numbers
                        else:
                            raise ValueError(
                                "Choose how to fill the remaining spaces."
                            )

                    if show_remaining:
                        return render_template(
                            "index.html",
                            data=data,
                            error=None,
                            passwords=[],
                            settings=None,
                            remaining=remaining,
                            show_remaining=True,
                            exited=False
                        )

                else:
                    symbols = max(1, length // 6)
                    numbers = max(1, length // 5)
                    letters = length - numbers - symbols

                if letters + numbers + symbols != length:
                    raise ValueError(
                        "Character counts must equal the password length."
                    )

                passwords = [
                    generate_password(letters, numbers, symbols)
                    for _ in range(count)
                ]

                settings = {
                    "length": length,
                    "letters": letters,
                    "numbers": numbers,
                    "symbols": symbols,
                    "count": count
                }

                data["letters"] = str(letters)
                data["numbers"] = str(numbers)
                data["symbols"] = str(symbols)

        except ValueError as exc:
            error = str(exc)

    return render_template(
        "index.html",
        data=data,
        error=error,
        passwords=passwords,
        settings=settings,
        remaining=remaining,
        show_remaining=show_remaining,
        exited=exited
    )


if __name__ == "__main__":
    app.run(debug=True)
