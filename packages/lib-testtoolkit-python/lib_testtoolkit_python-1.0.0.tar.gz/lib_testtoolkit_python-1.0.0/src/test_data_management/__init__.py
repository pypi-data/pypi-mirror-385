"""
Test data management module.
Provides collectors for various test result formats
and providers for integration with test management systems.
"""

from .core.test_data_manager import TestDataManager
from .core.base_provider import BaseProvider, TestResult, ResultStatus, TestRun
from .core.base_collector import BaseCollector
from .collectors.junit_collector import JUnitCollector
from .collectors.allure_collector import AllureCollector
from .collectors.cucumber_collector import CucumberCollector
from .collectors.nunit_collector import NUnitCollector
from .providers.testrail_provider import TestRailProvider

__all__ = [
    'TestDataManager',
    'BaseProvider',
    'BaseCollector',
    'TestResult',
    'ResultStatus',
    'TestRun',
    'JUnitCollector',
    'AllureCollector',
    'CucumberCollector',
    'NUnitCollector',
    'TestRailProvider'
]

__version__ = '1.0.0' 