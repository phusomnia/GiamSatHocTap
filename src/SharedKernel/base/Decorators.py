import importlib
import os
import sys
from functools import wraps
from pathlib import Path
from typing import Callable, TypeVar, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI
from src.SharedKernel.base.Logger import get_logger
from src.SharedKernel.base import Metrics
import inspect

T = TypeVar('T')

# Registry to store controller classes
_controllers_registry: list[type] = []

def Controller(cls: T) -> T:
    """
    Decorator to mark a class as a controller.
    Controllers will be automatically registered with the FastAPI app.
    """
    _controllers_registry.append(cls)
    return cls

logger = get_logger(__name__)

def _import_controller_module(module_path: str, feature_name: str, file_name: str) -> None:
    """Import a single controller module given its dotted path."""
    try:
        importlib.import_module(module_path)
        logger.info(f"Imported {Path(file_name).stem} from {feature_name}")
    except Exception as e:
        logger.error(f"❌ Failed to import {Path(file_name).stem} from {feature_name}/{file_name}: {e}")
        logger.error(f"📁 Module path attempted: {module_path}")
        import traceback
        logger.error(f"🔍 Full traceback:\n{traceback.format_exc()}")

def _scan_directory_for_controllers(base_dir: Path, base_module: str, feature_name: str) -> None:
    """Recursively scan a directory for *controller.py files."""
    try:
        with os.scandir(str(base_dir)) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith('controller.py'):
                    module_name = Path(entry.name).stem
                    module_path = f"{base_module}.{module_name}"
                    _import_controller_module(module_path, feature_name, entry.name)
                elif entry.is_dir() and not entry.name.startswith('__'):
                    sub_module = f"{base_module}.{entry.name}"
                    _scan_directory_for_controllers(
                        Path(entry.path), sub_module, feature_name
                    )
    except OSError as e:
        logger.error(f"❌ Error scanning directory {base_dir}: {e}")

def auto_import_controllers() -> None:
    """
    Automatically import all controllers from the Features directory.
    Recursively scans for files matching pattern '*controller.py' in feature directories.
    """
    src_path = Path(__file__).parent.parent.parent # Go up to src directory
    features_path = src_path / "Features"
    
    if not features_path.exists():
        logger.warning("Features directory not found")
        return
    
    logger.info("Scanning for controllers...")
    
    try:
        with os.scandir(str(features_path)) as feature_entries:
            for feature_entry in feature_entries:
                if not feature_entry.is_dir():
                    continue
                _scan_directory_for_controllers(
                    Path(feature_entry.path),
                    f"src.Features.{feature_entry.name}",
                    feature_entry.name
                )
    except OSError as e:
        logger.error(f"❌ Error scanning directories: {e}")


def _register_single_controller(app: FastAPI, controller_class: type, container) -> None:
    """Register a single controller with the FastAPI app."""
    if not hasattr(controller_class, 'register'):
        raise AttributeError(
            f"❌ Controller {controller_class.__name__} must have a 'register' method"
        )

    # Check if controller expects container parameter
    sig = inspect.signature(controller_class.__init__)
    params = [p for p in sig.parameters.values() if p.name != 'self']
    print(params)

    if len(params) == 1 and params[0].name == 'container' and params[0].annotation.__name__ == 'Container':
        # Pass container directly to avoid recursive container creation
        controller_instance = controller_class(container=container)
    else:
        # Resolve all dependencies from container
        controller_instance = container.resolve(controller_class)

    controller_instance.register(app)
    logger.info(f"Registered controller: {controller_class.__name__}")

@Metrics.time_function
def register_controllers(app: FastAPI, container) -> None:
    """
    Scan and register all controllers with the FastAPI app.
    Each controller should have a 'register' method that takes the app instance.
    """
    # Import essential modules to ensure they're in sys.modules for container scan

    container.scan_components()
    auto_import_controllers()

    total_controllers = len(_controllers_registry)
    logger.info(f"Starting registration of {total_controllers} controllers...")

    for controller_class in _controllers_registry:
        logger.info(f"controller class: f{controller_class}")
        _register_single_controller(app, controller_class, container)

    logger.info("All controllers registered successfully")


def get_controllers() -> list[type]:
    """Get all registered controller classes"""
    return _controllers_registry
