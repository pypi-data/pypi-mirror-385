"""
Image Classification Task - Complete Pipeline Implementation

This module provides a complete image classification pipeline including dataset handling,
model architectures, training logic, and factory pattern integration. It supports both
local and remote datasets, custom CNN models, and pre-trained models via TIMM.

Features:
    - Flexible dataset loading (local directories, URLs, CIFAR-10)
    - Automatic dataset download and extraction (ZIP, TAR.GZ formats)
    - Dynamic input dimension detection and model adaptation
    - Custom CNN architecture with configurable parameters
    - TIMM integration for pre-trained model support
    - Configurable image transformations (resize, grayscale, normalization)
    - Factory pattern integration for seamless task registration

Components:
    - ImageClassificationDataset: Handles data loading, downloading, and preprocessing
    - ImageClassificationModel: Custom CNN architecture with dynamic sizing
    - TimmModelWrapper: Wrapper for TIMM pre-trained models
    - ImageClassificationTrainer: Training logic specific to image classification
    - ImageClassificationFactory: Factory for creating task components

Key methods:
    Dataset:
        - **__init__**: Initializes dataset with configuration and transforms
        - load_dataset: Loads data from various sources (local, URL, CIFAR-10)
        - _get_transforms: Creates image transformation pipeline from config
        - _download_and_extract: Downloads and extracts remote datasets
    
    Models:
        - **__init__**: Initializes model architecture with dynamic input sizing
        - forward: Forward pass through the network
        - save/load: Model persistence methods
    
    Factory:
        - create_dataset: Creates and configures dataset instance
        - create_model: Creates model (custom CNN or TIMM) based on configuration
        - create_trainer: Assembles complete training pipeline

Usage:
    # Via AutoTrainer (recommended)
    config = {
        "task": "image_classification",
        "dataset_config": {
            "source": "path/to/images",  # or URL or "cifar-10"
            "transform_config": {
                "resize": (224, 224),
                "normalize_mean": [0.485, 0.456, 0.406],
                "normalize_std": [0.229, 0.224, 0.225]
            }
        },
        "model_config": {
            "type": "timm",
            "name": "resnet18",
            "pretrained": True
        },
        "batch_size": 32,
        "epochs": 50,
        "lr": 0.001
    }
    trainer = AutoTrainer(config=config)
    trainer.run()

Architecture:
    The module follows a layered architecture:
    1. Dataset layer handles data loading and preprocessing
    2. Model layer provides flexible architecture options
    3. Trainer layer implements classification-specific training logic
    4. Factory layer orchestrates component creation and configuration

Supported Data Sources:
    - Local directories (ImageFolder format)
    - Remote URLs (automatic download and extraction)
    - Built-in datasets (CIFAR-10)
    - Supported archive formats: ZIP, TAR.GZ, TGZ
        
Dependencies:
    - torch: PyTorch deep learning framework
    - torchvision: Computer vision utilities and datasets
    - timm: PyTorch Image Models for pre-trained architectures
    - requests: HTTP library for dataset downloading
    - PIL/Pillow: Image processing (via torchvision)

"""

# third party
import torch
import torchvision
from torchvision import transforms
from torchvision.datasets import ImageFolder
import timm

# local modules
from ml_trainer.base import BaseDataset, AbstractModelArchitecture
from ml_trainer.trainer import BaseTrainer
from ml_trainer.tasks.task_factory import AbstractTaskFactory
# from ml_trainer.tasks.task_registry import register_task

# ======================= DATASET =======================

from torchvision.datasets import ImageFolder
from urllib.parse import urlparse
import os
import requests
import zipfile
import tarfile

