# Worker Backend Client (Python)

Auto-generated Python client library for the Mesh-Sync worker-backend.

## Installation

### From PyPI (public registry)

```bash
pip install mesh-sync-worker-backend-client
```

### From source (development)

```bash
# Clone the repository and navigate to the generated Python client
cd generated/python

# Install in editable mode
pip install -e .
```

### From TestPyPI (testing)

```bash
pip install --index-url https://test.pypi.org/simple/ mesh-sync-worker-backend-client
```

### From GitHub Packages (Recommended for Private Access)

GitHub Packages provides package hosting with access control based on repository permissions.

**Prerequisites:**
- GitHub Personal Access Token (PAT) with `read:packages` scope
- Repository access (for private packages)

**Installation Steps:**

1. Generate a GitHub Personal Access Token:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `read:packages` scope
   - Copy the token

2. Install with GitHub authentication:

```bash
pip install mesh-sync-worker-backend-client \
  --index-url https://your_github_username:ghp_your_token@maven.pkg.github.com/Mesh-Sync/worker-backend/simple/
```

3. Or configure `~/.pypirc` for persistent authentication:

```ini
[distutils]
index-servers =
    github

[github]
repository = https://maven.pkg.github.com/Mesh-Sync/worker-backend
username = your_github_username
password = ghp_your_personal_access_token
```

Then install normally:

```bash
pip install mesh-sync-worker-backend-client
```

**Access Control:** Only users with read access to the repository can install private packages from GitHub Packages.

### From a private PyPI registry

Configure your `pip.conf` or `~/.pypirc`:

**For pip.conf (Linux/Mac: `~/.config/pip/pip.conf`, Windows: `%APPDATA%\pip\pip.ini`):**

```ini
[global]
index-url = https://your-registry.example.com/simple
```

**For authentication with .pypirc (`~/.pypirc`):**

```ini
[distutils]
index-servers =
    private

[private]
repository = https://your-registry.example.com
username = your_username
password = your_password
```

Then install:

```bash
pip install mesh-sync-worker-backend-client
```

## Usage

### Basic Example

```python
from worker_client import WorkerClient

# Initialize client
client = WorkerClient(
    base_url='http://localhost:3000',
    api_key='your_api_key',  # Optional
    timeout=30  # Optional, default 30s
)

# Type-safe method call
job = client.file_download_request({
    'url': 'https://example.com/file.pdf',
    'destination': '/downloads/file.pdf'
})

print(f'Job created: {job.job_id}')

# Check job status
status = client.get_job_status(job.job_id)
print(f'Job state: {status.state}')

# Close the client session
client.close()
```

### Using Context Manager

```python
from worker_client import WorkerClient

with WorkerClient(base_url='http://localhost:3000') as client:
    job = client.file_download_request({
        'url': 'https://example.com/file.pdf',
        'destination': '/downloads/file.pdf'
    })
    print(f'Job ID: {job.job_id}')
```

### Using Message Type Constants

```python
from worker_client import WorkerClient, MessageTypes

client = WorkerClient(base_url='http://localhost:3000')

# Dynamic message type
job = client.send_to_queue(MessageTypes.FILE_DOWNLOAD_REQUEST, {
    'url': 'https://example.com/file.pdf',
    'destination': '/downloads/file.pdf'
})
```

## Available Message Types

### file-download-request

**Description:** Handles file download requests.

**Method:** `client.file_download_request(data)`

**Payload Type:** `FileDownloadRequestMessage`

**Fields:**
- `modelId` (string) [✓]: The unique identifier for the model to be downloaded.
- `storageLocation` (object) [✓]: The storage location of the model.

### model-discovery-folder-processed-event

**Description:** Handles model discovery folder processed events.

**Method:** `client.model_discovery_folder_processed_event(data)`

**Payload Type:** `ModelDiscoveryFolderProcessedEventMessage`

**Fields:**
- `connectionId` (string) [✓]: The unique identifier for the connection.
- `folderPath` (string) [✓]: The path to the processed folder.
- `discoveredFiles` (array) [✓]: A list of files discovered in the folder.
- `folderSignature` (object) [✗]: A signature representing the state of the folder.
- `processedAt` (string) [✓]: The timestamp when the folder was processed.
- `statistics` (object) [✓]: Statistics about the processed folder.

