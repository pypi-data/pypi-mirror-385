"""
Robin Logistics Environment

A professional logistics optimization environment for hackathons and competitions.
"""

__version__ = "3.3.0"
__author__ = "Robin"
__email__ = "mario.salama@beltoneholding.com"
__description__ = "A professional logistics optimization environment for hackathons and competitions"

from .environment import LogisticsEnvironment
from .solvers import test_solver

__all__ = [
    "LogisticsEnvironment",
    "test_solver"
]