class ImageClassificationDataset(BaseDataset):
    def __init__(self, config, batch_size: int, split_ratio: float):
        super().__init__(config=config, batch_size=batch_size, split_ratio=split_ratio)
        self.transform = self._get_transforms(self.config.get("transform_config", {}))

    def _get_transforms(self, transform_config: dict):
        transform_list = []
        if "resize" in transform_config:
            transform_list.append(transforms.Resize(transform_config["resize"]))
        if transform_config.get("grayscale", False):
            transform_list.append(transforms.Grayscale())
        transform_list.append(transforms.ToTensor())
        if "normalize_mean" in transform_config and "normalize_std" in transform_config:
            transform_list.append(transforms.Normalize(
                transform_config["normalize_mean"],
                transform_config["normalize_std"]
            ))
        return transforms.Compose(transform_list)

    def load_dataset(self):
        source = self.config.get("source")
        s = source.lower()
        if not source:
            raise ValueError("dataset_config must include 'source'")

        if "cifar-10" in source.lower():
            dataset = torchvision.datasets.CIFAR10(
                root="data/cifar-10",
                train=True,
                transform=self.transform,
                download=True,
            )
        
        elif "stl10" in s or s == "stl10":
            # use torchvision’s official STL10 dataset instead of ImageFolder
            dataset = torchvision.datasets.STL10(
                root="data/stl10",
                split="train",           # "train" | "test" | "unlabeled"
                transform=self.transform,
                download=True,
            )
        
        else:
            parsed = urlparse(source)
            if parsed.scheme in ("http", "https"):
                local_path = self._download_and_extract(source)
            else:
                local_path = source
            print('image folder')
            dataset = ImageFolder(root=local_path, transform=self.transform)

        # parsed = urlparse(source)
        # if parsed.scheme in ("http", "https"):
        #     local_path = self._download_and_extract(source)
        # else:
        #     local_path = source

        # dataset = ImageFolder(root=local_path, transform=self.transform)
        
        # --- Auto detect channels from first sample
        sample_img, label = dataset[0]
        self.input_channels = sample_img.shape[0]
        # Detect channels and size
        self.input_channels = sample_img.shape[0]
        self.input_size = sample_img.shape[1:]
        self.num_classes = len(dataset.classes)
  # C x H x W
        return dataset

    # def _download_and_extract(self, url: str):
    #     os.makedirs("data", exist_ok=True)
    #     filename = os.path.basename(url)
    #     dataset_name = filename.split(".")[0]
    #     dataset_dir = os.path.join("data", dataset_name)
    #     os.makedirs(dataset_dir, exist_ok=True)

    #     archive_path = os.path.join(dataset_dir, filename)

    #     # Download if not already there
    #     if not os.path.exists(archive_path):
    #         print(f"Downloading dataset from {url}")
    #         r = requests.get(url)
    #         with open(archive_path, "wb") as f:
    #             f.write(r.content)

    #         # Extract the archive
    #         if filename.endswith(".zip"):
    #             with zipfile.ZipFile(archive_path, 'r') as zip_ref:
    #                 zip_ref.extractall(dataset_dir)
    #         elif filename.endswith((".tar.gz", ".tgz")):
    #             with tarfile.open(archive_path, "r:gz") as tar:
    #                 tar.extractall(dataset_dir)
    #         else:
    #             raise ValueError(f"Unsupported archive format: {filename}")

    #     # Find extracted folder
    #     extracted_dirs = [os.path.join(dataset_dir, name) for name in os.listdir(dataset_dir)
    #                     if os.path.isdir(os.path.join(dataset_dir, name))]

    #     if len(extracted_dirs) == 1:
    #         return extracted_dirs[0]  # e.g. cifar-10-batches-py
    #     return dataset_dir

    def _download_and_extract(self, url: str) -> str:
        """Download and extract dataset from URL."""
        import os
        import requests
        import tarfile
        import zipfile
        from urllib.parse import urlparse
        
        # Parse the URL and extract the actual filename
        parsed_url = urlparse(url)
        
        # Get filename from path, removing query parameters
        filename = os.path.basename(parsed_url.path)
        
        # If filename is empty or doesn't have an extension, try to get it from URL
        if not filename or '.' not in filename:
            # Extract from the full path
            path_parts = parsed_url.path.strip('/').split('/')
            for part in reversed(path_parts):
                if '.' in part and any(ext in part.lower() for ext in ['.tar.gz', '.zip', '.tar', '.tgz']):
                    filename = part
                    break
        
        # Create downloads directory
        download_dir = "data/downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        # Full path for downloaded file
        file_path = os.path.join(download_dir, filename)
        
        # Extract directory name (without extension)
        if filename.endswith('.tar.gz'):
            extract_name = filename[:-7]  # Remove .tar.gz
        elif filename.endswith('.tgz'):
            extract_name = filename[:-4]  # Remove .tgz
        elif filename.endswith('.zip'):
            extract_name = filename[:-4]  # Remove .zip
        elif filename.endswith('.tar'):
            extract_name = filename[:-4]  # Remove .tar
        else:
            extract_name = filename
        
        extract_path = os.path.join(download_dir, extract_name)
        
        # Check if already extracted
        if os.path.exists(extract_path):
            print(f"Dataset already exists at {extract_path}")
            return extract_path
        
        # Download file if it doesn't exist
        if not os.path.exists(file_path):
            print(f"Downloading dataset from {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # Get list of directories before extraction
        dirs_before = set()
        if os.path.exists(download_dir):
            dirs_before = {
                item for item in os.listdir(download_dir) 
                if os.path.isdir(os.path.join(download_dir, item))
            }
        
        # Extract based on actual filename (not URL with parameters)
        print(f"Extracting {filename}")
        
        if filename.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(file_path, 'r:gz') as tar:
                tar.extractall(path=download_dir)
        elif filename.endswith('.tar'):
            with tarfile.open(file_path, 'r') as tar:
                tar.extractall(path=download_dir)
        elif filename.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
        else:
            raise ValueError(f"Unsupported archive format: {filename}")
        
        # Find newly created directories
        dirs_after = {
            item for item in os.listdir(download_dir) 
            if os.path.isdir(os.path.join(download_dir, item))
        }
        new_dirs = dirs_after - dirs_before
        
        # First, check if the expected directory exists
        if os.path.exists(extract_path):
            return extract_path
        
        # Look for newly created directories
        if len(new_dirs) == 1:
            return os.path.join(download_dir, list(new_dirs)[0])
        elif len(new_dirs) > 1:
            # Try to find the most likely candidate
            for dir_name in new_dirs:
                full_path = os.path.join(download_dir, dir_name)
                # Check if it contains image files or subdirectories (for ImageFolder)
                if os.path.isdir(full_path):
                    contents = os.listdir(full_path)
                    # Look for subdirectories (classes) or image files
                    has_subdirs = any(os.path.isdir(os.path.join(full_path, item)) for item in contents)
                    has_images = any(item.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')) for item in contents)
                    
                    if has_subdirs or has_images:
                        return full_path
            
            # Fall back to first new directory
            return os.path.join(download_dir, list(new_dirs)[0])
        else:
            # No new directories found, check if files were extracted directly to download_dir
            return download_dir


# ======================= MODEL =======================
class ImageClassificationModel(AbstractModelArchitecture, torch.nn.Module):
    def __init__(self, num_classes=10, input_channels=3, input_size=(32, 32)):
        super().__init__()
        
        self.features = torch.nn.Sequential(
            torch.nn.Conv2d(input_channels, 32, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),  # Halves H and W
        )

        # Dynamically determine the flattened size after conv layers
        with torch.no_grad():
            dummy_input = torch.zeros(1, input_channels, *input_size)
            output = self.features(dummy_input)
            flattened_size = output.view(1, -1).shape[1]

        self.classifier = torch.nn.Sequential(
            torch.nn.Flatten(),
            torch.nn.Linear(flattened_size, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, num_classes),
        )

        self.model = torch.nn.Sequential(self.features, self.classifier)

    def forward(self, x):
        return self.model(x)

    def save(self, path):
        torch.save(self.state_dict(), path)

    def load(self, path):
        self.load_state_dict(torch.load(path))

class TimmModelWrapper(torch.nn.Module):
    def __init__(self, model_name: str, num_classes: int, pretrained=True):
        super().__init__()
        self.model = timm.create_model(model_name, pretrained=pretrained, num_classes=num_classes)

    def forward(self, x):
        return self.model(x)
    
    def save(self, path):
        torch.save(self.state_dict(), path)

    def load(self, path):
        self.load_state_dict(torch.load(path))


# ======================= TRAINER =======================

class ImageClassificationTrainer(BaseTrainer):
    def training_step(self, batch):
        inputs, labels = self.prepare_batch(*batch)
        outputs = self.model(inputs)
        return self.loss_fn(outputs, labels)

    def validation_step(self, batch):
        inputs, labels = self.prepare_batch(*batch)
        outputs = self.model(inputs)
        return self.loss_fn(outputs, labels)

# ======================= FACTORY =======================

# @register_task("image_classification")
class ImageClassificationFactory(AbstractTaskFactory):
    def create_dataset(self, config):
        dataset_cfg = config.get("dataset_config", {})
        dataset = ImageClassificationDataset(
            batch_size=config.get("batch_size", 32),
            split_ratio=config.get("split_ratio", 0.8),
            config=dataset_cfg,
        )
        _ = dataset.get_dataloaders()  # triggers load and sets input_channels

        config["input_channels"] = dataset.input_channels
        config["input_size"] = dataset.input_size
        config["num_classes"] = config.get("num_classes") or dataset.num_classes

        return dataset

    def create_model(self, config):
        model_cfg = config.get("model_config", {})

        if model_cfg.get("type") == "timm":
            # model_name = model_cfg.get("name", "resnet18")
            # pretrained = model_cfg.get("pretrained", True)
            model_name = model_cfg.get("name")
            pretrained = model_cfg.get("pretrained")
            return TimmModelWrapper(
                model_name=model_name,
                num_classes=config.get("num_classes"),
                pretrained=pretrained
            )

        # Default fallback
        return ImageClassificationModel(
            num_classes=config.get("num_classes", 10),
            input_channels=config.get("input_channels"),
            input_size=config.get("input_size"),
        )


    def create_trainer(self, model, dataset, config):
        train_loader, val_loader = dataset.get_dataloaders()
        optimizer = torch.optim.Adam(model.parameters(), lr=config.get("lr", 1e-3))
        loss_fn = torch.nn.CrossEntropyLoss()

        return ImageClassificationTrainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            optimizer=optimizer,
            loss_fn=loss_fn,
            epochs=config.get("epochs", 10),
            device=config.get("device"),
            log_dir=config.get("log_dir"),
            checkpoint_path=config.get("checkpoint_path"),
            config=config,
        )