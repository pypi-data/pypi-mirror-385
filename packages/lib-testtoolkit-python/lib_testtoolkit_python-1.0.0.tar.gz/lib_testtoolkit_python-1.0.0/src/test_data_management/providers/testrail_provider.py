"""
Provider for TestRail API integration.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..core.base_provider import BaseProvider, TestResult, ResultStatus, TestRun


class TestRailProvider(BaseProvider):
    """Provider for TestRail integration."""
    
    _version = '1.0.0'
    
    # Status mapping between internal and TestRail
    STATUS_MAPPING = {
        ResultStatus.PASSED: 1,    # Passed
        ResultStatus.FAILED: 5,    # Failed
        ResultStatus.SKIPPED: 3,   # Untested
        ResultStatus.BLOCKED: 2,   # Blocked
        ResultStatus.NOT_RUN: 3    # Untested
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TestRail provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize HTTP session
        self.session = requests.Session()
        self.session.auth = (
            self.config['username'], 
            self.config['password']
        )
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'TestRailProvider/{self._version}'
        })
    
    def validate_config(self) -> None:
        """Validate provider configuration."""
        required_fields = ['url', 'username', 'password', 'project_id']
        
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required configuration field: {field}")
        
        # Check URL correctness
        if not self.config['url'].startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        # Add /index.php?/api/v2/ to URL if missing
        if not self.config['url'].endswith('/index.php?/api/v2/'):
            self.config['url'] = self.config['url'].rstrip('/') + '/index.php?/api/v2/'
    
    def create_test_run(self, run_name: str, **kwargs) -> str:
        """
        Create test run in TestRail.
        
        Args:
            run_name: Run name
            **kwargs: Additional parameters
            
        Returns:
            Created run ID
        """
        url = f"{self.config['url']}add_run/{self.config['project_id']}"
        
        # Prepare data for run creation
        run_data = {
            'name': run_name,
            'description': kwargs.get('description', ''),
            'milestone_id': kwargs.get('milestone_id'),
            'suite_id': kwargs.get('suite_id'),
            'assignedto_id': kwargs.get('assignedto_id'),
            'include_all': kwargs.get('include_all', True)
        }
        
        # Remove None values
        run_data = {k: v for k, v in run_data.items() if v is not None}
        
        self.logger.info(f"Creating test run in TestRail: {run_name}")
        
        try:
            response = self.session.post(url, json=run_data)
            response.raise_for_status()
            
            result = response.json()
            run_id = str(result['id'])
            
            self.logger.info(f"Created run with ID: {run_id}")
            return run_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating test run: {e}")
            raise
        except KeyError as e:
            self.logger.error(f"Unexpected response from TestRail API: {e}")
            raise
    
    def upload_test_results(self, run_id: str, test_results: List[TestResult]) -> bool:
        """
        Upload test results to TestRail.
        
        Args:
            run_id: Run ID
            test_results: List of test results
            
        Returns:
            True if upload successful
        """
        url = f"{self.config['url']}add_results_for_run/{run_id}"
        
        # Prepare results for TestRail
        results_data = []
        for test_result in test_results:
            result_data = self._convert_test_result(test_result)
            if result_data:
                results_data.append(result_data)
        
        if not results_data:
            self.logger.warning("No results to upload")
            return False
        
        # Split results into batches for large runs
        batch_size = self.config.get('batch_size', 100)
        batches = [results_data[i:i + batch_size] for i in range(0, len(results_data), batch_size)]
        
        self.logger.info(f"Uploading {len(results_data)} results in {len(batches)} batches")
        
        try:
            for i, batch in enumerate(batches):
                self.logger.info(f"Uploading batch {i + 1}/{len(batches)}")
                
                response = self.session.post(url, json={'results': batch})
                response.raise_for_status()
                
                self.logger.info(f"Batch {i + 1} uploaded successfully")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error uploading results: {e}")
            return False
    
    def get_test_run_info(self, run_id: str) -> Optional[TestRun]:
        """
        Get test run information.
        
        Args:
            run_id: Run ID
            
        Returns:
            Run information or None if not found
        """
        url = f"{self.config['url']}get_run/{run_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            run_data = response.json()
            
            # Get test results
            results_url = f"{self.config['url']}get_results_for_run/{run_id}"
            results_response = self.session.get(results_url)
            results_response.raise_for_status()
            
            results_data = results_response.json()
            
            # Convert results
            test_results = []
            for result in results_data:
                test_result = self._convert_from_testrail_result(result)
                if test_result:
                    test_results.append(test_result)
            
            return TestRun(
                run_id=str(run_data['id']),
                run_name=run_data['name'],
                test_results=test_results,
                start_time=self._convert_timestamp(run_data.get('created_on')),
                end_time=self._convert_timestamp(run_data.get('completed_on')),
                custom_fields={
                    'description': run_data.get('description', ''),
                    'milestone_id': run_data.get('milestone_id'),
                    'suite_id': run_data.get('suite_id'),
                    'is_completed': run_data.get('is_completed', False)
                }
            )
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting test run information: {e}")
            return None
        except KeyError as e:
            self.logger.error(f"Unexpected response from TestRail API: {e}")
            return None
    
    def close_test_run(self, run_id: str) -> bool:
        """
        Close test run.
        
        Args:
            run_id: Run ID
            
        Returns:
            True if close successful
        """
        url = f"{self.config['url']}close_run/{run_id}"
        
        try:
            response = self.session.post(url)
            response.raise_for_status()
            
            self.logger.info(f"Run {run_id} closed successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error closing test run: {e}")
            return False
    
    def _convert_test_result(self, test_result: TestResult) -> Optional[Dict[str, Any]]:
        """
        Convert test result to TestRail format.
        
        Args:
            test_result: Test result
            
        Returns:
            Dictionary with TestRail data or None
        """
        # Get test ID in TestRail
        test_id = self._get_test_id_from_name(test_result.test_name)
        if not test_id:
            self.logger.warning(f"Test ID not found for: {test_result.test_name}")
            return None
        
        # Status mapping
        status_id = self.STATUS_MAPPING.get(test_result.status, 3)  # Default to Untested
        
        # Build comment
        comment_parts = []
        if test_result.error_message:
            comment_parts.append(f"Error: {test_result.error_message}")
        if test_result.stacktrace:
            comment_parts.append(f"Stack trace:\n{test_result.stacktrace}")
        
        result_data = {
            'test_id': test_id,
            'status_id': status_id,
            'comment': '\n\n'.join(comment_parts) if comment_parts else None,
            'elapsed': self._convert_duration(test_result.duration)
        }
        
        # Add custom fields
        if test_result.custom_fields:
            for key, value in test_result.custom_fields.items():
                if key.startswith('custom_'):
                    result_data[key] = value
        
        return result_data
    
    def _get_test_id_from_name(self, test_name: str) -> Optional[int]:
        """
        Get test ID by name.
        
        Args:
            test_name: Test name
            
        Returns:
            Test ID or None
        """
        # This is a simplified implementation
        # In a real project, you need to cache name-ID mappings
        # or use other identification methods
        
        # Can use test search or cache
        # For now, returning None for demonstration
        return None
    
    def _convert_from_testrail_result(self, result_data: Dict[str, Any]) -> Optional[TestResult]:
        """
        Convert result from TestRail format.
        
        Args:
            result_data: Result data from TestRail
            
        Returns:
            TestResult object or None
        """
        # Reverse status mapping
        status_mapping = {v: k for k, v in self.STATUS_MAPPING.items()}
        status = status_mapping.get(result_data.get('status_id'), ResultStatus.NOT_RUN)
        
        return TestResult(
            test_id=str(result_data.get('test_id', '')),
            test_name=result_data.get('test_name', ''),
            status=status,
            duration=self._parse_duration(result_data.get('elapsed')),
            error_message=result_data.get('comment'),
            custom_fields={
                'testrail_result_id': result_data.get('id'),
                'created_on': result_data.get('created_on'),
                'created_by': result_data.get('created_by')
            }
        )
    
    def _convert_duration(self, duration: Optional[float]) -> Optional[str]:
        """
        Convert duration to TestRail format.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            String with duration or None
        """
        if duration is None:
            return None
        
        # TestRail uses "1m 30s" format
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _convert_timestamp(self, timestamp: Optional[int]) -> Optional[str]:
        """
        Convert timestamp to string.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            String with date and time or None
        """
        if timestamp is None:
            return None
        
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.isoformat()
        except (ValueError, OSError):
            return None 