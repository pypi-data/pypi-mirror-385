"""Auto-generated worker client"""

import requests
from typing import Dict, Any, Optional
from . import types


class JobResponse:
    """Response from enqueueing a job"""
    def __init__(self, data: Dict[str, Any]):
        self.success = data.get("success", False)
        self.job_id = data.get("jobId")
        self.message_name = data.get("messageName")
        self.queue = data.get("queue")

    def __repr__(self):
        return f"JobResponse(job_id={self.job_id}, message={self.message_name})"


class JobStatus:
    """Job status information"""
    def __init__(self, data: Dict[str, Any]):
        self.job_id = data.get("jobId")
        self.name = data.get("name")
        self.queue = data.get("queue")
        self.state = data.get("state")
        self.data = data.get("data")
        self.returnvalue = data.get("returnvalue")
        self.progress = data.get("progress")
        self.timestamp = data.get("timestamp")

    def __repr__(self):
        return f"JobStatus(job_id={self.job_id}, state={self.state})"


class WorkerClient:
    """HTTP-based client for worker-backend"""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """Initialize the worker client

        Args:
            base_url: Base URL of the worker backend (e.g., "http://localhost:3000")
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def send_to_queue(self, message_type: str, payload: Dict[str, Any]) -> JobResponse:
        """Send a job to the queue

        Args:
            message_type: Type of message (use types.MessageTypes constants)
            payload: Message payload

        Returns:
            JobResponse with job ID and metadata

        Raises:
            requests.HTTPError: If the request fails
        """
        url = f"{self.base_url}/api/jobs/{message_type}"
        response = self.session.post(
            url,
            json=payload,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return JobResponse(response.json())

    def get_job_status(self, job_id: str) -> JobStatus:
        """Get job status by job ID

        Args:
            job_id: Job ID returned from send_to_queue

        Returns:
            JobStatus with job details

        Raises:
            requests.HTTPError: If the request fails
        """
        url = f"{self.base_url}/api/jobs/{job_id}"
        response = self.session.get(
            url,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return JobStatus(response.json())

    def file_download_request(self, data: types.FileDownloadRequestMessage) -> JobResponse:
        """Handles file download requests.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.FILE_DOWNLOAD_REQUEST, data)

    def model_discovery_folder_processed_event(self, data: types.ModelDiscoveryFolderProcessedEventMessage) -> JobResponse:
        """Handles model discovery folder processed events.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.MODEL_DISCOVERY_FOLDER_PROCESSED_EVENT, data)

    def model_discovery_scan_found_event(self, data: types.ModelDiscoveryScanFoundEventMessage) -> JobResponse:
        """Handles model discovery scan found events.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.MODEL_DISCOVERY_SCAN_FOUND_EVENT, data)

    def model_discovery_scan_progress_event(self, data: types.ModelDiscoveryScanProgressEventMessage) -> JobResponse:
        """Handles model discovery scan progress events.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.MODEL_DISCOVERY_SCAN_PROGRESS_EVENT, data)

    def model_discovery_scan_request(self, data: types.ModelDiscoveryScanRequestMessage) -> JobResponse:
        """Handles model discovery scan requests events.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.MODEL_DISCOVERY_SCAN_REQUEST, data)

    def model_metadata_generation_completed(self, data: types.ModelMetadataGenerationCompletedMessage) -> JobResponse:
        """Handles model metadata generation completed.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.MODEL_METADATA_GENERATION_COMPLETED, data)

    def model_metadata_generation_request(self, data: types.ModelMetadataGenerationRequestMessage) -> JobResponse:
        """Handles model metadata generation requests.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.MODEL_METADATA_GENERATION_REQUEST, data)

    def model_metamodel_detection_found(self, data: types.ModelMetamodelDetectionFoundMessage) -> JobResponse:
        """Handles model metamodel detection found.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.MODEL_METAMODEL_DETECTION_FOUND, data)

    def model_metamodel_detection_request(self, data: types.ModelMetamodelDetectionRequestMessage) -> JobResponse:
        """Handles model metamodel detection requests.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.MODEL_METAMODEL_DETECTION_REQUEST, data)

    def thumbnail_generation_completed(self, data: types.ThumbnailGenerationCompletedMessage) -> JobResponse:
        """Handles thumbnail generation completed.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.THUMBNAIL_GENERATION_COMPLETED, data)

    def thumbnail_generation_request(self, data: types.ThumbnailGenerationRequestMessage) -> JobResponse:
        """Handles thumbnail generation requests.

        Args:
            data: Message payload

        Returns:
            JobResponse with job ID
        """
        return self.send_to_queue(types.MessageTypes.THUMBNAIL_GENERATION_REQUEST, data)

    def close(self) -> None:
        """Close the HTTP session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