### model-discovery-scan-found-event

**Description:** Handles model discovery scan found events.

**Method:** `client.model_discovery_scan_found_event(data)`

**Payload Type:** `ModelDiscoveryScanFoundEventMessage`

**Fields:**
- `modelId` (string) [✓]: The unique identifier for the model.
- `name` (string) [✓]: The name of the model.
- `fileName` (string) [✓]: The name of the model file.
- `description` (string) [✓]: A description of the model.
- `fileTypes` (array) [✓]: An array of file types associated with the model.
- `size` (number) [✓]: The size of the model file in bytes.
- `storageLocation` (object) [✓]: The storage location of the model.
- `providerType` (string) [✓]: The type of the storage provider.
- `metadata` (object) [✓]: A flexible object for additional metadata.

### model-discovery-scan-progress-event

**Description:** Handles model discovery scan progress events.

**Method:** `client.model_discovery_scan_progress_event(data)`

**Payload Type:** `ModelDiscoveryScanProgressEventMessage`

**Fields:**
- `payload` (object) [✓]: Contains the discovery scan progress details.

### model-discovery-scan-request

**Description:** Handles model discovery scan requests events.

**Method:** `client.model_discovery_scan_request(data)`

**Payload Type:** `ModelDiscoveryScanRequestMessage`

**Fields:**
- `libraryId` (string) [✓]: The ID of the library to scan.

### model-metadata-generation-completed

**Description:** Handles model metadata generation completed.

**Method:** `client.model_metadata_generation_completed(data)`

**Payload Type:** `ModelMetadataGenerationCompletedMessage`

**Fields:**
- `modelId` (string) [✗]: The unique identifier for the model.
- `metadata` (object) [✓]: The enriched metadata for the model.

### model-metadata-generation-request

**Description:** Handles model metadata generation requests.

**Method:** `client.model_metadata_generation_request(data)`

**Payload Type:** `ModelMetadataGenerationRequestMessage`

**Fields:**
- `modelId` (string) [✓]: The unique identifier for the model.
- `storageConnectionId` (string) [✓]: The ID of the storage connection.
- `filePath` (string) [✓]: The path to the model file.
- `fileName` (string) [✓]: The name of the model file.
- `fileSize` (number) [✓]: The size of the model file in bytes.
- `fileLastModified` (string) [✓]: The last modified date of the model file.
- `storageProviderType` (string) [✓]: The type of the storage provider.
- `modelThumbnailUrl` (string) [✗]: The URL of the model thumbnail.
- `metamodel` (object) [✗]: The metamodel of the model.

### model-metamodel-detection-found

**Description:** Handles model metamodel detection found.

**Method:** `client.model_metamodel_detection_found(data)`

**Payload Type:** `ModelMetamodelDetectionFoundMessage`

**Fields:**
- `suggestions` (array) [✗]: List of metamodel suggestions.

### model-metamodel-detection-request

**Description:** Handles model metamodel detection requests.

**Method:** `client.model_metamodel_detection_request(data)`

**Payload Type:** `ModelMetamodelDetectionRequestMessage`

**Fields:**
- `connectionId` (string) [✗]: The unique identifier for the storage connection.
- `folderPath` (string) [✗]: The path to the folder that was processed.
- `discoveredFiles` (array) [✗]: A list of files discovered in the folder.
- `folderSignature` (object) [✓]: A signature representing the state of the folder.
- `processedAt` (string) [✗]: The timestamp when the folder was processed.
- `statistics` (object) [✓]: Statistics about the processed folder.

### thumbnail-generation-completed

**Description:** Handles thumbnail generation completed.

**Method:** `client.thumbnail_generation_completed(data)`

**Payload Type:** `ThumbnailGenerationCompletedMessage`

**Fields:**
- `originalJobId` (string) [✓]: The ID of the original job that requested the thumbnail generation.
- `modelId` (string) [✓]: The ID of the model that the thumbnail was generated for.
- `status` (string) [✓]: The status of the thumbnail generation.
- `thumbnailPath` (string) [✗]: The path to the generated thumbnail.
- `errorMessage` (string) [✗]: An error message if the thumbnail generation failed.
- `storageLocation` (object) [✓]: The storage location of the model.

