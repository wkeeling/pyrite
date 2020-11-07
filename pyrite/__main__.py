"""This module acts as the entry point for running the application."""
from pyrite import application, settings


def main():
    settings.initialise()
    application.run()


if __name__ == '__main__':
    main()
