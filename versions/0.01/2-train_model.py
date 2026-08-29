"""
BOT-MMORPG-AI Training Script (PyTorch)

Train neural network models on recorded gameplay data.
Supports multiple architectures with modern training practices.

Usage:
    python 2-train_model.py --data data/raw --model efficientnet_lstm --epochs 10
    python 2-train_model.py --data data/raw --model mobilenet_v3 --epochs 5 --batch-size 32
    python 2-train_model.py --list-models
"""

from __future__ import annotations

import argparse
import gc
import sys
import os
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
from datetime import timedelta

import numpy as np
import cv2  # noqa: F401  (kept for compatibility; not used directly here)

# PyTorch imports
#
# We catch BaseException (not just ImportError) because Windows torch
# failures often surface as OSError ("[WinError 126] The specified module
# could not be found", "DLL load failed"), RuntimeError (CPU lacks AVX
# instructions), or even raw access violations during DLL load. Catching
# only ImportError silently masks those and the user sees the misleading
# "PyTorch not installed" message even though pip install succeeded.
PYTORCH_AVAILABLE = False
PYTORCH_IMPORT_ERROR: Optional[BaseException] = None
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except BaseException as _torch_import_exc:  # noqa: BLE001 -- intentional broad catch
    PYTORCH_IMPORT_ERROR = _torch_import_exc
    print(
        f"[Warning] PyTorch failed to import: "
        f"{type(_torch_import_exc).__name__}: {_torch_import_exc}"
    )
    print("[Hint] Most common causes on Windows:")
    print("       - Visual C++ Redistributable missing (install vc_redist.x64.exe)")
    print("       - Antivirus quarantined torch DLLs (check exclusions / restore)")
    print("       - CPU lacks AVX/AVX2 instructions (very old hardware)")
    print("       - torch package incomplete (re-run: pip install torch torchvision)")

# When torch is unavailable, `Dataset` is undefined at module top-level.
# `class GameplayDataset(Dataset):` further down would then raise NameError
# at IMPORT time -- before main() ever gets to check PYTORCH_AVAILABLE and
# print a clean error. Use a fallback base class so the module always
# parses; the actual training loop still bails on PYTORCH_AVAILABLE below.
BaseDataset = Dataset if PYTORCH_AVAILABLE else object

