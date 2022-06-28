import os

from config.config import settings


def run():
    name = settings.BASE_PATH
    print(name)


if __name__ == "__main__":
    run()
