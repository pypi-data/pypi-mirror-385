"""
Collector for gathering results from Cucumber JSON files.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import logging

from ..core.base_collector import BaseCollector
from ..core.base_provider import TestResult, ResultStatus


class CucumberCollector(BaseCollector):
    """Collector for Cucumber JSON files."""
    
    _version = '1.0.0'
    
    # Cucumber status mapping
    STATUS_MAPPING = {
        'passed': ResultStatus.PASSED,
        'failed': ResultStatus.FAILED,
        'skipped': ResultStatus.SKIPPED,
        'undefined': ResultStatus.NOT_RUN,
        'pending': ResultStatus.SKIPPED
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
        # No special configuration required for Cucumber collector
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
        Collect test results from Cucumber JSON files.
        
        Args:
            source_path: Path to file or directory with results
            
        Returns:
            List of test results
        """
        results = []
        
        if source_path.is_file():
            if self.is_format_supported(source_path):
                results.extend(self._parse_cucumber_file(source_path))
            else:
                self.logger.warning(f"File format {source_path} is not supported")
        elif source_path.is_dir():
            # Search for all JSON files in directory
            for json_file in source_path.glob('**/*.json'):
                if self._is_cucumber_file(json_file):
                    results.extend(self._parse_cucumber_file(json_file))
        else:
            raise ValueError(f"Unknown source type: {source_path}")
        
        return results
    
    def _is_cucumber_file(self, file_path: Path) -> bool:
        """
        Check if file is Cucumber JSON.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is Cucumber JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check for Cucumber-specific keys
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                return (
                    isinstance(first_item, dict) and 
                    'elements' in first_item and 
                    'name' in first_item
                )
            return False
        except (json.JSONDecodeError, FileNotFoundError):
            return False
        except Exception:
            return False
    
    def _parse_cucumber_file(self, file_path: Path) -> List[TestResult]:
        """
        Parse Cucumber JSON file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of test results
        """
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cucumber JSON contains array of features
            if isinstance(data, list):
                for feature in data:
                    results.extend(self._parse_cucumber_feature(feature))
            else:
                results.extend(self._parse_cucumber_feature(data))
            
            self.logger.info(f"Processed {len(results)} tests from file {file_path}")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error for file {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error processing file {file_path}: {e}")
            raise
        
        return results
    
    def _parse_cucumber_feature(self, feature_data: Dict[str, Any]) -> List[TestResult]:
        """
        Parse data for single feature from Cucumber.
        
        Args:
            feature_data: Feature data from Cucumber
            
        Returns:
            List of test results
        """
        results = []
        
        feature_name = feature_data.get('name', '')
        feature_id = feature_data.get('id', '')
        feature_uri = feature_data.get('uri', '')
        
        # Process each scenario
        for element in feature_data.get('elements', []):
            result = self._parse_cucumber_scenario(element, feature_name, feature_id, feature_uri)
            if result:
                results.append(result)
        
        return results
    
    def _parse_cucumber_scenario(
        self, 
        scenario_data: Dict[str, Any], 
        feature_name: str, 
        feature_id: str, 
        feature_uri: str
    ) -> TestResult:
        """
        Parse data for single scenario from Cucumber.
        
        Args:
            scenario_data: Scenario data from Cucumber
            feature_name: Feature name
            feature_id: Feature ID
            feature_uri: Feature URI
            
        Returns:
            Test result
        """
        # Extract basic information
        scenario_name = scenario_data.get('name', '')
        scenario_id = scenario_data.get('id', '')
        scenario_type = scenario_data.get('type', '')
        
        # Build full test name
        test_name = f"{feature_name}: {scenario_name}"
        test_id = f"{feature_id}.{scenario_id}"
        
        # Determine scenario status based on step statuses
        status = ResultStatus.PASSED
        duration = 0.0
        error_message = None
        stacktrace = None
        
        failed_steps = []
        
        # Process steps
        for step in scenario_data.get('steps', []):
            step_result = step.get('result', {})
            step_status = step_result.get('status', 'undefined')
            step_duration = step_result.get('duration', 0) / 1000000000.0  # Nanoseconds to seconds
            
            duration += step_duration
            
            # Determine overall status
            if step_status == 'failed':
                status = ResultStatus.FAILED
                error_message = step_result.get('error_message', '')
                
                # Collect information about failed step
                failed_steps.append({
                    'step_name': step.get('name', ''),
                    'step_keyword': step.get('keyword', ''),
                    'error_message': error_message
                })
            elif step_status == 'skipped' and status == ResultStatus.PASSED:
                status = ResultStatus.SKIPPED
            elif step_status == 'undefined' and status == ResultStatus.PASSED:
                status = ResultStatus.NOT_RUN
        
        # Build error message for failed steps
        if failed_steps:
            error_parts = []
            for step in failed_steps:
                error_parts.append(f"{step['step_keyword']}{step['step_name']}: {step['error_message']}")
            error_message = '\n'.join(error_parts)
        
        # Extract tags
        tags = [tag.get('name', '') for tag in scenario_data.get('tags', [])]
        
        # Build custom fields
        custom_fields = {
            'feature_name': feature_name,
            'feature_id': feature_id,
            'feature_uri': feature_uri,
            'scenario_id': scenario_id,
            'scenario_type': scenario_type,
            'tags': tags,
            'steps_count': len(scenario_data.get('steps', [])),
            'failed_steps': failed_steps
        }
        
        return TestResult(
            test_id=test_id,
            test_name=self._clean_test_name(test_name),
            status=status,
            duration=duration if duration > 0 else None,
            error_message=error_message,
            stacktrace=stacktrace,
            custom_fields=custom_fields
        ) 