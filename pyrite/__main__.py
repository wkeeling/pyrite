"""This module acts as the entry point for running the application."""
from pyrite import app, settings, state


def main():
    settings.initialise()
    state.initialise()
    app.run()


if __name__ == '__main__':
    main()
