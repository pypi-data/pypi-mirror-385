"""
Main manager for test data management.
"""

from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import logging

from .base_provider import BaseProvider, TestResult
from .base_collector import BaseCollector


class TestDataManager:
    """Manager for test data management."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize manager.
        
        Args:
            config: Manager configuration
        """
        self.config = config or {}
        self.providers: Dict[str, BaseProvider] = {}
        self.collectors: Dict[str, BaseCollector] = {}
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(
                getattr(logging, self.config.get('log_level', 'INFO'))
            )
    
    def register_provider(self, provider_name: str, provider: BaseProvider) -> None:
        """
        Register provider.
        
        Args:
            provider_name: Provider name
            provider: Provider instance
        """
        self.providers[provider_name] = provider
        self.logger.info(f"Registered provider: {provider_name}")
    
    def register_collector(self, collector_name: str, collector: BaseCollector) -> None:
        """
        Register collector.
        
        Args:
            collector_name: Collector name
            collector: Collector instance
        """
        self.collectors[collector_name] = collector
        self.logger.info(f"Registered collector: {collector_name}")
    
    def collect_results(self, collector_name: str, source_path: Path) -> List[TestResult]:
        """
        Collect test results using specified collector.
        
        Args:
            collector_name: Name of registered collector
            source_path: Path to test results
            
        Returns:
            List of test results
            
        Raises:
            ValueError: If collector not found
        """
        if collector_name not in self.collectors:
            raise ValueError(f"Collector '{collector_name}' not registered")
        
        collector = self.collectors[collector_name]
        self.logger.info(f"Collecting results from {source_path} using {collector_name}")
        
        results = collector.collect_results(source_path)
        self.logger.info(f"Collected {len(results)} test results")
        
        return results
    
    def upload_results(self, provider_name: str, run_id: str, test_results: List[TestResult]) -> bool:
        """
        Upload test results using specified provider.
        
        Args:
            provider_name: Name of registered provider
            run_id: Test run ID
            test_results: List of test results
            
        Returns:
            True if upload successful
            
        Raises:
            ValueError: If provider not found
        """
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not registered")
        
        provider = self.providers[provider_name]
        self.logger.info(f"Uploading {len(test_results)} results to {provider_name}")
        
        success = provider.upload_test_results(run_id, test_results)
        
        if success:
            self.logger.info("Results uploaded successfully")
        else:
            self.logger.error("Failed to upload results")
        
        return success
    
    def create_test_run(self, provider_name: str, run_name: str, **kwargs) -> str:
        """
        Create test run using specified provider.
        
        Args:
            provider_name: Name of registered provider
            run_name: Name of test run
            **kwargs: Additional parameters
            
        Returns:
            Created run ID
            
        Raises:
            ValueError: If provider not found
        """
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not registered")
        
        provider = self.providers[provider_name]
        self.logger.info(f"Creating test run '{run_name}' in {provider_name}")
        
        run_id = provider.create_test_run(run_name, **kwargs)
        self.logger.info(f"Created test run with ID: {run_id}")
        
        return run_id
    
    def get_registered_providers(self) -> List[str]:
        """
        Get list of registered providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
    
    def get_registered_collectors(self) -> List[str]:
        """
        Get list of registered collectors.
        
        Returns:
            List of collector names
        """
        return list(self.collectors.keys())
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of manager status.
        
        Returns:
            Status summary dictionary
        """
        return {
            'providers': len(self.providers),
            'collectors': len(self.collectors),
            'provider_list': self.get_registered_providers(),
            'collector_list': self.get_registered_collectors()
        } 