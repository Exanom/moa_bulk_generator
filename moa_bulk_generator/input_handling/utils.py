import os


def handle_input(
    prompt: str, options: list[str] | None = ["y", "n"], default_answer: str = "y"
) -> str:
    """
    Helper function for handling user input where the expected response is a string. Will accept only a response that fits a predefined list, and will repeat the input prompt should an unexpected response be supplied by the user.

    Parameters:
        prompt (str): The message that will be displayed to the user
        options (list[str] | None): A list of expected responses. Can be None if any response(even an empty one) is acceptable
        default_answer (str): A default response to be used, should user interaction be dissabled. Not yet implemented

    Returns:
        str: User response that fits the criteria set by options parameter
    """
    response = ""
    if options is None:
        response = input(prompt)
        return response
    options = [x.lower() for x in options]
    while response not in options:
        response = input(prompt).lower()
    return response


def handle_input_int(
    prompt: str, min_val: int | None = None, max_val: int | None = None
) -> int:
    """
    Helper function for handling user input where the expected response is a an integer. Will accept only a response that fits defined criteria, otherwise will repeat the prompt for user input.

    Parameters:
        prompt (str): The message that will be displayed to the user
        min_val (int | None): Minimum acceptable value. User will not be able to provide an answer that is lower than this value. Can be None if there is no lower bound
        max_val (int | None): Maximum acceptable value. User will not be able to provide an answer that is higher than this value. Can be None if there is no upper bound
    
    Returns:
        int: User response, parsed into int, that fits the criteria set by min_val and max_val parameters
    """
    while True:
        response_str = input(prompt)
        try:
            response = int(response_str)
        except ValueError:
            print("Must input a number")
            continue

        if min_val is not None and response < min_val:
            print(f"Number must be at least {min_val}")
            continue
        if max_val is not None and response > max_val:
            print(f"Number must be at most {max_val}")
            continue

        return response

def handle_input_indexes(
    prompt: str
) -> list[int]:
    """
    Helper function for handling user input where the expected response is list of dataset indexes to remove. Will accept only a response that fits defined criteria, otherwise will repeat the prompt for user input.

    Parameters:
        prompt (str): The message that will be displayed to the user

    Returns:
        int: User response, parsed into list[int].
    """
    while True:
        response_str = input(prompt)
        user_input = response_str.strip()

        if not user_input:
            print("No indexes provided. Please try again.\n")
            continue

        indexes = set()
        valid = True

        for part in user_input.split(','):
            part = part.strip()
            if not part:
                continue

            if '-' in part:
                try:
                    start, end = map(int, part.split('-', 1))
                    if start > end:
                        print(f"Invalid range '{part}' (start > end)")
                        valid = False
                        break
                    indexes.update(range(start, end + 1))
                except ValueError:
                    print(f"Invalid range format: '{part}'")
                    valid = False
                    break
            else:
                if not part.isdigit():
                    print(f"Invalid index: '{part}' (not a number)")
                    valid = False
                    break
                indexes.add(int(part))

        if valid and indexes:
            return sorted(indexes)
        else:
            print("Please enter valid indexes (e.g. 1,3,6 or 2-10,14).\n")

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")
