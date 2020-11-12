"""This module acts as the entry point for running the application."""
from pyrite import settings, state
from pyrite.ui import app


def main():
    settings.initialise()
    state.initialise()
    app.run()


if __name__ == '__main__':
    main()