### thumbnail-generation-request

**Description:** Handles thumbnail generation requests.

**Method:** `client.thumbnail_generation_request(data)`

**Payload Type:** `ThumbnailGenerationRequestMessage`

**Fields:**
- `modelId` (string) [✓]: The unique identifier for the model requiring a thumbnail.
- `ownerId` (string) [✓]: The identifier of the user who owns the entity.
- `storageLocation` (object) [✓]: The storage location of the model.
- `previewType` (string) [✓]: The type of preview to generate, e.g., 'default', 'static', 'glb'.

## Configuration

### Environment Variables

You can use environment variables for configuration:

```python
import os
from worker_client import WorkerClient

client = WorkerClient(
    base_url=os.getenv('WORKER_BACKEND_URL', 'http://localhost:3000'),
    api_key=os.getenv('WORKER_BACKEND_API_KEY'),
    timeout=int(os.getenv('WORKER_BACKEND_TIMEOUT', '30'))
)
```

Supported environment variables:
- `WORKER_BACKEND_URL`: Base URL of the worker backend
- `WORKER_BACKEND_API_KEY`: Optional API key for authentication
- `WORKER_BACKEND_TIMEOUT`: Request timeout in seconds

### Client Options

```python
class WorkerClient:
    def __init__(
        self,
        base_url: str,        # Required: Worker backend URL
        api_key: Optional[str] = None,  # Optional: API key
        timeout: int = 30     # Optional: Request timeout in seconds
    )
```

## API Reference

### `WorkerClient`

#### Methods

- `send_to_queue(message_type: str, payload: Dict[str, Any]) -> JobResponse`
  - Send a job to the queue with the specified message type
  
- `get_job_status(job_id: str) -> JobStatus`
  - Get the current status of a job

- `file_download_request(data: FileDownloadRequestMessage) -> JobResponse`
  - Handles file download requests.
- `model_discovery_folder_processed_event(data: ModelDiscoveryFolderProcessedEventMessage) -> JobResponse`
  - Handles model discovery folder processed events.
- `model_discovery_scan_found_event(data: ModelDiscoveryScanFoundEventMessage) -> JobResponse`
  - Handles model discovery scan found events.
- `model_discovery_scan_progress_event(data: ModelDiscoveryScanProgressEventMessage) -> JobResponse`
  - Handles model discovery scan progress events.
- `model_discovery_scan_request(data: ModelDiscoveryScanRequestMessage) -> JobResponse`
  - Handles model discovery scan requests events.
- `model_metadata_generation_completed(data: ModelMetadataGenerationCompletedMessage) -> JobResponse`
  - Handles model metadata generation completed.
- `model_metadata_generation_request(data: ModelMetadataGenerationRequestMessage) -> JobResponse`
  - Handles model metadata generation requests.
- `model_metamodel_detection_found(data: ModelMetamodelDetectionFoundMessage) -> JobResponse`
  - Handles model metamodel detection found.
- `model_metamodel_detection_request(data: ModelMetamodelDetectionRequestMessage) -> JobResponse`
  - Handles model metamodel detection requests.
- `thumbnail_generation_completed(data: ThumbnailGenerationCompletedMessage) -> JobResponse`
  - Handles thumbnail generation completed.
- `thumbnail_generation_request(data: ThumbnailGenerationRequestMessage) -> JobResponse`
  - Handles thumbnail generation requests.

- `close() -> None`
  - Close the HTTP session

#### Context Manager Support

The client supports the context manager protocol for automatic resource cleanup:

```python
with WorkerClient(base_url='...') as client:
    # Use client
    pass
# Session is automatically closed
```

### Response Types

#### `JobResponse`

```python
class JobResponse:
    success: bool
    job_id: str
    message_name: str
    queue: str
```

#### `JobStatus`

```python
class JobStatus:
    job_id: str
    name: str
    queue: str
    state: str  # 'waiting' | 'active' | 'completed' | 'failed' | 'delayed'
    data: Any
    returnvalue: Optional[Any]
    progress: Optional[int]
    timestamp: int
```

## Docker Usage

A Dockerfile is included for containerized usage:

```bash
cd generated/python
docker build -t worker-client-python .
docker run -it --rm worker-client-python python
```

## License

ISC
