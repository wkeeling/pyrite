"""This module acts as the entry point for running the application."""
from pyrite import application
from pyrite import settings


if __name__ == '__main__':
    settings.initialise()
    application.run()
