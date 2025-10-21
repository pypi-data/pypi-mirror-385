"""
Unit tests for FireOpalJob.
"""

import logging
from unittest.mock import Mock, patch

import pytest
from qiskit.primitives.containers import SamplerPubResult
from qiskit_ibm_runtime.base_primitive import SamplerPub
from qiskit_ibm_runtime.runtime_job_v2 import RuntimeJobV2

from fireopalrikenclient.tests.conftest import MockFireOpalClient
from fireopalrikenclient.utils.job import FireOpalJob


def test_from_runtime_job_v2_creates_fire_opal_job(
    mock_client: MockFireOpalClient,
    mock_runtime_job: RuntimeJobV2,
    sample_pubs: list[SamplerPub],
) -> None:
    """Test that from_runtime_job_v2 creates a FireOpalJob with all attributes copied."""
    task_id = "test_task_123"
    input_pubs = sample_pubs
    preprocessed_pubs = sample_pubs  # For simplicity, use the same pubs

    # Create FireOpalJob from RuntimeJobV2
    fire_opal_job = FireOpalJob.from_runtime_job_v2(
        job=mock_runtime_job,
        task_id=task_id,
        input_pubs=input_pubs,
        preprocessed_pubs=preprocessed_pubs,
        grpc_client=mock_client,
    )

    # Verify it's a FireOpalJob instance
    assert isinstance(fire_opal_job, FireOpalJob)

    # Verify Fire Opal specific attributes are set
    assert fire_opal_job._grpc_client is mock_client
    assert fire_opal_job._task_id == task_id
    assert fire_opal_job._input_pubs == input_pubs
    assert fire_opal_job._preprocessed_pubs == preprocessed_pubs

    # Verify attributes copied from original job
    assert fire_opal_job._job_id == mock_runtime_job._job_id
    assert fire_opal_job._backend is mock_runtime_job._backend
    assert fire_opal_job._service is mock_runtime_job._service
    assert fire_opal_job._status == mock_runtime_job._status


@patch("fireopalrikenclient.utils.job.RuntimeJobV2.result")
def test_result_calls_postprocessing_and_returns_results(
    mock_super_result: Mock,
    mock_client: MockFireOpalClient,
    mock_runtime_job: RuntimeJobV2,
    sample_pubs: list[SamplerPub],
    sample_job_results: list[SamplerPubResult],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that result method calls postprocessing and returns processed results."""
    # Setup mocks
    mock_super_result.return_value = sample_job_results
    task_id = "test_task_456"

    # Create FireOpalJob
    fire_opal_job = FireOpalJob.from_runtime_job_v2(
        job=mock_runtime_job,
        task_id=task_id,
        input_pubs=sample_pubs,
        preprocessed_pubs=sample_pubs,
        grpc_client=mock_client,
    )

    # Call result method
    with caplog.at_level(logging.INFO):
        results = fire_opal_job.result()

    # Verify super().result() was called
    mock_super_result.assert_called_once_with(timeout=None, decoder=None)

    # Verify postprocessing was called
    assert len(mock_client.postprocessing_calls) == 1
    postprocessing_request = mock_client.postprocessing_calls[0]
    assert postprocessing_request.task_id == task_id

    # Verify results are returned
    assert isinstance(results, list)
    assert len(results) == len(sample_job_results)

    # Verify appropriate logging occurred
    log_messages = [record.message for record in caplog.records]
    assert any("Results received from device" in msg for msg in log_messages)
    assert any(
        "Calling Fire Opal post-processing grpc task" in msg for msg in log_messages
    )
    assert any(
        f"FireOpal job '{task_id}' completed successfully" in msg
        for msg in log_messages
    )


@patch("fireopalrikenclient.utils.job.RuntimeJobV2.result")
def test_result_handles_device_failure(
    mock_super_result: Mock,
    mock_client: MockFireOpalClient,
    mock_runtime_job: RuntimeJobV2,
    sample_pubs: list[SamplerPub],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that result method handles device execution failures."""
    # Setup mock to raise exception
    mock_super_result.side_effect = Exception("Device execution failed")
    task_id = "test_task_error"

    # Create FireOpalJob
    fire_opal_job = FireOpalJob.from_runtime_job_v2(
        job=mock_runtime_job,
        task_id=task_id,
        input_pubs=sample_pubs,
        preprocessed_pubs=sample_pubs,
        grpc_client=mock_client,
    )

    # Verify exception is re-raised and logged
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="Device execution failed"):
            fire_opal_job.result()

    # Verify error was logged
    log_messages = [record.message for record in caplog.records]
    assert any(
        f"Failed to retrieve results for task '{task_id}'" in msg
        for msg in log_messages
    )

    # Verify postprocessing was not called since device failed
    assert len(mock_client.postprocessing_calls) == 0


@patch("fireopalrikenclient.utils.job.RuntimeJobV2.result")
def test_result_caches_post_processed_results(
    mock_super_result: Mock,
    mock_client: MockFireOpalClient,
    mock_runtime_job: RuntimeJobV2,
    sample_pubs: list[SamplerPub],
    sample_job_results: list[SamplerPubResult],
) -> None:
    """Test that result method caches post-processed results for subsequent calls."""
    # Setup mocks
    mock_super_result.return_value = sample_job_results
    task_id = "test_task_cache"

    # Create FireOpalJob
    fire_opal_job = FireOpalJob.from_runtime_job_v2(
        job=mock_runtime_job,
        task_id=task_id,
        input_pubs=sample_pubs,
        preprocessed_pubs=sample_pubs,
        grpc_client=mock_client,
    )

    # Verify initial state - no cached results
    assert fire_opal_job._post_processed_results is None

    # First call to result() - should perform full processing
    results_1 = fire_opal_job.result()

    # Verify postprocessing was called once
    assert len(mock_client.postprocessing_calls) == 1
    assert mock_super_result.call_count == 1

    # Verify results are cached
    assert fire_opal_job._post_processed_results is not None
    assert fire_opal_job._post_processed_results == results_1

    # Second call to result() - should return cached results
    results_2 = fire_opal_job.result()

    # Verify postprocessing was NOT called again (still only 1 call)
    assert len(mock_client.postprocessing_calls) == 1
    # Verify super().result() was NOT called again (still only 1 call)
    assert mock_super_result.call_count == 1

    # Verify same results are returned
    assert results_2 is results_1
    assert results_2 == results_1
