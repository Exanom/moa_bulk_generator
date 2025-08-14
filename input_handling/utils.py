

def handle_input(prompt:str, options: list[str] = ['y','n'], default_answer: str = 'y') -> str:
    response = ''
    options = [x.lower() for x in options]
    while(response not in options):
        response = input(prompt).lower()
    return response