"""Test package initialization and path setup.

Configures Python path to ensure podfeedfilter package modules can be
imported during test execution. Modifies sys.path to include the
parent directory for proper module resolution in test files.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))
