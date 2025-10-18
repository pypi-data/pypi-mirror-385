"""Auto-generated message types"""

from typing import TypedDict, Optional, Any, List, Dict

# Message type constants
class MessageTypes:
    """Message type constants for type-safe queue operations"""
    FILE_DOWNLOAD_REQUEST = 'file-download-request'
    MODEL_DISCOVERY_FOLDER_PROCESSED_EVENT = 'model-discovery-folder-processed-event'
    MODEL_DISCOVERY_SCAN_FOUND_EVENT = 'model-discovery-scan-found-event'
    MODEL_DISCOVERY_SCAN_PROGRESS_EVENT = 'model-discovery-scan-progress-event'
    MODEL_DISCOVERY_SCAN_REQUEST = 'model-discovery-scan-request'
    MODEL_METADATA_GENERATION_COMPLETED = 'model-metadata-generation-completed'
    MODEL_METADATA_GENERATION_REQUEST = 'model-metadata-generation-request'
    MODEL_METAMODEL_DETECTION_FOUND = 'model-metamodel-detection-found'
    MODEL_METAMODEL_DETECTION_REQUEST = 'model-metamodel-detection-request'
    THUMBNAIL_GENERATION_COMPLETED = 'thumbnail-generation-completed'
    THUMBNAIL_GENERATION_REQUEST = 'thumbnail-generation-request'

class FileDownloadRequestMessage(TypedDict, total=False):
    """Handles file download requests."""
    modelId: str  # The unique identifier for the model to be downloaded.
    storageLocation: Dict[str, Any]  # The storage location of the model.

class ModelDiscoveryFolderProcessedEventMessage(TypedDict, total=False):
    """Handles model discovery folder processed events."""
    connectionId: str  # The unique identifier for the connection.
    folderPath: str  # The path to the processed folder.
    discoveredFiles: List[Any]  # A list of files discovered in the folder.
    folderSignature: Dict[str, Any]  # A signature representing the state of the folder., optional
    processedAt: str  # The timestamp when the folder was processed.
    statistics: Dict[str, Any]  # Statistics about the processed folder.

class ModelDiscoveryScanFoundEventMessage(TypedDict, total=False):
    """Handles model discovery scan found events."""
    modelId: str  # The unique identifier for the model.
    name: str  # The name of the model.
    fileName: str  # The name of the model file.
    description: str  # A description of the model.
    fileTypes: List[Any]  # An array of file types associated with the model.
    size: float  # The size of the model file in bytes.
    storageLocation: Dict[str, Any]  # The storage location of the model.
    providerType: str  # The type of the storage provider.
    metadata: Dict[str, Any]  # A flexible object for additional metadata.

class ModelDiscoveryScanProgressEventMessage(TypedDict, total=False):
    """Handles model discovery scan progress events."""
    payload: Dict[str, Any]  # Contains the discovery scan progress details.

class ModelDiscoveryScanRequestMessage(TypedDict, total=False):
    """Handles model discovery scan requests events."""
    libraryId: str  # The ID of the library to scan.

class ModelMetadataGenerationCompletedMessage(TypedDict, total=False):
    """Handles model metadata generation completed."""
    modelId: str  # The unique identifier for the model., optional
    metadata: Dict[str, Any]  # The enriched metadata for the model.

class ModelMetadataGenerationRequestMessage(TypedDict, total=False):
    """Handles model metadata generation requests."""
    modelId: str  # The unique identifier for the model.
    storageConnectionId: str  # The ID of the storage connection.
    filePath: str  # The path to the model file.
    fileName: str  # The name of the model file.
    fileSize: float  # The size of the model file in bytes.
    fileLastModified: str  # The last modified date of the model file.
    storageProviderType: str  # The type of the storage provider.
    modelThumbnailUrl: str  # The URL of the model thumbnail., optional
    metamodel: Dict[str, Any]  # The metamodel of the model., optional

class ModelMetamodelDetectionFoundMessage(TypedDict, total=False):
    """Handles model metamodel detection found."""
    suggestions: List[Any]  # List of metamodel suggestions., optional

class ModelMetamodelDetectionRequestMessage(TypedDict, total=False):
    """Handles model metamodel detection requests."""
    connectionId: str  # The unique identifier for the storage connection., optional
    folderPath: str  # The path to the folder that was processed., optional
    discoveredFiles: List[Any]  # A list of files discovered in the folder., optional
    folderSignature: Dict[str, Any]  # A signature representing the state of the folder.
    processedAt: str  # The timestamp when the folder was processed., optional
    statistics: Dict[str, Any]  # Statistics about the processed folder.

class ThumbnailGenerationCompletedMessage(TypedDict, total=False):
    """Handles thumbnail generation completed."""
    originalJobId: str  # The ID of the original job that requested the thumbnail generation.
    modelId: str  # The ID of the model that the thumbnail was generated for.
    status: str  # The status of the thumbnail generation.
    thumbnailPath: str  # The path to the generated thumbnail., optional
    errorMessage: str  # An error message if the thumbnail generation failed., optional
    storageLocation: Dict[str, Any]  # The storage location of the model.

class ThumbnailGenerationRequestMessage(TypedDict, total=False):
    """Handles thumbnail generation requests."""
    modelId: str  # The unique identifier for the model requiring a thumbnail.
    ownerId: str  # The identifier of the user who owns the entity.
    storageLocation: Dict[str, Any]  # The storage location of the model.
    previewType: str  # The type of preview to generate, e.g., 'default', 'static', 'glb'.

