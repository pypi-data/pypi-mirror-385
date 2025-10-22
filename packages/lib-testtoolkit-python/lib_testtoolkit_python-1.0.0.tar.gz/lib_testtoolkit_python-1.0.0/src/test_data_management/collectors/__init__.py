"""
Collectors for gathering test results.
"""

from .junit_collector import JUnitCollector
from .allure_collector import AllureCollector
from .cucumber_collector import CucumberCollector
from .nunit_collector import NUnitCollector

__all__ = [
    'JUnitCollector',
    'AllureCollector',
    'CucumberCollector',
    'NUnitCollector'
] 