"""
Fire Opal job functionality.
"""

# ruff: noqa: SLF001

import logging
from typing import Optional

from qiskit.primitives.containers import SamplerPubResult
from qiskit_ibm_runtime.base_primitive import SamplerPub
from qiskit_ibm_runtime.runtime_job_v2 import RuntimeJobV2
from qiskit_ibm_runtime.utils.result_decoder import ResultDecoder

from fireopalrikenclient.utils.client import (
    FireOpalClientInterface,
)
from fireopalrikenclient.utils.requests import (
    create_fire_opal_postprocessing_request,
)
from fireopalrikencommons.serializers import (
    decode_sampler_pub_results,
)

logger = logging.getLogger(__name__)


class FireOpalJob(RuntimeJobV2):
    """
    Specialized job class for Fire Opal sampler. This runs Fire Opal post-processing
    after the job completes.

    Notes
    -----
    A current limitation is that this object needs to be kept alive in memory in order to perform
    Fire Opal post-processing. This is due to the fact that we need the input pubs and preprocessed
    pubs to properly shape and extract the post-processed results.
    """

    _grpc_client: FireOpalClientInterface
    _task_id: str
    _input_pubs: list[SamplerPub]
    _preprocessed_pubs: list[SamplerPub]
    _post_processed_results: Optional[list[SamplerPubResult]]

    @classmethod
    def from_runtime_job_v2(
        cls,
        job: RuntimeJobV2,
        task_id: str,
        input_pubs: list[SamplerPub],
        preprocessed_pubs: list[SamplerPub],
        grpc_client: FireOpalClientInterface,
    ) -> "FireOpalJob":
        """
        Create a FireOpalJob instance from an existing RuntimeJobV2. This method
        copies over all relevant attributes and sets Fire Opal specific attributes
        needed for post-processing.

        Parameters
        ----------
        job : RuntimeJobV2
            The original runtime job to copy attributes from.
        task_id : str
            The unique identifier for the Fire Opal task.
        input_pubs : list[SamplerPub]
            The list of input publications for the job.
        preprocessed_pubs : list[SamplerPub]
            The list of preprocessed publications for the job.
        grpc_client : FireOpalClientInterface
            The gRPC client used to communicate with the Fire Opal server.

        Returns
        -------
        FireOpalJob
            An instance of FireOpalJob with necessary attributes set to handle
            post-processing.
        """
        # Copy over job attributes to new FireOpalJob instance.
        # Deprecated attributes are excluded.
        instance = FireOpalJob(
            backend=job._backend,
            api_client=job._api_client,
            job_id=job._job_id,
            program_id=job._program_id,
            service=job._service,
            creation_date=job._creation_date,
            result_decoder=job._final_result_decoder,
            image=job._image,
            session_id=job._session_id,
            tags=job._tags,
            version=job._version,
            private=job._private,
        )

        # Copy over the internal state from the original job. If it does not exist,
        # default to "INITIALIZING"
        instance._status = getattr(job, "_status", "INITIALIZING")

        # Set Fire Opal specific attributes
        instance._grpc_client = grpc_client
        instance._task_id = task_id
        instance._input_pubs = input_pubs
        instance._preprocessed_pubs = preprocessed_pubs

        # Create a object to cache and store post-processed results
        instance._post_processed_results = None
        return instance

    def result(  # pylint: disable=arguments-differ
        self,
        timeout: Optional[float] = None,
        decoder: Optional[type[ResultDecoder]] = None,
    ) -> list[SamplerPubResult]:
        """
        Override the base qiskit RuntimeJobV2 result method to call the Fire Opal
        post-processing grpc task.

        Parameters
        ----------
        timeout : float, optional
            The maximum number of seconds to wait for the job to complete.
            If None, wait indefinitely. Default is None.
        decoder : Type[ResultDecoder], optional
            A custom result decoder class. If None, use the default decoder.
            Default is None.
        """
        if self._post_processed_results is not None:
            return self._post_processed_results

        try:
            device_result_pubs: list[SamplerPubResult] = super().result(
                timeout=timeout, decoder=decoder
            )
        except Exception:
            logger.exception(
                "Failed to retrieve results for task '%s' on device '%s'.",
                self._task_id,
                self._backend.name,
            )
            raise

        logger.info(
            "Results received from device '%s' for job '%s'",
            self._backend.name,
            self._task_id,
        )

        # Call fire opal post-processing grpc task.
        postprocessing_request = create_fire_opal_postprocessing_request(
            self._task_id, device_result_pubs, self._input_pubs, self._preprocessed_pubs
        )

        logger.info("Calling Fire Opal post-processing grpc task")
        postprocessing_result = self._grpc_client.postprocess_results(
            postprocessing_request
        )

        output_result_pubs = decode_sampler_pub_results(postprocessing_result.results)
        logger.info("FireOpal job '%s' completed successfully", self._task_id)

        # Cache the post-processed results for subsequent calls to result.
        self._post_processed_results = output_result_pubs
        return output_result_pubs
