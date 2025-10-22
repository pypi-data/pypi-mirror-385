"""
Collector for gathering results from Allure JSON files.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import logging

from ..core.base_collector import BaseCollector
from ..core.base_provider import TestResult, ResultStatus


class AllureCollector(BaseCollector):
    """Collector for Allure JSON files."""
    
    _version = '1.0.0'
    
    # Allure status mapping
    STATUS_MAPPING = {
        'passed': ResultStatus.PASSED,
        'failed': ResultStatus.FAILED,
        'skipped': ResultStatus.SKIPPED,
        'broken': ResultStatus.FAILED,
        'unknown': ResultStatus.NOT_RUN
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
        # No special configuration required for Allure collector
        pass
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported formats.
        
        Returns:
            List of supported file formats
        """
        return ['.json']
    
    def collect_results(self, source_path: Path) -> List[TestResult]:
        """
        Collect test results from Allure JSON files.
        
        Args:
            source_path: Path to file or directory with results
            
        Returns:
            List of test results
        """
        results = []
        
        if source_path.is_file():
            if self.is_format_supported(source_path):
                results.extend(self._parse_allure_file(source_path))
            else:
                self.logger.warning(f"File format {source_path} is not supported")
        elif source_path.is_dir():
            # Search for all JSON files in directory
            for json_file in source_path.glob('**/*.json'):
                if self._is_allure_file(json_file):
                    results.extend(self._parse_allure_file(json_file))
        else:
            raise ValueError(f"Unknown source type: {source_path}")
        
        return results
    
    def _is_allure_file(self, file_path: Path) -> bool:
        """
        Check if file is Allure JSON.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is Allure JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check for Allure-specific keys
            return (
                isinstance(data, dict) and 
                'uuid' in data and 
                'name' in data and 
                'status' in data
            )
        except (json.JSONDecodeError, FileNotFoundError):
            return False
        except Exception:
            return False
    
    def _parse_allure_file(self, file_path: Path) -> List[TestResult]:
        """
        Parse Allure JSON file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of test results
        """
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Allure can contain single test or array of tests
            if isinstance(data, list):
                for test_data in data:
                    result = self._parse_allure_test(test_data)
                    if result:
                        results.append(result)
            else:
                result = self._parse_allure_test(data)
                if result:
                    results.append(result)
            
            self.logger.info(f"Processed {len(results)} tests from file {file_path}")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error for file {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error processing file {file_path}: {e}")
            raise
        
        return results
    
    def _parse_allure_test(self, test_data: Dict[str, Any]) -> TestResult:
        """
        Parse data for single test from Allure.
        
        Args:
            test_data: Test data from Allure
            
        Returns:
            Test result
        """
        # Extract basic information
        test_id = test_data.get('uuid', '')
        test_name = test_data.get('name', '')
        full_name = test_data.get('fullName', test_name)
        
        # Determine status
        status_str = test_data.get('status', 'unknown').lower()
        status = self.STATUS_MAPPING.get(status_str, ResultStatus.NOT_RUN)
        
        # Extract execution time
        start_time = test_data.get('start', 0)
        stop_time = test_data.get('stop', 0)
        duration = (stop_time - start_time) / 1000.0 if stop_time > start_time else None
        
        # Extract error information
        error_message = None
        stacktrace = None
        
        status_details = test_data.get('statusDetails', {})
        if status_details:
            error_message = status_details.get('message', '')
            stacktrace = status_details.get('trace', '')
        
        # Extract attachments
        attachments = []
        for attachment in test_data.get('attachments', []):
            attachments.append(attachment.get('name', ''))
        
        # Extract labels and parameters
        labels = test_data.get('labels', [])
        parameters = test_data.get('parameters', [])
        
        # Build custom fields
        custom_fields = {
            'uuid': test_id,
            'full_name': full_name,
            'history_id': test_data.get('historyId', ''),
            'test_case_id': test_data.get('testCaseId', ''),
            'stage': test_data.get('stage', ''),
            'labels': {label.get('name', ''): label.get('value', '') for label in labels},
            'parameters': {param.get('name', ''): param.get('value', '') for param in parameters},
            'links': test_data.get('links', [])
        }
        
        return TestResult(
            test_id=test_id,
            test_name=self._clean_test_name(test_name),
            status=status,
            duration=duration,
            error_message=error_message,
            stacktrace=stacktrace,
            attachments=attachments if attachments else None,
            custom_fields=custom_fields
        ) 