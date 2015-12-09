import logging

from logging import NullHandler

# Add a "do-nothing" handler to the top-level to avoids the following
# warning message being printed: "No handlers could be found for logger...",
# since a handler will always be found for the library's events.
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

try:
    __import__('pkg_resources').declare_namespace(__name__)
except:
    pass
