from colorama import init as colorama_init
from colorama import Fore


class Speaker:
    name = "default"

    def __init__(self):
        colorama_init()

    def print_name(self):
        print(f"My name is {Fore.GREEN}{self.name}{Fore.RESET}!")
