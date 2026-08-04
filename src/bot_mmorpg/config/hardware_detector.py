"""
Hardware Detection Module

Automatically detects system capabilities and recommends appropriate
settings for training and inference.
"""

import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class HardwareTier(Enum):
    """Hardware capability tiers for model selection."""

    LOW = "low"  # < 4GB VRAM or CPU-only
    MEDIUM = "medium"  # 4-8GB VRAM
    HIGH = "high"  # > 8GB VRAM


@dataclass
class GPUInfo:
    """GPU hardware information."""

    name: str
    vram_mb: int
    cuda_available: bool
    cuda_version: Optional[str] = None
    compute_capability: Optional[str] = None


@dataclass
class SystemInfo:
    """Complete system hardware information."""

    platform: str
    cpu_cores: int
    ram_mb: int
    gpu: Optional[GPUInfo]
    tier: HardwareTier

    def summary(self) -> str:
        """Human-readable hardware summary."""
        gpu_str = f"{self.gpu.name} ({self.gpu.vram_mb}MB)" if self.gpu else "CPU only"
        return (
            f"Platform: {self.platform}\n"
            f"CPU Cores: {self.cpu_cores}\n"
            f"RAM: {self.ram_mb // 1024}GB\n"
            f"GPU: {gpu_str}\n"
            f"Tier: {self.tier.value.upper()}"
        )


class HardwareDetector:
    """
    Detects system hardware capabilities for optimal configuration.

    Usage:
        detector = HardwareDetector()
        info = detector.detect()
        print(info.tier)  # HardwareTier.HIGH
        print(info.summary())
    """

    # VRAM thresholds in MB
    LOW_VRAM_THRESHOLD = 4096  # 4GB
    HIGH_VRAM_THRESHOLD = 8192  # 8GB

    def __init__(self):
        self._cached_info: Optional[SystemInfo] = None

    def detect(self, force_refresh: bool = False) -> SystemInfo:
        """
        Detect system hardware capabilities.

        Args:
            force_refresh: If True, re-detect even if cached

        Returns:
            SystemInfo with detected capabilities
        """
        if self._cached_info and not force_refresh:
            return self._cached_info

        system_platform = platform.system()
        cpu_cores = self._detect_cpu_cores()
        ram_mb = self._detect_ram()
        gpu_info = self._detect_gpu()

        tier = self._determine_tier(gpu_info)

        self._cached_info = SystemInfo(
            platform=system_platform,
            cpu_cores=cpu_cores,
            ram_mb=ram_mb,
            gpu=gpu_info,
            tier=tier,
        )

        return self._cached_info

    def _detect_cpu_cores(self) -> int:
        """Detect number of CPU cores."""
        try:
            import os

            return os.cpu_count() or 4
        except Exception:
            return 4

    def _detect_ram(self) -> int:
        """Detect total system RAM in MB."""
        try:
            import psutil

            return int(psutil.virtual_memory().total / (1024 * 1024))
        except ImportError:
            # Fallback for systems without psutil
            return self._detect_ram_fallback()
        except Exception:
            return 8192  # Assume 8GB

    def _detect_ram_fallback(self) -> int:
        """Fallback RAM detection without psutil."""
        system = platform.system()
        try:
            if system == "Linux":
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal"):
                            # MemTotal is in KB
                            kb = int(line.split()[1])
                            return kb // 1024
            elif system == "Darwin":  # macOS
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=5,
                )
                if result.returncode == 0:
                    return int((result.stdout or "").strip()) // (1024 * 1024)
            elif system == "Windows":
                # Issue #76: pin the codec. Under PYTHONUTF8=1 the
                # default text decode is UTF-8, but wmic emits the OEM
                # codepage on localized Windows -- the UnicodeDecodeError
                # is raised inside subprocess's reader thread, so it does
                # not surface here as an exception, it just prints a
                # traceback and leaves stdout as None.
                result = subprocess.run(
                    ["wmic", "OS", "get", "TotalVisibleMemorySize"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=5,
                )
                if result.returncode == 0:
                    lines = (result.stdout or "").strip().split("\n")
                    if len(lines) > 1:
                        kb = int(lines[1].strip())
                        return kb // 1024
        except Exception:
            pass
        return 8192  # Default assumption

    def _detect_gpu(self) -> Optional[GPUInfo]:
        """Detect GPU capabilities using PyTorch."""
        try:
            import torch

            if not torch.cuda.is_available():
                return None

            device_id = 0
            props = torch.cuda.get_device_properties(device_id)

            # Get CUDA version
            cuda_version = None
            if hasattr(torch.version, "cuda"):
                cuda_version = torch.version.cuda

            # Get compute capability
            compute_cap = f"{props.major}.{props.minor}"

            return GPUInfo(
                name=props.name,
                vram_mb=props.total_memory // (1024 * 1024),
                cuda_available=True,
                cuda_version=cuda_version,
                compute_capability=compute_cap,
            )
        except ImportError:
            return None
        except Exception:
            return None

    def _determine_tier(self, gpu: Optional[GPUInfo]) -> HardwareTier:
        """Determine hardware tier based on GPU capabilities."""
        if gpu is None or not gpu.cuda_available:
            return HardwareTier.LOW

        if gpu.vram_mb < self.LOW_VRAM_THRESHOLD:
            return HardwareTier.LOW
        elif gpu.vram_mb < self.HIGH_VRAM_THRESHOLD:
            return HardwareTier.MEDIUM
        else:
            return HardwareTier.HIGH

    def get_recommended_workers(self) -> int:
        """Get recommended number of data loader workers."""
        info = self.detect()
        # Use half of CPU cores, capped at tier limits
        base_workers = max(2, info.cpu_cores // 2)

        tier_limits = {
            HardwareTier.LOW: 2,
            HardwareTier.MEDIUM: 4,
            HardwareTier.HIGH: 8,
        }

        return min(base_workers, tier_limits[info.tier])

    def get_recommended_batch_size(self, input_size: tuple = (224, 224)) -> int:
        """
        Get recommended batch size based on GPU memory.

        Args:
            input_size: Input image dimensions (height, width)

        Returns:
            Recommended batch size
        """
        info = self.detect()

        # Base recommendations by tier
        tier_batch_sizes = {
            HardwareTier.LOW: 8,
            HardwareTier.MEDIUM: 16,
            HardwareTier.HIGH: 32,
        }

        batch_size = tier_batch_sizes[info.tier]

        # Adjust for larger input sizes
        if input_size[0] > 224 or input_size[1] > 224:
            batch_size = max(4, batch_size // 2)

        return batch_size

    def can_use_temporal(self) -> bool:
        """Check if system can handle temporal (LSTM) models."""
        info = self.detect()
        # Temporal models need more memory
        return info.tier in (HardwareTier.MEDIUM, HardwareTier.HIGH)

    def get_recommended_temporal_frames(self) -> int:
        """Get recommended number of temporal frames."""
        info = self.detect()

        if info.tier == HardwareTier.LOW:
            return 0  # No temporal
        elif info.tier == HardwareTier.MEDIUM:
            return 2
        else:
            return 4


# Convenience function
def detect_hardware() -> SystemInfo:
    """Quick hardware detection."""
    return HardwareDetector().detect()
