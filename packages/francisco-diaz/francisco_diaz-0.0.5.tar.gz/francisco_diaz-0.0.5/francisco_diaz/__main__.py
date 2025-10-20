from .speakers import Francisco
from pathlib import Path
# from francisco_diaz.speakers import Francisco


def main():
    Francisco().print_name()
    # with open("names.txt", encoding="utf-8") as f:
    with (Path(__file__).parent / "names.txt").open(encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    main()
