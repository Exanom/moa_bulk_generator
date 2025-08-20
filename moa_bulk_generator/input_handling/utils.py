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


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")
