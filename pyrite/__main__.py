"""This module acts as the entry point for running the application."""
from pyrite import settings
from pyrite.ui import app


def main():
    settings.initialise()
    app.run()


if __name__ == '__main__':
    main()
