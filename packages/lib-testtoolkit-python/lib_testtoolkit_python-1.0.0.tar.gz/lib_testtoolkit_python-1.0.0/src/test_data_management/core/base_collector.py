"""
Base interface for test result collectors.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path

from .base_provider import TestResult


class BaseCollector(ABC):
    """Base class for test result collectors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize collector.
        
        Args:
            config: Collector configuration
        """
        self.config = config or {}
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """Validate collector configuration."""
        pass
    
    @abstractmethod
    def collect_results(self, source_path: Path) -> List[TestResult]:
        """
        Collect test results from source.
        
        Args:
            source_path: Path to file or directory with results
            
        Returns:
            List of test results
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported formats.
        
        Returns:
            List of supported file formats
        """
        pass
    
    def is_format_supported(self, file_path: Path) -> bool:
        """
        Check if file format is supported.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if format is supported
        """
        supported_formats = self.get_supported_formats()
        return file_path.suffix.lower() in supported_formats
    
    def get_collector_name(self) -> str:
        """Get collector name."""
        return self.__class__.__name__
    
    def get_collector_version(self) -> str:
        """Get collector version."""
        return getattr(self, '_version', '1.0.0')
    
    def _parse_duration(self, duration_str: str) -> Optional[float]:
        """
        Parse duration string to seconds.
        
        Args:
            duration_str: Duration string
            
        Returns:
            Duration in seconds or None
        """
        try:
            return float(duration_str)
        except (ValueError, TypeError):
            return None
    
    def _clean_test_name(self, test_name: str) -> str:
        """
        Clean test name from extra characters.
        
        Args:
            test_name: Original test name
            
        Returns:
            Cleaned test name
        """
        return " ".join(test_name.split())
    
    def _extract_error_info(self, error_element) -> tuple[Optional[str], Optional[str]]:
        """
        Extracting information about the error.
        
        Args:
            error_element: Element containing error information
            
        Returns:
            Tuple (error message, stack trace)
        """
        error_message = None
        stacktrace = None
        
        if error_element is not None:
            error_message = error_element.get('message', '')
            stacktrace = error_element.text if error_element.text else ''
        
        return error_message, stacktrace 