# Local imports
try:
    from models_pytorch import (
        get_model, list_models, get_model_info,
        save_model, count_parameters, get_device
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False


# =============================================================================
# Logging
# =============================================================================

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("trainer")
    if logger.handlers:
        return logger  # prevent duplicate handlers if re-imported

    level_str = os.getenv("BOTMMO_LOG_LEVEL", "INFO").upper().strip()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Make sure prints from libraries don't hide our output
    logger.propagate = False
    return logger


LOG = setup_logger()


def hr(title: str = "", width: int = 72) -> str:
    if not title:
        return "=" * width
    pad = max(0, width - len(title) - 2)
    left = pad // 2
    right = pad - left
    return f"{'=' * left} {title} {'=' * right}"


def fmt_seconds(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    return str(timedelta(seconds=int(seconds)))


# =============================================================================
# Configuration (Legacy compatibility)
# =============================================================================

WIDTH = 480
HEIGHT = 270
LR = 1e-3
EPOCHS = 1
MODEL_NAME = 'model/mmorpg_bot'


# =============================================================================
# Dataset
# =============================================================================

class GameplayDataset(BaseDataset):
    """
    PyTorch Dataset for gameplay recordings.

    Loads .npy files containing (frame, action) pairs.
    Supports temporal windowing for LSTM-based models.
    """

    def __init__(
        self,
        data_dir: Path,
        seq_len: int = 1,
        transform=None,
        limit_files: Optional[int] = None,
        file_pattern: str = "training_data-*.npy",
    ):
        self.data_dir = Path(data_dir)
        self.seq_len = seq_len
        self.transform = transform

        # Find all data files (support multiple patterns)
        patterns = [file_pattern, "preprocessed_training_data-*.npy"]
        self.files = []
        for pattern in patterns:
            self.files.extend(sorted(self.data_dir.glob(pattern)))

        # Remove duplicates and sort
        self.files = sorted(set(self.files))

        if limit_files:
            self.files = self.files[:limit_files]

        if not self.files:
            raise ValueError(f"No training data found in {data_dir}")

        LOG.info(f"[Dataset] Found {len(self.files)} data file(s) in: {self.data_dir.resolve()}")
        LOG.info(f"[Dataset] Patterns: {patterns}")

        self._load_data()

    def _load_data(self):
        """Load all data files into memory."""
        all_frames = []
        all_actions = []
        skipped_files = 0
        skipped_items = 0

        t0 = time.time()
        for f in self.files:
            try:
                data = np.load(f, allow_pickle=True)
                for item in data:
                    try:
                        if len(item) >= 2:
                            frame, action = item[0], item[1]
                            all_frames.append(frame)
                            all_actions.append(action)
                        else:
                            skipped_items += 1
                    except Exception:
                        skipped_items += 1
            except Exception as e:
                skipped_files += 1
                LOG.warning(f"[Dataset] Could not load {f}: {e}")

        if not all_frames:
            raise ValueError("No valid data loaded from files")

        self.frames = np.array(all_frames)
        self.actions = np.array(all_actions, dtype=np.float32)

        # Auto-detected width of the action vector. This is the single
        # source of truth for sizing the model's output head. When mouse
        # recording is enabled, collect_data appends 10 extra values
        # (x, y, dx, dy, vx, vy, lmb, rmb, mmb, scroll) so the vector is
        # 39 wide instead of 29 (keyboard=9 + gamepad=20). The trainer
        # must size the head to match or BCEWithLogitsLoss raises
        # "Target size ... must be the same as input size" (issue #64).
        self.num_actions = (
            self.actions.shape[1] if self.actions.ndim == 2 else len(self.actions[0])
        )

        dt = time.time() - t0
        LOG.info(f"[Dataset] Loaded {len(self.frames)} sample(s) in {dt:.1f}s")
        LOG.info(f"[Dataset] Skipped files: {skipped_files}, skipped items: {skipped_items}")
        LOG.info(f"[Dataset] Frame shape: {self.frames[0].shape}")
        LOG.info(f"[Dataset] Action shape: {self.actions[0].shape}")
        LOG.info(f"[Dataset] Auto-detected num_actions: {self.num_actions}")

    def __len__(self) -> int:
        return max(0, len(self.frames) - self.seq_len + 1)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        if self.seq_len > 1:
            frames = self.frames[idx:idx + self.seq_len]
        else:
            frames = self.frames[idx:idx + 1]

        action = self.actions[idx + self.seq_len - 1]

        frames = torch.tensor(frames, dtype=torch.float32)
        frames = frames.permute(0, 3, 1, 2)  # (seq, C, H, W)
        frames = frames / 255.0

        if self.seq_len == 1:
            frames = frames.squeeze(0)

        action = torch.tensor(action, dtype=torch.float32)
        return frames, action


# =============================================================================
# Training Functions
# =============================================================================

def _autocast_cuda():
    """CUDA autocast context, across the torch 2.0 -> 2.4 API move."""
    try:
        return torch.amp.autocast("cuda")
    except (AttributeError, TypeError):
        return torch.cuda.amp.autocast()


def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    epoch: int,
    log_every_batches: int = 10,
    scaler=None,
    use_amp: bool = False,
) -> float:
    """Train for one epoch, with optional mixed precision and OOM recovery."""
    model.train()
    total_loss = 0.0
    num_batches = len(dataloader)
    oom_count = 0

    if num_batches == 0:
        return 0.0

    for batch_idx, (frames, actions) in enumerate(dataloader, start=1):
        frames = frames.to(device)
        actions = actions.to(device)

        try:
            optimizer.zero_grad()

            if use_amp and scaler is not None:
                with _autocast_cuda():
                    outputs = model(frames)
                    loss = criterion(outputs, actions)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(frames)
                loss = criterion(outputs, actions)
                loss.backward()

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

                optimizer.step()

            total_loss += loss.item()

        except RuntimeError as e:
            # A single oversized batch used to abort the whole run with a
            # raw CUDA OOM traceback (issue #27). Drop the batch, free the
            # allocator's cache and keep going; a run that OOMs constantly
            # still stops, but with an actionable message.
            if "out of memory" not in str(e).lower():
                raise
            oom_count += 1
            if device.type == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
            suggested = max(1, (dataloader.batch_size or 2) // 2)
            LOG.warning(
                f"    [OOM] Skipped batch {batch_idx} (total skips: {oom_count}). "
                f"Retry with --batch-size {suggested} if this repeats."
            )
            if oom_count > 5:
                raise RuntimeError(
                    f"Too many CUDA out-of-memory errors ({oom_count}). "
                    f"Re-run with --batch-size {suggested}."
                ) from e
            continue

        if (batch_idx % log_every_batches == 0) or (batch_idx == num_batches):
            LOG.info(f"    [Epoch {epoch}] Batch {batch_idx:>4}/{num_batches} | loss={loss.item():.4f}")

    return total_loss / max(1, num_batches - oom_count)


def validate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float]:
    """Validate the model."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    if dataloader is None or len(dataloader) == 0:
        return 0.0, 0.0

    with torch.no_grad():
        for frames, actions in dataloader:
            frames = frames.to(device)
            actions = actions.to(device)

            outputs = model(frames)
            loss = criterion(outputs, actions)
            total_loss += loss.item()

            preds = (torch.sigmoid(outputs) > 0.5).float()
            correct += (preds == actions).all(dim=1).sum().item()
            total += actions.size(0)

    avg_loss = total_loss / len(dataloader) if len(dataloader) > 0 else 0.0
    accuracy = correct / total if total > 0 else 0.0
    return avg_loss, accuracy


def _safe_total_vram_gb() -> Optional[float]:
    """Total GPU VRAM in GB, or None when it cannot be determined.

    PyTorch's CUDA 13 build renamed the device property `total_mem` ->
    `total_memory`; older builds only have `total_mem`. Probe both and
    give up quietly on anything else (ROCm, forks, a CPU-only build that
    reports is_available() anyway) so a missing attribute never takes
    down the run. See issue #59.
    """
    if not PYTORCH_AVAILABLE or not torch.cuda.is_available():
        return None
    try:
        props = torch.cuda.get_device_properties(0)
    except Exception:  # noqa: BLE001
        return None
    for attr in ("total_memory", "total_mem"):
        val = getattr(props, attr, None)
        if val is not None:
            try:
                return float(val) / 1e9
            except (TypeError, ValueError):
                continue
    return None


def _enable_gradient_checkpointing(model: "nn.Module") -> bool:
    """Trade compute for VRAM on backbones that support it."""
    enabled = False
    backbone = getattr(model, "backbone", None)
    features = getattr(backbone, "features", None)
    if features is not None:
        for module in features:
            if hasattr(module, "gradient_checkpointing_enable"):
                module.gradient_checkpointing_enable()
                enabled = True
    if hasattr(model, "set_grad_checkpointing"):
        model.set_grad_checkpointing(True)
        enabled = True
    return enabled


def autotune_batch_size(
    batch_size: int, device: "torch.device"
) -> Tuple[int, bool, bool]:
    """Pick VRAM-safe training settings for the detected GPU.

    The shipped default of 8 still OOMs on 6 GB cards, and a user who
    manually raised it has no way to know their card cannot take it --
    the run just dies mid-epoch with a CUDA allocator dump (issue #27).
    Scale the batch down to what the card holds and turn on mixed
    precision, which is both lighter and *faster* than the fp32 fallback
    the reporter measured as "slower than CPU".

    Returns:
        (batch_size, use_amp, use_gradient_checkpointing)
    """
    if device.type != "cuda":
        return batch_size, False, False

    total_gb = _safe_total_vram_gb()
    if total_gb is None:
        LOG.info(
            "[Auto] Could not read GPU VRAM size; assuming 6GB and using "
            "conservative batch size + AMP + gradient checkpointing."
        )
        total_gb = 6.0

    if total_gb <= 6 and batch_size > 4:
        LOG.info(
            f"[Auto] GPU has {total_gb:.1f}GB VRAM — reducing batch_size "
            f"{batch_size} -> 4, enabling AMP (fp16) and gradient checkpointing"
        )
        return 4, True, True
    if total_gb <= 8 and batch_size > 8:
        LOG.info(
            f"[Auto] GPU has {total_gb:.1f}GB VRAM — reducing batch_size "
            f"{batch_size} -> 8, enabling AMP (fp16) and gradient checkpointing"
        )
        return 8, True, True
    if total_gb <= 12 and batch_size > 16:
        LOG.info(
            f"[Auto] GPU has {total_gb:.1f}GB VRAM — reducing batch_size "
            f"{batch_size} -> 16 and enabling AMP (fp16)"
        )
        return 16, True, False

    # Plenty of VRAM: keep the requested batch but still use AMP, which
    # is the difference between "GPU slower than CPU" and a real speedup
    # on any tensor-core card.
    LOG.info(f"[Auto] GPU has {total_gb:.1f}GB VRAM — enabling AMP (fp16)")
    return batch_size, True, False


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: Optional[DataLoader],
    device: torch.device,
    epochs: int = 10,
    learning_rate: float = 1e-4,
    save_dir: Path = Path("artifacts/model"),
    model_name: str = "model",
    use_amp: bool = False,
    use_gradient_checkpointing: bool = False,
) -> nn.Module:
    """Full training loop with validation and checkpointing."""
    model = model.to(device)

    if use_gradient_checkpointing and _enable_gradient_checkpointing(model):
        LOG.info("Gradient checkpointing enabled (lower VRAM, ~20% slower/epoch)")

    # `torch.amp.GradScaler("cuda")` landed in torch 2.4; pyproject still
    # allows 2.0, so fall back to the older namespace and, failing that,
    # train in fp32 rather than crashing a run that used to work.
    scaler = None
    if use_amp and device.type == "cuda":
        try:
            scaler = torch.amp.GradScaler("cuda")
        except (AttributeError, TypeError):
            try:
                scaler = torch.cuda.amp.GradScaler()
            except Exception:  # noqa: BLE001
                LOG.warning(
                    "Mixed precision unavailable on this PyTorch build; "
                    "continuing in fp32."
                )
    if scaler is None:
        use_amp = False

    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, epochs))
    criterion = nn.BCEWithLogitsLoss()

    best_val_loss = float("inf")
    start_time = time.time()

    LOG.info(hr("TRAINING CONFIG"))
    LOG.info(f"Model           : {model_name} ({model.__class__.__name__})")
    LOG.info(f"Parameters      : {count_parameters(model):,}")
    LOG.info(f"Device          : {device}")
    LOG.info(f"Epochs          : {epochs}")
    LOG.info(f"Learning rate   : {learning_rate}")
    LOG.info(f"Train batches   : {len(train_loader)}")
    LOG.info(f"Val batches     : {len(val_loader) if val_loader else 0}")
    LOG.info(f"Batch size      : {train_loader.batch_size}")
    LOG.info(f"Mixed precision : {'on (fp16)' if use_amp else 'off'}")
    LOG.info(f"Artifacts dir   : {save_dir.resolve()}")
    LOG.info(hr())

    for ep in range(1, epochs + 1):
        epoch_t0 = time.time()
        lr_now = optimizer.param_groups[0]["lr"]

        LOG.info(hr(f"EPOCH {ep}/{epochs}", width=72))

        train_loss = train_epoch(
            model=model,
            dataloader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            device=device,
            epoch=ep,
            log_every_batches=10,
            scaler=scaler,
            use_amp=use_amp,
        )

        val_loss = None
        val_acc = None
        if val_loader:
            val_loss, val_acc = validate(model, val_loader, criterion, device)

        scheduler.step()

        epoch_dt = time.time() - epoch_t0
        elapsed = time.time() - start_time
        avg_epoch = elapsed / ep
        eta = avg_epoch * (epochs - ep)

        if val_loader:
            LOG.info(
                f"[Epoch {ep}/{epochs}] "
                f"train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | val_acc={val_acc:.4f} | "
                f"lr={lr_now:.2e} | time={epoch_dt:.1f}s | eta={fmt_seconds(eta)}"
            )
        else:
            LOG.info(
                f"[Epoch {ep}/{epochs}] "
                f"train_loss={train_loss:.4f} | lr={lr_now:.2e} | time={epoch_dt:.1f}s | eta={fmt_seconds(eta)}"
            )

        # Save best model (if validation exists)
        if val_loader and val_loss is not None and val_loss < best_val_loss:
            best_val_loss = val_loss
            save_path = save_dir / f"{model_name}_best.pth"
            save_model(
                model, str(save_path),
                optimizer=optimizer,
                epoch=ep - 1,
                loss=val_loss,
                model_name=model.__class__.__name__,
            )
            LOG.info(f"[Save] New best model -> {save_path.resolve()} (val_loss={val_loss:.4f})")

        # Checkpoint every 5 epochs
        if ep % 5 == 0:
            save_path = save_dir / f"{model_name}_epoch{ep}.pth"
            save_model(model, str(save_path), optimizer=optimizer, epoch=ep - 1, loss=train_loss)
            LOG.info(f"[Save] Checkpoint -> {save_path.resolve()}")

    # Save final model
    save_path = save_dir / f"{model_name}_final.pth"
    save_model(model, str(save_path), optimizer=optimizer, epoch=epochs - 1)
    LOG.info(hr("TRAINING DONE"))
    LOG.info(f"[Save] Final model -> {save_path.resolve()}")
    LOG.info(hr())

    return model


# =============================================================================
# Main
# =============================================================================

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="BOT-MMORPG-AI Model Training (PyTorch)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--data", default="data/raw", help="Folder with .npy files")
    parser.add_argument("--out", default="artifacts/model", help="Folder to save model")
    parser.add_argument("--model", default="efficientnet_lstm", help="Model architecture")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size. Default 8 to fit 8 GB GPUs (issue #27). Raise to 16/32 for more VRAM.",
    )
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--seq-len", type=int, default=4, help="Sequence length for temporal models")
    parser.add_argument(
        "--num-actions",
        type=int,
        default=0,
        help="Number of output actions (0 = auto-detect from data; issue #64)",
    )
    parser.add_argument(
        "--amp",
        action="store_true",
        help="Force mixed-precision (fp16) training on CUDA.",
    )
    parser.add_argument(
        "--no-autotune",
        action="store_true",
        help="Use --batch-size verbatim instead of fitting it to the GPU's VRAM (issue #27).",
    )
    parser.add_argument("--val-split", type=float, default=0.1, help="Validation split ratio")
    parser.add_argument("--no-pretrained", action="store_true", help="Don't use pretrained weights")
    parser.add_argument("--cpu", action="store_true", help="Force CPU training")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--limit-files", type=int, help="Limit number of data files (for testing)")

    args = parser.parse_args(argv)

    # List models and exit
    if args.list_models:
        if not MODELS_AVAILABLE:
            LOG.error("[Error] models_pytorch.py not found")
            return 1
        LOG.info("\nAvailable Models:")
        LOG.info(hr())
        for name in list_models():
            info = get_model_info(name)
            rec = " [RECOMMENDED]" if info.get("recommended") else ""
            LOG.info(f"\n  {name}{rec}")
            LOG.info(f"    {info['description']}")
            LOG.info(f"    Params: {info['params']}, Inference: {info['inference_ms']}")
        return 0

    # Check dependencies
    if not PYTORCH_AVAILABLE:
        LOG.error("[Error] PyTorch not available — training cannot start.")
        if PYTORCH_IMPORT_ERROR is not None:
            LOG.error(
                "[Error] Import failed: %s: %s",
                type(PYTORCH_IMPORT_ERROR).__name__,
                PYTORCH_IMPORT_ERROR,
            )
        LOG.error("[Hint] See [Warning] / [Hint] lines above for diagnostic guidance.")
        # Why os._exit(1) instead of `return 1`/`sys.exit(1)`:
        # When torch's native DLLs partially load and then fail, the Python
        # interpreter's normal shutdown path (atexit handlers, gc finalizers,
        # cleanup of half-initialized C extensions) can dereference torn-down
        # state and crash with STATUS_ACCESS_VIOLATION (0xC0000005, exit code
        # -1073741819). That crash masks our clean error message in the UI
        # log and looks like the trainer itself crashed. os._exit bypasses
        # that cleanup entirely — the process dies immediately with our
        # intended exit code, and the user sees the [Error] / [Hint] lines.
        os._exit(1)

    if not MODELS_AVAILABLE:
        LOG.error("[Error] models_pytorch.py not found")
        return 1

    data_dir = Path(args.data)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not data_dir.exists():
        LOG.error(f"[Error] Data directory not found: {data_dir}")
        return 1

    device = torch.device("cpu") if args.cpu else get_device()

    LOG.info(hr("BOT-MMORPG-AI TRAINING"))
    LOG.info(f"Data dir     : {data_dir.resolve()}")
    LOG.info(f"Artifacts dir: {out_dir.resolve()}")
    LOG.info(f"Model        : {args.model}")
    LOG.info(f"Device       : {device}")

    model_info = get_model_info(args.model)
    is_temporal = model_info.get("temporal", False)
    seq_len = args.seq_len if is_temporal else 1
    LOG.info(f"Temporal     : {is_temporal} (seq_len={seq_len})")
    LOG.info(hr())

    # Create dataset
    LOG.info("Loading data...")
    try:
        dataset = GameplayDataset(data_dir, seq_len=seq_len, limit_files=args.limit_files)
    except ValueError as e:
        LOG.error(f"[Error] {e}")
        return 1

    # Split train/val
    total_size = len(dataset)
    val_size = int(total_size * args.val_split)
    train_size = total_size - val_size

    if train_size <= 0:
        LOG.error("[Error] Not enough samples to train. Try collecting more data or lowering --val-split.")
        return 1

    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    LOG.info(f"Train samples : {len(train_dataset)}")
    LOG.info(f"Val samples   : {len(val_dataset)}")

    # Fit the batch size to the GPU actually present, and turn on mixed
    # precision where it helps (issue #27). --no-autotune skips the whole
    # thing so an advanced user's --batch-size is used verbatim.
    if args.no_autotune:
        batch_size, use_amp, use_grad_ckpt = args.batch_size, args.amp, False
        LOG.info(f"[Auto] Disabled — using --batch-size {batch_size} as given")
    else:
        batch_size, use_amp, use_grad_ckpt = autotune_batch_size(
            args.batch_size, device
        )
        use_amp = use_amp or args.amp

    # Dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=(device.type == "cuda"),
    )

    val_loader = (
        DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
        if val_size > 0 else None
    )

    # Resolve the output-head size. Prefer the value auto-detected from
    # the dataset so the model head always matches the recorded action
    # vector (29 keyboard+gamepad, or 39 when mouse recording is on).
    # A positive --num-actions overrides it for advanced use. This fixes
    # the "Target size ... must be the same as input size" crash (#64).
    num_actions = args.num_actions if args.num_actions > 0 else dataset.num_actions
    LOG.info(f"Action vector size: {num_actions}")
    if num_actions > 29:
        mouse_extra = num_actions - 29
        LOG.info(f"  (keyboard=9 + gamepad=20 + mouse={mouse_extra})")

    # Create model
    LOG.info(f"Creating model: {args.model}")
    model = get_model(
        args.model,
        num_actions=num_actions,
        temporal_frames=seq_len,
        pretrained=not args.no_pretrained,
    )

    LOG.info(f"Parameters   : {count_parameters(model):,}")
    LOG.info("Starting training...")
    LOG.info("NOTE: Artifacts will be saved as .pth into the artifacts dir above.")

    train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        epochs=args.epochs,
        learning_rate=args.lr,
        save_dir=out_dir,
        model_name=args.model,
        use_amp=use_amp,
        use_gradient_checkpointing=use_grad_ckpt,
    )

    LOG.info(hr("TRAINING COMPLETE"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
