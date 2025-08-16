import os


def handle_input(
    prompt: str, options: list[str] | None = ["y", "n"], default_answer: str = "y"
) -> str:
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
