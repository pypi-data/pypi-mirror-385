"""
Base interface for test management system providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ResultStatus(Enum):
    """Test statuses."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    NOT_RUN = "not_run"


@dataclass
class TestResult:
    """Test result data structure."""
    test_id: str
    test_name: str
    status: ResultStatus
    duration: Optional[float] = None
    error_message: Optional[str] = None
    stacktrace: Optional[str] = None
    attachments: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class TestRun:
    """Test run data structure."""
    run_id: str
    name: str
    status: str
    created_on: Optional[str] = None
    description: Optional[str] = None
    test_count: Optional[int] = None


class BaseProvider(ABC):
    """Base class for test management system providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """Validate provider configuration."""
        pass
    
    @abstractmethod
    def create_test_run(self, run_name: str, **kwargs) -> str:
        """
        Create test run.
        
        Args:
            run_name: Run name
            **kwargs: Additional parameters
            
        Returns:
            Created run ID
        """
        pass
    
    @abstractmethod
    def upload_test_results(self, run_id: str, test_results: List[TestResult]) -> bool:
        """
        Upload test results.
        
        Args:
            run_id: Run ID
            test_results: List of test results
            
        Returns:
            True if upload successful
        """
        pass
    
    @abstractmethod
    def get_test_run_info(self, run_id: str) -> Optional[TestRun]:
        """
        Get test run information.
        
        Args:
            run_id: Run ID
            
        Returns:
            Run information or None if not found
        """
        pass 