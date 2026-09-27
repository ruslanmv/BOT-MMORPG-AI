# modelhub/model_metadata.py
"""
Model Metadata Management System

Industry best practices for video game AI model management:
- Comprehensive model versioning and tracking
- Training configuration preservation
- Performance metrics and benchmarks
- Input/output specifications
- Cross-platform compatibility information

This module provides structured metadata for neural network models
used in the MMORPG AI bot system.
"""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import platform

from modelhub.action_space import BASE_ACTION_COUNT


@dataclass
class InputSpec:
    """Specification for model input."""
    width: int = 480
    height: int = 270
    channels: int = 3
    dtype: str = "float32"
    normalize: bool = True
    color_space: str = "RGB"  # RGB, BGR, GRAY

    @property
    def shape(self) -> Tuple[int, int, int]:
        return (self.height, self.width, self.channels)


@dataclass
class OutputSpec:
    """Specification for model output.

    `num_classes` is the discrete slot count; a model recorded with
    `collect_data --mouse` declares this plus the mouse block.
    """
    num_classes: int = BASE_ACTION_COUNT
    class_names: List[str] = field(default_factory=list)
    output_type: str = "classification"  # classification, regression, multi-label
    activation: str = "softmax"


@dataclass
class TrainingConfig:
    """Configuration used during model training."""
    architecture: str = "inception_v3"
    learning_rate: float = 0.001
    optimizer: str = "momentum"
    loss_function: str = "categorical_crossentropy"
    batch_size: int = 32
    epochs_total: int = 0
    epochs_per_file: int = 1
    dropout_rate: float = 0.4
    augmentation_enabled: bool = False
    early_stopping: bool = False

    # Dataset info
    training_files: int = 0
    training_samples: int = 0
    validation_split: float = 0.1

    # Hardware
    gpu_enabled: bool = False
    gpu_name: Optional[str] = None
    mixed_precision: bool = False


@dataclass
class PerformanceMetrics:
    """Model performance and benchmark data."""
    # Accuracy metrics
    train_accuracy: Optional[float] = None
    val_accuracy: Optional[float] = None
    test_accuracy: Optional[float] = None

    # Loss metrics
    train_loss: Optional[float] = None
    val_loss: Optional[float] = None

    # Per-class metrics (optional)
    class_accuracies: Dict[str, float] = field(default_factory=dict)
    confusion_matrix: Optional[List[List[int]]] = None

    # Inference benchmarks
    inference_time_ms: Optional[float] = None
    fps_capability: Optional[float] = None
    memory_usage_mb: Optional[float] = None

    # Training time
    total_training_time_seconds: Optional[float] = None


@dataclass
class CompatibilityInfo:
    """Platform and framework compatibility information."""
    tensorflow_version: str = ""
    tflearn_version: str = ""
    pytorch_version: str = ""
    torchvision_version: str = ""
    python_version: str = ""
    platform: str = ""

    # Model format
    model_format: str = "pytorch"  # pytorch, tensorflow_checkpoint, keras, savedmodel, onnx
    checkpoint_version: int = 2

    # Hardware requirements
    min_gpu_memory_mb: Optional[int] = None
    cpu_only_compatible: bool = True

    # PyTorch specific
    temporal_frames: int = 1  # For LSTM models


