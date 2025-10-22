
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def get_int(prompt, min_value=None, max_value=None):
    """
    Prompt user for an integer input, with optional min/max validation.
    """
    while True:
        val = input(Fore.CYAN + prompt + " " + Style.RESET_ALL).strip()
        if val.isdigit():
            val = int(val)
            if (min_value is not None and val < min_value) or \
               (max_value is not None and val > max_value):
                print(Fore.YELLOW + f"⚠️ Please enter a number between {min_value} and {max_value}.")
            else:
                return val
        else:
            print(Fore.RED + "⚠️ Invalid input. Enter a valid number.")


def get_float(prompt, min_value=None, max_value=None):
    """
    Prompt user for a float input, with optional min/max validation.
    """
    while True:
        val = input(Fore.CYAN + prompt + " " + Style.RESET_ALL).strip()
        try:
            val = float(val)
            if (min_value is not None and val < min_value) or \
               (max_value is not None and val > max_value):
                print(Fore.YELLOW + f"⚠️ Please enter a number between {min_value} and {max_value}.")
            else:
                return val
        except ValueError:
            print(Fore.RED + "⚠️ Invalid input. Enter a valid number.")


def get_str(prompt, capitalize=False, lower=False, upper=False):
    """
    Prompt user for a string input. Optional formatting: capitalize, lower, upper.
    """
    val = input(Fore.CYAN + prompt + " " + Style.RESET_ALL).strip()
    if capitalize:
        val = val.title()
    elif lower:
        val = val.lower()
    elif upper:
        val = val.upper()
    return val


def get_choice(prompt, choices):
    """
    Prompt user to select from a list of choices (numbers).
    Returns the selected choice.
    """
    if not choices:
        raise ValueError("Choices list cannot be empty.")
    
    while True:
        print(Fore.MAGENTA + prompt)
        for i, choice in enumerate(choices, 1):
            print(Fore.GREEN + f"{i}. {choice}")
        selection = input(Fore.CYAN + "Enter choice number: " + Style.RESET_ALL).strip()
        if selection.isdigit() and 1 <= int(selection) <= len(choices):
            return choices[int(selection)-1]
        else:
            print(Fore.RED + "⚠️ Invalid choice. Try again.")


def confirm(prompt="Are you sure? (y/n): "):
    """
    Ask user for a yes/no confirmation.
    Returns True if yes, False if no.
    """
    while True:
        ans = input(Fore.CYAN + prompt + Style.RESET_ALL).strip().lower()
        if ans in ["y", "yes"]:
            return True
        elif ans in ["n", "no"]:
            return False
        else:
            print(Fore.YELLOW + "⚠️ Please enter 'y' or 'n'.")
