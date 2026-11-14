
import secrets
import string


def get_number(message, minimum, maximum):
    while True:
        try:
            number = int(input(message))
            if minimum <= number <= maximum:
                return number
            print(f"Enter a number between {minimum} and {maximum}.")
        except ValueError:
            print("Please enter a valid whole number.")


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


def main():
    print("=" * 45)
    print("       CUSTOM PASSWORD GENERATOR")
    print("=" * 45)

    while True:
        print("\n1. Normal Password")
        print("2. Strong Password")
        print("3. Custom Password")
        print("4. Exit")

        choice = input("Choose password type: ").strip()

        if choice == "4":
            print("Thank you for using Password Generator!")
            break

        if choice not in ("1", "2", "3"):
            print("Invalid choice. Choose 1, 2, 3 or 4.")
            continue

        length = get_number(
            "\nEnter the total password length (4-128): ", 4, 128
        )

        print(f"\nYour total password length is {length}.")
        print("\nHow would you like to create your password?")
        print("1. I will choose alphabets, numbers and symbols")
        print("2. Create a password for me")

        while True:
            method = input("Choose an option: ").strip()
            if method in ("1", "2"):
                break
            print("Please choose 1 or 2.")

        if method == "1":
            while True:
                print("\nChoose your character counts.")

                letters = get_number(
                    "How many alphabets? ", 0, length
                )
                numbers = get_number(
                    "How many numbers? ", 0, length
                )
                symbols = get_number(
                    "How many special symbols? ", 0, length
                )

                total = letters + numbers + symbols

                if total > length:
                    print(
                        f"\nYour counts total {total}, but your "
                        f"password length is {length}."
                    )
                    print("Please enter the counts again.")
                    continue

                while total < length:
                    remaining = length - total

                    print(
                        f"\nYou still have {remaining} space(s) to fill."
                    )
                    print("1. Add alphabets")
                    print("2. Add numbers")
                    print("3. Add special symbols")
                    print("4. Choose the remaining counts yourself")

                    option = input("Choose an option: ").strip()

                    if option == "1":
                        letters += remaining

                    elif option == "2":
                        numbers += remaining

                    elif option == "3":
                        symbols += remaining

                    elif option == "4":
                        add_letters = get_number(
                            f"How many of the {remaining} spaces "
                            "should be alphabets? ",
                            0, remaining
                        )

                        left = remaining - add_letters

                        add_numbers = get_number(
                            f"How many of the remaining {left} "
                            "spaces should be numbers? ",
                            0, left
                        )

                        add_symbols = left - add_numbers

                        letters += add_letters
                        numbers += add_numbers
                        symbols += add_symbols

                        if add_symbols > 0:
                            print(
                                f"The remaining {add_symbols} "
                                "space(s) will be symbols."
                            )

                    else:
                        print("Choose 1, 2, 3 or 4.")
                        continue

                    total = letters + numbers + symbols

                break

        else:
            symbols = max(1, length // 6)
            numbers = max(1, length // 5)
            letters = length - numbers - symbols

            print("\nYour password will be created automatically.")

        print("\nFinal password settings:")
        print(f"Total length: {length}")
        print(f"Alphabets: {letters}")
        print(f"Numbers: {numbers}")
        print(f"Special symbols: {symbols}")

        count = get_number(
            "\nHow many passwords do you want? (1-20): ", 1, 20
        )

        print("\nGenerated Passwords:")

        for i in range(1, count + 1):
            password = generate_password(letters, numbers, symbols)
            print(f"Password {i}: {password}")

        print("\nPassword generation completed!")


if __name__ == "__main__":
    main()