@dataclass
class ModelMetadata:
    """
    Complete model metadata following video game industry best practices.

    This metadata is stored alongside model files as 'metadata.json' and
    provides all information needed to:
    - Reproduce training
    - Understand model capabilities
    - Ensure compatibility
    - Track model lineage
    """
    # Identity
    model_id: str = ""
    model_name: str = ""
    version: str = "1.0.0"
    description: str = ""

    # Game association
    game_id: str = "genshin_impact"
    game_name: str = "Genshin Impact"

    # Timestamps
    created_at: str = ""
    updated_at: str = ""
    trained_at: str = ""

    # Author info
    author: str = ""
    organization: str = ""

    # Specifications
    input_spec: InputSpec = field(default_factory=InputSpec)
    output_spec: OutputSpec = field(default_factory=OutputSpec)
    training_config: TrainingConfig = field(default_factory=TrainingConfig)
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    compatibility: CompatibilityInfo = field(default_factory=CompatibilityInfo)

    # Model files
    checkpoint_files: List[str] = field(default_factory=list)
    model_hash: str = ""  # SHA256 of primary model file
    total_size_bytes: int = 0

    # Tags and categories
    tags: List[str] = field(default_factory=list)
    status: str = "draft"  # draft, testing, production, deprecated

    # Lineage
    parent_model_id: Optional[str] = None
    dataset_ids: List[str] = field(default_factory=list)

    # Custom fields
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps and system info if not set."""
        now = datetime.utcnow().isoformat() + "Z"
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

        # Auto-detect compatibility info
        if not self.compatibility.python_version:
            self.compatibility.python_version = platform.python_version()
        if not self.compatibility.platform:
            self.compatibility.platform = f"{platform.system()} {platform.release()}"

        # Try to get PyTorch version (preferred)
        if not self.compatibility.pytorch_version:
            try:
                import torch
                self.compatibility.pytorch_version = torch.__version__
            except ImportError:
                pass

        # Try to get torchvision version
        if not self.compatibility.torchvision_version:
            try:
                import torchvision
                self.compatibility.torchvision_version = torchvision.__version__
            except ImportError:
                pass

        # Try to get TensorFlow version (legacy)
        if not self.compatibility.tensorflow_version:
            try:
                import tensorflow as tf
                self.compatibility.tensorflow_version = tf.__version__
            except ImportError:
                pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelMetadata":
        """Create ModelMetadata from dictionary."""
        # Handle nested dataclasses
        if "input_spec" in data and isinstance(data["input_spec"], dict):
            data["input_spec"] = InputSpec(**data["input_spec"])
        if "output_spec" in data and isinstance(data["output_spec"], dict):
            data["output_spec"] = OutputSpec(**data["output_spec"])
        if "training_config" in data and isinstance(data["training_config"], dict):
            data["training_config"] = TrainingConfig(**data["training_config"])
        if "performance" in data and isinstance(data["performance"], dict):
            data["performance"] = PerformanceMetrics(**data["performance"])
        if "compatibility" in data and isinstance(data["compatibility"], dict):
            data["compatibility"] = CompatibilityInfo(**data["compatibility"])

        return cls(**data)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow().isoformat() + "Z"


def save_metadata(metadata: ModelMetadata, model_dir: Path) -> Path:
    """
    Save model metadata to a JSON file.

    Args:
        metadata: ModelMetadata instance
        model_dir: Directory containing the model files

    Returns:
        Path to the saved metadata file
    """
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    metadata.update_timestamp()

    # Calculate model hash if checkpoint exists
    # Support both PyTorch (.pth, .pt) and TensorFlow (.index, .data-*, .keras, .h5) formats
    for ckpt_pattern in ["*.pth", "*.pt", "*.index", "*.data-*", "*.keras", "*.h5"]:
        for f in model_dir.glob(ckpt_pattern):
            if f.is_file() and not metadata.model_hash:
                metadata.model_hash = _hash_file(f)
                break

    # Calculate total size
    metadata.total_size_bytes = sum(
        f.stat().st_size for f in model_dir.rglob("*") if f.is_file()
    )

    # List checkpoint files
    metadata.checkpoint_files = [
        f.name for f in model_dir.iterdir()
        if f.is_file() and not f.name.endswith(".json")
    ]

    metadata_path = model_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return metadata_path


def load_metadata(model_dir: Path) -> Optional[ModelMetadata]:
    """
    Load model metadata from a JSON file.

    Args:
        model_dir: Directory containing the model files

    Returns:
        ModelMetadata instance or None if not found
    """
    model_dir = Path(model_dir)
    metadata_path = model_dir / "metadata.json"

    if not metadata_path.exists():
        # Try legacy profile.json
        profile_path = model_dir / "profile.json"
        if profile_path.exists():
            return _migrate_from_profile(profile_path)
        return None

    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        return ModelMetadata.from_dict(data)
    except Exception:
        return None


def _hash_file(path: Path, chunk_size: int = 65536) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def _migrate_from_profile(profile_path: Path) -> Optional[ModelMetadata]:
    """
    Migrate legacy profile.json to new metadata format.

    This provides backward compatibility with existing models.
    """
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))

        metadata = ModelMetadata(
            model_id=profile_path.parent.name,
            model_name=data.get("profile_name", profile_path.parent.name),
            game_id=data.get("game", "genshin_impact"),
            created_at=data.get("created_at", ""),
        )

        # Map legacy fields
        if "architecture" in data:
            metadata.training_config.architecture = data["architecture"]
        if "dataset_id" in data:
            metadata.dataset_ids = [data["dataset_id"]]

        return metadata
    except Exception:
        return None


def create_default_metadata(
    model_id: str,
    game_id: str = "genshin_impact",
    architecture: str = "inception_v3",
) -> ModelMetadata:
    """
    Create default metadata for a new model.

    Args:
        model_id: Unique identifier for the model
        game_id: Game this model is trained for
        architecture: Neural network architecture name

    Returns:
        ModelMetadata with default values
    """
    # Default class names for MMORPG bot
    default_classes = [
        "W", "S", "A", "D",           # Basic movement
        "WA", "WD", "SA", "SD",       # Diagonal movement
        "NONE",                        # No input
        # Gamepad actions (9-28)
        "GP_A", "GP_B", "GP_X", "GP_Y",
        "GP_LB", "GP_RB", "GP_LT", "GP_RT",
        "GP_LS_UP", "GP_LS_DOWN", "GP_LS_LEFT", "GP_LS_RIGHT",
        "GP_RS_UP", "GP_RS_DOWN", "GP_RS_LEFT", "GP_RS_RIGHT",
        "GP_START", "GP_SELECT", "GP_DPAD_UP", "GP_DPAD_DOWN"
    ]

    return ModelMetadata(
        model_id=model_id,
        model_name=f"{game_id}_{architecture}_{datetime.now().strftime('%Y%m%d')}",
        game_id=game_id,
        input_spec=InputSpec(width=480, height=270, channels=3),
        output_spec=OutputSpec(
            num_classes=BASE_ACTION_COUNT,
            class_names=default_classes[:BASE_ACTION_COUNT],
        ),
        training_config=TrainingConfig(architecture=architecture),
        tags=[game_id, architecture, "auto-generated"],
        status="draft"
    )


def validate_metadata(metadata: ModelMetadata) -> Tuple[bool, List[str]]:
    """
    Validate model metadata for completeness and consistency.

    Args:
        metadata: ModelMetadata to validate

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors: List[str] = []

    # Required fields
    if not metadata.model_id:
        errors.append("model_id is required")
    if not metadata.game_id:
        errors.append("game_id is required")
    if not metadata.training_config.architecture:
        errors.append("training_config.architecture is required")

    # Input spec validation
    if metadata.input_spec.width <= 0 or metadata.input_spec.height <= 0:
        errors.append("input_spec dimensions must be positive")
    if metadata.input_spec.channels not in [1, 3, 4]:
        errors.append("input_spec.channels must be 1, 3, or 4")

    # Output spec validation
    if metadata.output_spec.num_classes <= 0:
        errors.append("output_spec.num_classes must be positive")

    # Performance validation (warnings, not errors)
    if metadata.performance.val_accuracy is not None:
        if not 0 <= metadata.performance.val_accuracy <= 1:
            errors.append("performance.val_accuracy should be between 0 and 1")

    return len(errors) == 0, errors
