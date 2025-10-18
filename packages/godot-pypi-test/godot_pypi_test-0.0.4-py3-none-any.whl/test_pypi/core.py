import os

from dotenv import load_dotenv

load_dotenv()


def main():

    config = {**os.environ}
    print(f"{config=}")


if __name__ == "__main__":
    main()
