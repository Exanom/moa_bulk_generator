

def handle_input(prompt:str, options: list[str] = ['y','n'], default_answer: str = 'y', force_mode:bool = False) -> str:
    response = ''
    print(force_mode)
    options = [x.lower() for x in options]
    while(response not in options):
        response = input(prompt).lower()
    return response