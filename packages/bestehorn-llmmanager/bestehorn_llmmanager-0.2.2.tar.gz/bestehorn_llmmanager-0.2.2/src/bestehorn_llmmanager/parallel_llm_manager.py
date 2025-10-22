"""
ParallelLLMManager - Main class for parallel processing of AWS Bedrock Converse API requests.

Provides parallel execution of multiple requests across multiple regions with intelligent
load balancing, error handling, and comprehensive response aggregation.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union, cast

from .bedrock.distributors.region_distribution_manager import RegionDistributionManager
from .bedrock.exceptions.parallel_exceptions import (
    ParallelConfigurationError,
    ParallelExecutionError,
    ParallelProcessingError,
)
from .bedrock.executors.thread_parallel_executor import ThreadParallelExecutor
from .bedrock.models.bedrock_response import BedrockResponse
from .bedrock.models.llm_manager_constants import LLMManagerConfig
from .bedrock.models.llm_manager_structures import AuthConfig, ResponseValidationConfig, RetryConfig
from .bedrock.models.parallel_constants import ParallelConfig, ParallelLogMessages
from .bedrock.models.parallel_structures import (
    BedrockConverseRequest,
    FailureHandlingStrategy,
    ParallelExecutionStats,
    ParallelProcessingConfig,
    ParallelResponse,
    RegionAssignment,
)
from .bedrock.validators.request_validator import RequestValidator
from .llm_manager import LLMManager


class ParallelLLMManager:
    """
    Main class for parallel processing of LLM requests across multiple regions.

    Extends the functionality of LLMManager to support parallel execution of multiple
    requests with intelligent region distribution, load balancing, and comprehensive
    error handling.

    Example:
        Basic parallel processing:
        >>> parallel_manager = ParallelLLMManager(
        ...     models=["Claude 3 Haiku", "Claude 3 Sonnet"],
        ...     regions=["us-east-1", "us-west-2", "eu-west-1"]
        ... )
        >>> requests = [
        ...     BedrockConverseRequest(messages=[{"role": "user", "content": [{"text": "Hello"}]}]),
        ...     BedrockConverseRequest(messages=[{"role": "user", "content": [{"text": "How are you?"}]}])
        ... ]
        >>> response = parallel_manager.converse_parallel(
        ...     requests=requests,
        ...     target_regions_per_request=2
        ... )
        >>> print(f"Success rate: {response.get_success_rate():.1f}%")

        With custom configuration:
        >>> config = ParallelProcessingConfig(
        ...     max_concurrent_requests=10,
        ...     request_timeout_seconds=120,
        ...     failure_handling_strategy=FailureHandlingStrategy.STOP_ON_THRESHOLD
        ... )
        >>> parallel_manager = ParallelLLMManager(
        ...     models=["Claude 3 Haiku"],
        ...     regions=["us-east-1", "us-west-2"],
        ...     parallel_config=config
        ... )
    """

    def __init__(
        self,
        models: List[str],
        regions: List[str],
        auth_config: Optional[AuthConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        parallel_config: Optional[ParallelProcessingConfig] = None,
        default_inference_config: Optional[Dict] = None,
        timeout: int = ParallelConfig.DEFAULT_REQUEST_TIMEOUT_SECONDS,
        log_level: Union[int, str] = LLMManagerConfig.DEFAULT_LOG_LEVEL,
    ) -> None:
        """
        Initialize the Parallel LLM Manager.

        Args:
            models: List of model names/IDs to use for requests
            regions: List of AWS regions to use for parallel processing
            auth_config: Authentication configuration. If None, uses auto-detection
            retry_config: Retry behavior configuration. If None, uses defaults
            parallel_config: Parallel processing configuration. If None, uses defaults
            default_inference_config: Default inference parameters to apply
            timeout: Request timeout in seconds (applies to individual requests)
            log_level: Logging level (e.g., logging.WARNING, "INFO", 20). Defaults to logging.WARNING

        Raises:
            ParallelConfigurationError: If configuration is invalid
        """
        self._logger = logging.getLogger(__name__)

        # Validate initialization parameters
        self._validate_initialization_params(models=models, regions=regions)

        # Store configuration
        self._models = models.copy()
        self._regions = regions.copy()
        self._retry_config = retry_config
        self._parallel_config = parallel_config or ParallelProcessingConfig()

        # Initialize core LLMManager for single request execution
        self._llm_manager = LLMManager(
            models=models,
            regions=regions,
            auth_config=auth_config,
            retry_config=retry_config,
            default_inference_config=default_inference_config,
            timeout=timeout,
            log_level=log_level,
        )

        # Initialize parallel processing components
        self._request_validator = RequestValidator()
        self._region_distributor = RegionDistributionManager(
            load_balancing_strategy=self._parallel_config.load_balancing_strategy
        )
        self._parallel_executor = ThreadParallelExecutor(config=self._parallel_config)

        self._logger.info(
            ParallelLogMessages.PARALLEL_MANAGER_INITIALIZED.format(
                model_count=len(self._models),
                region_count=len(self._regions),
                max_concurrent=self._parallel_config.max_concurrent_requests,
            )
        )

    def _calculate_optimal_target_regions(self) -> int:
        """
        Calculate optimal target_regions_per_request based on configuration and available regions.

        Returns:
            Optimal number of target regions per request
        """
        available_regions_count = len(self._regions)
        max_concurrent = self._parallel_config.max_concurrent_requests

        # Use the smaller of max_concurrent_requests and available regions
        optimal_target = min(max_concurrent, available_regions_count)

        # Ensure at least 1 region is used
        return max(1, optimal_target)

    def _log_target_regions_adjustment(self, adjusted_value: int) -> None:
        """
        Log warning message when target_regions_per_request is auto-adjusted.

        Args:
            adjusted_value: The auto-calculated target regions value
        """
        available_regions_count = len(self._regions)
        max_concurrent = self._parallel_config.max_concurrent_requests

        if adjusted_value == available_regions_count and available_regions_count < max_concurrent:
            # Capped by region availability
            message = ParallelLogMessages.TARGET_REGIONS_CAPPED_BY_AVAILABILITY.format(
                adjusted_value=adjusted_value, available_regions=available_regions_count
            )
        elif adjusted_value == max_concurrent and max_concurrent < available_regions_count:
            # Capped by concurrency limit
            message = ParallelLogMessages.TARGET_REGIONS_CAPPED_BY_CONCURRENCY.format(
                adjusted_value=adjusted_value, max_concurrent=max_concurrent
            )
        else:
            # General auto-adjustment message
            message = ParallelLogMessages.TARGET_REGIONS_AUTO_ADJUSTED.format(
                adjusted_value=adjusted_value,
                max_concurrent=max_concurrent,
                available_regions=available_regions_count,
            )

        self._logger.warning(message)

    def _validate_initialization_params(self, models: List[str], regions: List[str]) -> None:
        """
        Validate initialization parameters.

        Args:
            models: List of model names to validate
            regions: List of region names to validate

        Raises:
            ParallelConfigurationError: If parameters are invalid
        """
        if not models:
            raise ParallelConfigurationError(
                message="No models specified for ParallelLLMManager",
                invalid_parameter="models",
                provided_value=len(models),
            )

        if not regions:
            raise ParallelConfigurationError(
                message="No regions specified for ParallelLLMManager",
                invalid_parameter="regions",
                provided_value=len(regions),
            )

        if len(regions) < 2:
            self._logger.warning(
                "Only one region specified. Parallel processing benefits from multiple regions."
            )

    def converse_parallel(
        self,
        requests: List[BedrockConverseRequest],
        target_regions_per_request: Optional[int] = None,
        response_validation_config: Optional[ResponseValidationConfig] = None,
    ) -> ParallelResponse:
        """
        Execute multiple conversation requests in parallel across regions.

        Args:
            requests: List of BedrockConverseRequest objects to process
            target_regions_per_request: Target number of regions to assign per request
            response_validation_config: Optional validation configuration for responses

        Returns:
            ParallelResponse with aggregated results

        Raises:
            ParallelProcessingError: If parallel processing fails
            ParallelConfigurationError: If configuration is invalid
        """
        execution_start = datetime.now()

        try:
            # Step 1: Validate requests
            self._request_validator.validate_batch_requests(requests=requests)

            # Step 1.5: Auto-calculate target_regions_per_request if not provided
            calculated_target_regions = target_regions_per_request
            if calculated_target_regions is None:
                calculated_target_regions = self._calculate_optimal_target_regions()
                self._log_target_regions_adjustment(calculated_target_regions)

            # Step 2: Distribute requests across regions
            assignments = self._region_distributor.distribute_requests(
                requests=requests,
                available_regions=self._regions,
                target_regions_per_request=calculated_target_regions,
            )

            # Step 3: Create request map for execution
            request_map = {
                request.request_id: request for request in requests if request.request_id
            }

            # Step 4: Execute requests in parallel with retry support
            execution_responses = self._parallel_executor.execute_requests_parallel(
                assignments=assignments,
                request_map=request_map,
                execute_single_request_func=self._create_single_request_executor(
                    response_validation_config=response_validation_config
                ),
                retry_config=self._retry_config,
                available_regions=self._regions,
            )

            # Step 5: Calculate execution statistics
            total_duration = (datetime.now() - execution_start).total_seconds() * 1000
            execution_stats = self._calculate_execution_stats(
                responses=execution_responses,
                assignments=assignments,
                total_duration_ms=total_duration,
            )

            # Step 6: Create aggregated response with original requests
            parallel_response = self._create_parallel_response(
                responses=execution_responses,
                execution_stats=execution_stats,
                total_duration_ms=total_duration,
                original_requests=request_map,
            )

            # Step 7: Handle failure strategies
            self._handle_failure_strategy(parallel_response=parallel_response)

            return parallel_response

        except Exception as e:
            if isinstance(e, (ParallelProcessingError, ParallelConfigurationError)):
                raise
            else:
                total_duration = (datetime.now() - execution_start).total_seconds() * 1000
                raise ParallelProcessingError(
                    message=f"Parallel processing failed: {str(e)}",
                    details={"total_duration_ms": total_duration},
                ) from e

    def _create_single_request_executor(
        self, response_validation_config: Optional[ResponseValidationConfig] = None
    ) -> Callable[[Dict[str, Any]], BedrockResponse]:
        """
        Create a function to execute a single request through LLMManager.

        Args:
            response_validation_config: Optional response validation configuration

        Returns:
            Function that can execute a single request
        """

        def execute_single_request(converse_args: Dict) -> "BedrockResponse":
            """Execute a single request using the underlying LLMManager."""
            return self._llm_manager.converse(
                response_validation_config=response_validation_config, **converse_args
            )

        return execute_single_request

    def _calculate_execution_stats(
        self,
        responses: Dict[str, "BedrockResponse"],
        assignments: List["RegionAssignment"],
        total_duration_ms: float,
    ) -> ParallelExecutionStats:
        """
        Calculate execution statistics from responses.

        Args:
            responses: Dictionary of responses
            assignments: List of region assignments
            total_duration_ms: Total execution duration

        Returns:
            ParallelExecutionStats object
        """
        successful_responses = [r for r in responses.values() if r.success]
        failed_responses = [r for r in responses.values() if not r.success]

        # Calculate duration statistics
        successful_durations = []
        for response in successful_responses:
            if response.total_duration_ms is not None:
                successful_durations.append(response.total_duration_ms)

        if successful_durations:
            avg_duration = sum(successful_durations) / len(successful_durations)
            max_duration = max(successful_durations)
            min_duration = min(successful_durations)
        else:
            avg_duration = max_duration = min_duration = 0.0

        # Calculate region distribution
        region_distribution: Dict[str, int] = {}
        for assignment in assignments:
            for region in assignment.assigned_regions:
                region_distribution[region] = region_distribution.get(region, 0) + 1

        # Calculate peak concurrent executions
        concurrent_executions = min(len(responses), self._parallel_config.max_concurrent_requests)

        return ParallelExecutionStats(
            total_requests=len(responses),
            successful_requests=len(successful_responses),
            failed_requests_count=len(failed_responses),
            average_request_duration_ms=avg_duration,
            max_request_duration_ms=max_duration,
            min_request_duration_ms=min_duration,
            concurrent_executions=concurrent_executions,
            region_distribution=region_distribution,
        )

    def _create_parallel_response(
        self,
        responses: Dict[str, "BedrockResponse"],
        execution_stats: ParallelExecutionStats,
        total_duration_ms: float,
        original_requests: Dict[str, BedrockConverseRequest],
    ) -> ParallelResponse:
        """
        Create aggregated parallel response with categorized request IDs.

        Args:
            responses: Dictionary of individual responses
            execution_stats: Execution statistics
            total_duration_ms: Total execution duration
            original_requests: Dictionary of original requests for retry support

        Returns:
            ParallelResponse object with categorized request IDs
        """
        successful_responses = {
            req_id: response for req_id, response in responses.items() if response.success
        }
        failed_requests = [req_id for req_id, response in responses.items() if not response.success]

        # Categorize request IDs by outcome
        successful_request_ids = list(successful_responses.keys())
        failed_request_ids = []
        timed_out_request_ids = []

        for req_id, response in responses.items():
            if not response.success:
                # Check if this is a timeout by examining warnings
                is_timeout = any(
                    "timed out" in warning.lower() for warning in response.get_warnings()
                )
                if is_timeout:
                    timed_out_request_ids.append(req_id)
                else:
                    failed_request_ids.append(req_id)

        # Collect warnings from all responses
        all_warnings = []
        for response in responses.values():
            all_warnings.extend(response.get_warnings())

        # Determine overall success
        overall_success = len(successful_responses) > 0

        # Apply failure handling strategy for overall success determination
        if (
            self._parallel_config.failure_handling_strategy
            == FailureHandlingStrategy.STOP_ON_FIRST_FAILURE
        ):
            overall_success = len(failed_requests) == 0
        elif (
            self._parallel_config.failure_handling_strategy
            == FailureHandlingStrategy.STOP_ON_THRESHOLD
        ):
            failure_rate = len(failed_requests) / len(responses) if responses else 0
            overall_success = failure_rate <= self._parallel_config.failure_threshold

        return ParallelResponse(
            success=overall_success,
            request_responses=responses,
            total_duration_ms=total_duration_ms,
            parallel_execution_stats=execution_stats,
            warnings=all_warnings,
            failed_requests=failed_requests,
            successful_request_ids=successful_request_ids,
            failed_request_ids=failed_request_ids,
            timed_out_request_ids=timed_out_request_ids,
            original_requests=original_requests,
        )

    def _handle_failure_strategy(self, parallel_response: ParallelResponse) -> None:
        """
        Handle failure strategy enforcement.

        Args:
            parallel_response: ParallelResponse to evaluate

        Raises:
            ParallelExecutionError: If failure strategy conditions are met
        """
        if not parallel_response.success:
            if (
                self._parallel_config.failure_handling_strategy
                == FailureHandlingStrategy.STOP_ON_FIRST_FAILURE
            ):
                if parallel_response.failed_requests:
                    raise ParallelExecutionError(
                        message="Parallel execution stopped due to first failure",
                        failed_requests=parallel_response.failed_requests,
                        total_requests=len(parallel_response.request_responses),
                    )
            elif (
                self._parallel_config.failure_handling_strategy
                == FailureHandlingStrategy.STOP_ON_THRESHOLD
            ):
                failure_rate = len(parallel_response.failed_requests) / len(
                    parallel_response.request_responses
                )
                if failure_rate > self._parallel_config.failure_threshold:
                    raise ParallelExecutionError(
                        message=f"Parallel execution stopped due to failure rate {failure_rate:.1%} exceeding threshold {self._parallel_config.failure_threshold:.1%}",
                        failed_requests=parallel_response.failed_requests,
                        total_requests=len(parallel_response.request_responses),
                    )

    def retry_failed_requests(
        self,
        previous_response: ParallelResponse,
        filter_func: Optional[Callable[[str, BedrockResponse], bool]] = None,
        target_regions_per_request: Optional[int] = None,
        response_validation_config: Optional[ResponseValidationConfig] = None,
    ) -> ParallelResponse:
        """
        Retry failed requests from a previous parallel execution.

        This method allows selective retry of failed requests with optional filtering.
        The retry results are merged with previous successful results to create a
        comprehensive response.

        Args:
            previous_response: Previous ParallelResponse containing failed requests
            filter_func: Optional function to filter which failed requests to retry.
                        Signature: func(request_id: str, response: BedrockResponse) -> bool
                        Return True to retry the request, False to skip it.
            target_regions_per_request: Target number of regions for retry attempts
            response_validation_config: Optional validation configuration for responses

        Returns:
            ParallelResponse with merged results (previous successful + retry results)

        Raises:
            ParallelProcessingError: If retry execution fails
            ValueError: If previous_response has no failed requests to retry

        Example:
            >>> # Retry only throttled requests
            >>> def retry_throttled(req_id, response):
            ...     return any("throttl" in w.lower() for w in response.get_warnings())
            >>> retry_response = manager.retry_failed_requests(
            ...     previous_response=initial_response,
            ...     filter_func=retry_throttled
            ... )
        """
        # Validate that there are requests to retry
        if not previous_response.failed_request_ids and not previous_response.timed_out_request_ids:
            raise ValueError("No failed or timed-out requests to retry in previous response")

        # Build list of requests to retry
        retry_requests = self._build_retry_requests(
            previous_response=previous_response,
            filter_func=filter_func,
        )

        if not retry_requests:
            self._logger.warning("No requests selected for retry after applying filter")
            return previous_response

        self._logger.info(f"Retrying {len(retry_requests)} failed requests")

        # Execute retry
        retry_response = self.converse_parallel(
            requests=retry_requests,
            target_regions_per_request=target_regions_per_request,
            response_validation_config=response_validation_config,
        )

        # Merge retry results with previous results
        merged_response = self._merge_responses(
            previous_response=previous_response,
            retry_response=retry_response,
        )

        return merged_response

    def _build_retry_requests(
        self,
        previous_response: ParallelResponse,
        filter_func: Optional[Callable[[str, BedrockResponse], bool]] = None,
    ) -> List[BedrockConverseRequest]:
        """
        Build list of requests to retry from previous response.

        Args:
            previous_response: Previous ParallelResponse with failed requests
            filter_func: Optional filter function to select which requests to retry

        Returns:
            List of BedrockConverseRequest objects to retry
        """
        retry_requests = []

        # Get all failed and timed-out request IDs
        failed_ids = set(
            previous_response.failed_request_ids + previous_response.timed_out_request_ids
        )

        for req_id in failed_ids:
            # Get the original request
            original_request = previous_response.original_requests.get(req_id)
            if original_request is None:
                self._logger.warning(f"Original request not found for {req_id}, skipping retry")
                continue

            # Get the failed response for filtering
            failed_response = previous_response.request_responses.get(req_id)
            if failed_response is None:
                self._logger.warning(f"Response not found for {req_id}, skipping retry")
                continue

            # Apply filter if provided
            if filter_func is not None:
                try:
                    should_retry = filter_func(req_id, failed_response)
                    if not should_retry:
                        self._logger.debug(f"Request {req_id} filtered out from retry")
                        continue
                except Exception as e:
                    self._logger.error(f"Error in filter function for {req_id}: {e}, skipping")
                    continue

            # Reset retry count for clean retry attempt
            original_request.retry_count = 0
            original_request.failure_history.clear()

            retry_requests.append(original_request)

        return retry_requests

    def _merge_responses(
        self,
        previous_response: ParallelResponse,
        retry_response: ParallelResponse,
    ) -> ParallelResponse:
        """
        Merge retry response with previous response.

        Combines successful responses from both previous and retry executions,
        keeping only the latest attempt for each request ID.

        Args:
            previous_response: Original ParallelResponse
            retry_response: ParallelResponse from retry execution

        Returns:
            Merged ParallelResponse with combined results
        """
        # Start with previous successful responses
        merged_responses = {}
        for req_id, response in previous_response.request_responses.items():
            if response.success:
                merged_responses[req_id] = response

        # Override/add responses from retry
        for req_id, response in retry_response.request_responses.items():
            merged_responses[req_id] = response

        # Recalculate categorized lists
        successful_request_ids = []
        failed_request_ids = []
        timed_out_request_ids = []

        for req_id, response in merged_responses.items():
            if response.success:
                successful_request_ids.append(req_id)
            else:
                # Check if timeout
                is_timeout = any(
                    "timed out" in warning.lower() for warning in response.get_warnings()
                )
                if is_timeout:
                    timed_out_request_ids.append(req_id)
                else:
                    failed_request_ids.append(req_id)

        # Combine warnings
        all_warnings = []
        for response in merged_responses.values():
            all_warnings.extend(response.get_warnings())

        # Calculate merged statistics
        total_duration_ms = previous_response.total_duration_ms + retry_response.total_duration_ms

        # Recalculate execution stats
        successful_count = len(successful_request_ids)
        failed_count = len(failed_request_ids) + len(timed_out_request_ids)

        # Calculate duration stats from merged responses
        successful_durations = []
        for response in merged_responses.values():
            if response.success and response.total_duration_ms is not None:
                successful_durations.append(response.total_duration_ms)

        if successful_durations:
            avg_duration = sum(successful_durations) / len(successful_durations)
            max_duration = max(successful_durations)
            min_duration = min(successful_durations)
        else:
            avg_duration = max_duration = min_duration = 0.0

        # Merge region distributions
        merged_region_dist: Dict[str, int] = {}
        if previous_response.parallel_execution_stats:
            merged_region_dist = (
                previous_response.parallel_execution_stats.region_distribution.copy()
            )
        if retry_response.parallel_execution_stats:
            for (
                region,
                count,
            ) in retry_response.parallel_execution_stats.region_distribution.items():
                merged_region_dist[region] = merged_region_dist.get(region, 0) + count

        merged_stats = ParallelExecutionStats(
            total_requests=len(merged_responses),
            successful_requests=successful_count,
            failed_requests_count=failed_count,
            average_request_duration_ms=avg_duration,
            max_request_duration_ms=max_duration,
            min_request_duration_ms=min_duration,
            concurrent_executions=max(
                (
                    previous_response.parallel_execution_stats.concurrent_executions
                    if previous_response.parallel_execution_stats
                    else 0
                ),
                (
                    retry_response.parallel_execution_stats.concurrent_executions
                    if retry_response.parallel_execution_stats
                    else 0
                ),
            ),
            region_distribution=merged_region_dist,
        )

        # Determine overall success
        overall_success = successful_count > 0
        if (
            self._parallel_config.failure_handling_strategy
            == FailureHandlingStrategy.STOP_ON_FIRST_FAILURE
        ):
            overall_success = failed_count == 0
        elif (
            self._parallel_config.failure_handling_strategy
            == FailureHandlingStrategy.STOP_ON_THRESHOLD
        ):
            failure_rate = failed_count / len(merged_responses) if merged_responses else 0
            overall_success = failure_rate <= self._parallel_config.failure_threshold

        # Preserve original requests from previous response
        original_requests = previous_response.original_requests.copy()

        return ParallelResponse(
            success=overall_success,
            request_responses=merged_responses,
            total_duration_ms=total_duration_ms,
            parallel_execution_stats=merged_stats,
            warnings=all_warnings,
            failed_requests=failed_request_ids + timed_out_request_ids,
            successful_request_ids=successful_request_ids,
            failed_request_ids=failed_request_ids,
            timed_out_request_ids=timed_out_request_ids,
            original_requests=original_requests,
        )

    def converse_with_request(self, request: BedrockConverseRequest) -> "BedrockResponse":
        """
        Execute a single BedrockConverseRequest using the underlying LLMManager.

        This method provides compatibility with the new request structure while
        using the existing single-request processing logic.

        Args:
            request: BedrockConverseRequest to execute

        Returns:
            BedrockResponse with the result
        """
        # Convert request to converse arguments and execute
        converse_args = request.to_converse_args()
        return self._llm_manager.converse(**converse_args)

    def get_available_models(self) -> List[str]:
        """
        Get list of currently configured models.

        Returns:
            List of model names
        """
        return self._models.copy()

    def get_available_regions(self) -> List[str]:
        """
        Get list of currently configured regions.

        Returns:
            List of region names
        """
        return self._regions.copy()

    def get_parallel_config(self) -> ParallelProcessingConfig:
        """
        Get current parallel processing configuration.

        Returns:
            ParallelProcessingConfig being used
        """
        return self._parallel_config

    def get_underlying_llm_manager(self) -> LLMManager:
        """
        Get the underlying LLMManager instance.

        Returns:
            LLMManager instance being used for single requests
        """
        return self._llm_manager

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current configuration and return status information.

        Returns:
            Dictionary with validation results
        """
        # Get base validation from underlying LLMManager
        base_validation = self._llm_manager.validate_configuration()

        # Add parallel-specific validation
        parallel_validation: Dict[str, Union[bool, List[str], int, str]] = {
            "parallel_config_valid": True,
            "parallel_errors": [],
            "parallel_warnings": [],
            "max_concurrent_requests": self._parallel_config.max_concurrent_requests,
            "target_regions_available": len(self._regions),
            "load_balancing_strategy": self._parallel_config.load_balancing_strategy.value,
        }

        # Validate parallel configuration
        try:
            if self._parallel_config.max_concurrent_requests > len(self._regions) * 2:
                cast(List[str], parallel_validation["parallel_warnings"]).append(
                    f"High concurrency ({self._parallel_config.max_concurrent_requests}) "
                    f"compared to available regions ({len(self._regions)})"
                )
        except Exception as e:
            parallel_validation["parallel_config_valid"] = False
            cast(List[str], parallel_validation["parallel_errors"]).append(str(e))

        # Combine validations
        combined_validation = base_validation.copy()
        combined_validation.update(parallel_validation)
        combined_validation["valid"] = (
            base_validation["valid"] and parallel_validation["parallel_config_valid"]
        )

        return combined_validation

    def refresh_model_data(self) -> None:
        """
        Refresh the unified model data for the underlying LLMManager.

        Raises:
            ParallelProcessingError: If refresh fails
        """
        try:
            self._llm_manager.refresh_model_data()
        except Exception as e:
            raise ParallelProcessingError(f"Failed to refresh model data: {str(e)}") from e

    def __repr__(self) -> str:
        """Return string representation of the ParallelLLMManager."""
        return (
            f"ParallelLLMManager(models={len(self._models)}, regions={len(self._regions)}, "
            f"max_concurrent={self._parallel_config.max_concurrent_requests}, "
            f"strategy={self._parallel_config.load_balancing_strategy.value})"
        )
