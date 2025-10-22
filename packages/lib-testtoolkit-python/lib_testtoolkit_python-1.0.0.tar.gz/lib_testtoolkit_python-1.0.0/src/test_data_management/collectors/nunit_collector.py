"""
Collector for gathering results from NUnit XML files.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any
import logging

from ..core.base_collector import BaseCollector
from ..core.base_provider import TestResult, ResultStatus


class NUnitCollector(BaseCollector):
    """Collector for NUnit XML files."""
    
    _version = '1.0.0'
    
    # NUnit status mapping
    STATUS_MAPPING = {
        'passed': ResultStatus.PASSED,
        'failed': ResultStatus.FAILED,
        'skipped': ResultStatus.SKIPPED,
        'inconclusive': ResultStatus.SKIPPED,
        'ignored': ResultStatus.SKIPPED
    }
    
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
        # No special configuration required for NUnit collector
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
        Collect test results from NUnit XML files.
        
        Args:
            source_path: Path to file or directory with results
            
        Returns:
            List of test results
        """
        results = []
        
        if source_path.is_file():
            if self.is_format_supported(source_path):
                results.extend(self._parse_nunit_file(source_path))
            else:
                self.logger.warning(f"File format {source_path} is not supported")
        elif source_path.is_dir():
            # Search for all XML files in directory
            for xml_file in source_path.glob('**/*.xml'):
                if self._is_nunit_file(xml_file):
                    results.extend(self._parse_nunit_file(xml_file))
        else:
            raise ValueError(f"Unknown source type: {source_path}")
        
        return results
    
    def _is_nunit_file(self, file_path: Path) -> bool:
        """
        Check if file is NUnit XML.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is NUnit XML
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check for test-run or test-results root element
            return root.tag in ['test-run', 'test-results']
        except ET.ParseError:
            return False
        except Exception:
            return False
    
    def _parse_nunit_file(self, file_path: Path) -> List[TestResult]:
        """
        Parse NUnit XML file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of test results
        """
        results = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # NUnit can have different format versions
            if root.tag == 'test-run':
                # NUnit 3.x format
                results.extend(self._parse_nunit3_format(root))
            elif root.tag == 'test-results':
                # NUnit 2.x format
                results.extend(self._parse_nunit2_format(root))
            
            self.logger.info(f"Processed {len(results)} tests from file {file_path}")
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error for file {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error processing file {file_path}: {e}")
            raise
        
        return results
    
    def _parse_nunit3_format(self, root: ET.Element) -> List[TestResult]:
        """
        Parse NUnit 3.x format.
        
        Args:
            root: Root XML element
            
        Returns:
            List of test results
        """
        results = []
        
        # Find all test cases
        for test_case in root.findall('.//test-case'):
            result = self._parse_nunit3_test_case(test_case)
            if result:
                results.append(result)
        
        return results
    
    def _parse_nunit2_format(self, root: ET.Element) -> List[TestResult]:
        """
        Parse NUnit 2.x format.
        
        Args:
            root: Root XML element
            
        Returns:
            List of test results
        """
        results = []
        
        # Find all test cases
        for test_case in root.findall('.//test-case'):
            result = self._parse_nunit2_test_case(test_case)
            if result:
                results.append(result)
        
        return results
    
    def _parse_nunit3_test_case(self, test_case: ET.Element) -> TestResult:
        """
        Parse NUnit 3.x test case.
        
        Args:
            test_case: XML test-case element
            
        Returns:
            Test result
        """
        # Extract basic information
        test_name = test_case.get('name', '')
        full_name = test_case.get('fullname', test_name)
        result_attr = test_case.get('result', 'Inconclusive').lower()
        
        # Determine status
        status = self.STATUS_MAPPING.get(result_attr, ResultStatus.NOT_RUN)
        
        # Extract duration
        duration = self._parse_duration(test_case.get('duration', '0'))
        
        # Extract error information
        error_message = None
        stacktrace = None
        
        # Find failure or error elements
        failure_element = test_case.find('failure')
        if failure_element is not None:
            error_message = self._get_element_text(failure_element.find('message'))
            stacktrace = self._get_element_text(failure_element.find('stack-trace'))
        
        # Extract metadata
        categories = []
        properties = {}
        
        # Process properties
        properties_element = test_case.find('properties')
        if properties_element is not None:
            for prop in properties_element.findall('property'):
                prop_name = prop.get('name', '')
                prop_value = prop.get('value', '')
                properties[prop_name] = prop_value
                
                # Categories are often stored as properties
                if prop_name.lower() == 'category':
                    categories.append(prop_value)
        
        # Build custom fields
        custom_fields = {
            'full_name': full_name,
            'method_name': test_case.get('methodname', ''),
            'classname': test_case.get('classname', ''),
            'test_id': test_case.get('id', ''),
            'categories': categories,
            'properties': properties,
            'assertions': test_case.get('asserts', ''),
            'label': test_case.get('label', '')
        }
        
        return TestResult(
            test_id=full_name,
            test_name=self._clean_test_name(test_name),
            status=status,
            duration=duration,
            error_message=error_message,
            stacktrace=stacktrace,
            custom_fields=custom_fields
        )
    
    def _parse_nunit2_test_case(self, test_case: ET.Element) -> TestResult:
        """
        Parse NUnit 2.x test case.
        
        Args:
            test_case: XML test-case element
            
        Returns:
            Test result
        """
        # Extract basic information
        test_name = test_case.get('name', '')
        executed = test_case.get('executed', 'True').lower() == 'true'
        success = test_case.get('success', 'False').lower() == 'true'
        
        # Determine status
        if not executed:
            status = ResultStatus.SKIPPED
        elif success:
            status = ResultStatus.PASSED
        else:
            status = ResultStatus.FAILED
        
        # Extract duration
        duration = self._parse_duration(test_case.get('time', '0'))
        
        # Extract error information
        error_message = None
        stacktrace = None
        
        # Find failure or error elements
        failure_element = test_case.find('failure')
        if failure_element is not None:
            error_message = self._get_element_text(failure_element.find('message'))
            stacktrace = self._get_element_text(failure_element.find('stack-trace'))
        
        # Extract skip reason
        reason_element = test_case.find('reason')
        if reason_element is not None and status == ResultStatus.SKIPPED:
            reason_message = self._get_element_text(reason_element.find('message'))
            if reason_message:
                error_message = reason_message
        
        # Build custom fields
        custom_fields = {
            'asserts': test_case.get('asserts', ''),
            'description': test_case.get('description', ''),
            'executed': executed,
            'success': success
        }
        
        return TestResult(
            test_id=test_name,
            test_name=self._clean_test_name(test_name),
            status=status,
            duration=duration,
            error_message=error_message,
            stacktrace=stacktrace,
            custom_fields=custom_fields
        )
    
    def _get_element_text(self, element: ET.Element) -> str:
        """
        Get text from XML element.
        
        Args:
            element: XML element
            
        Returns:
            Element text or empty string
        """
        if element is not None:
            return element.text or ''
        return '' 