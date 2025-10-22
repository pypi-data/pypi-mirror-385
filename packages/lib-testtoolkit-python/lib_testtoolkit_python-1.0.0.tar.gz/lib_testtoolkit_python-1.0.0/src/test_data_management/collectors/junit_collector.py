"""
Collector for gathering results from JUnit XML files.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any
import logging

from ..core.base_collector import BaseCollector
from ..core.base_provider import TestResult, ResultStatus


class JUnitCollector(BaseCollector):
    """Collector for JUnit XML files."""
    
    _version = '1.0.0'
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize collector.
        
        Args:
            config: Collector configuration
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
    
    def validate_config(self) -> None:
        """Validate collector configuration."""
        # No special configuration required for JUnit collector
        pass
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported formats.
        
        Returns:
            List of supported file formats
        """
        return ['.xml']
    
    def collect_results(self, source_path: Path) -> List[TestResult]:
        """
        Collect test results from JUnit XML files.
        
        Args:
            source_path: Path to file or directory with results
            
        Returns:
            List of test results
        """
        results = []
        
        if source_path.is_file():
            if self.is_format_supported(source_path):
                results.extend(self._parse_junit_file(source_path))
            else:
                self.logger.warning(f"File format {source_path} is not supported")
        elif source_path.is_dir():
            # Search for all XML files in directory
            for xml_file in source_path.glob('**/*.xml'):
                if self._is_junit_file(xml_file):
                    results.extend(self._parse_junit_file(xml_file))
        else:
            raise ValueError(f"Unknown source type: {source_path}")
        
        return results
    
    def _is_junit_file(self, file_path: Path) -> bool:
        """
        Check if file is JUnit XML.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is JUnit XML
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check for testsuite or testsuites root element
            return root.tag in ['testsuite', 'testsuites']
        except ET.ParseError:
            return False
        except Exception:
            return False
    
    def _parse_junit_file(self, file_path: Path) -> List[TestResult]:
        """
        Parse JUnit XML file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of test results
        """
        results = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Process testsuites
            if root.tag == 'testsuites':
                for testsuite in root.findall('testsuite'):
                    results.extend(self._parse_testsuite(testsuite))
            elif root.tag == 'testsuite':
                results.extend(self._parse_testsuite(root))
            
            self.logger.info(f"Processed {len(results)} tests from file {file_path}")
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error for file {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error processing file {file_path}: {e}")
            raise
        
        return results
    
    def _parse_testsuite(self, testsuite_element: ET.Element) -> List[TestResult]:
        """
        Parse testsuite element.
        
        Args:
            testsuite_element: XML testsuite element
            
        Returns:
            List of test results
        """
        results = []
        
        # Get test suite information
        suite_name = testsuite_element.get('name', '')
        
        # Process each test
        for testcase in testsuite_element.findall('testcase'):
            result = self._parse_testcase(testcase, suite_name)
            if result:
                results.append(result)
        
        return results
    
    def _parse_testcase(self, testcase_element: ET.Element, suite_name: str) -> TestResult:
        """
        Parse testcase element.
        
        Args:
            testcase_element: XML testcase element
            suite_name: Test suite name
            
        Returns:
            Test result
        """
        # Extract basic test information
        test_name = testcase_element.get('name', '')
        classname = testcase_element.get('classname', '')
        duration = self._parse_duration(testcase_element.get('time', '0'))
        
        # Build full test name
        full_test_name = f"{classname}.{test_name}" if classname else test_name
        
        # Determine test status
        status = ResultStatus.PASSED
        error_message = None
        stacktrace = None
        
        # Check for failure, error, skipped elements
        failure_element = testcase_element.find('failure')
        error_element = testcase_element.find('error')
        skipped_element = testcase_element.find('skipped')
        
        if failure_element is not None:
            status = ResultStatus.FAILED
            error_message, stacktrace = self._extract_error_info(failure_element)
        elif error_element is not None:
            status = ResultStatus.FAILED
            error_message, stacktrace = self._extract_error_info(error_element)
        elif skipped_element is not None:
            status = ResultStatus.SKIPPED
            error_message = skipped_element.get('message', 'Test skipped')
        
        # Create test result
        return TestResult(
            test_id=full_test_name,
            test_name=self._clean_test_name(full_test_name),
            status=status,
            duration=duration,
            error_message=error_message,
            stacktrace=stacktrace,
            custom_fields={
                'suite_name': suite_name,
                'classname': classname,
                'raw_test_name': test_name
            }
        )
    
    def _extract_error_info(self, error_element: ET.Element) -> tuple[str, str]:
        """
        Extract error information from XML element.
        
        Args:
            error_element: XML element with error
            
        Returns:
            Tuple (error message, stack trace)
        """
        if error_element is None:
            return None, None
        
        error_message = error_element.get('message', '')
        stacktrace = (error_element.text or '').strip()
        
        return error_message, stacktrace 