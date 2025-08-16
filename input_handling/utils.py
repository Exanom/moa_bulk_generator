import os

def handle_input(prompt:str, options: list[str] | None = ['y','n'], default_answer: str = 'y') -> str:
    response = ''
    if(options is None): 
        response = input(prompt)
        return response
    options = [x.lower() for x in options]
    while(response not in options):
        response = input(prompt).lower()
    return response

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

