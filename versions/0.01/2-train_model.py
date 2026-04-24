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
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("[Warning] PyTorch not installed. Install with: pip install torch torchvision")

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

class GameplayDataset(Dataset):
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

        dt = time.time() - t0
        LOG.info(f"[Dataset] Loaded {len(self.frames)} sample(s) in {dt:.1f}s")
        LOG.info(f"[Dataset] Skipped files: {skipped_files}, skipped items: {skipped_items}")
        LOG.info(f"[Dataset] Frame shape: {self.frames[0].shape}")
        LOG.info(f"[Dataset] Action shape: {self.actions[0].shape}")

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

def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    epoch: int,
    log_every_batches: int = 10,
) -> float:
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    num_batches = len(dataloader)

    if num_batches == 0:
        return 0.0

    for batch_idx, (frames, actions) in enumerate(dataloader, start=1):
        frames = frames.to(device)
        actions = actions.to(device)

        optimizer.zero_grad()
        outputs = model(frames)
        loss = criterion(outputs, actions)
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()
        total_loss += loss.item()

        if (batch_idx % log_every_batches == 0) or (batch_idx == num_batches):
            LOG.info(f"    [Epoch {epoch}] Batch {batch_idx:>4}/{num_batches} | loss={loss.item():.4f}")

    return total_loss / num_batches


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


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: Optional[DataLoader],
    device: torch.device,
    epochs: int = 10,
    learning_rate: float = 1e-4,
    save_dir: Path = Path("artifacts/model"),
    model_name: str = "model",
) -> nn.Module:
    """Full training loop with validation and checkpointing."""
    model = model.to(device)

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
    parser.add_argument("--num-actions", type=int, default=29, help="Number of output actions")
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
        LOG.error("[Error] PyTorch not available. Install with: pip install torch torchvision")
        return 1

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

    # Dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=(device.type == "cuda"),
    )

    val_loader = (
        DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
        if val_size > 0 else None
    )

    # Create model
    LOG.info(f"Creating model: {args.model}")
    model = get_model(
        args.model,
        num_actions=args.num_actions,
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
    )

    LOG.info(hr("TRAINING COMPLETE"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
