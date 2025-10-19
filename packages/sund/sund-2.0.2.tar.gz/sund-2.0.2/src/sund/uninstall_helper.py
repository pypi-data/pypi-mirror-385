import logging
import shutil
import site
from pathlib import Path

logger = logging.getLogger(__name__)


def handle_error(path, exc):
    logger.warning("Could not remove %s: %s", path, exc)


def cleanup_package_generated_files():
    """Remove any package generated files during uninstall"""

    logger.info("Starting cleanup...")

    # Find all possible locations of the package
    site_packages = [*site.getsitepackages(), site.getusersitepackages()]

    for site_pkg in site_packages:
        site_pkg_path = Path(site_pkg)

        # Remove sund/Models files
        models_dir = site_pkg_path / "sund" / "Models"
        if models_dir.exists():
            shutil.rmtree(models_dir, onexc=handle_error)

        # Remove sund/temp folder
        temp_dir = site_pkg_path / "sund" / "temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir, onexc=handle_error)

    logger.info("Cleanup completed!")


if __name__ == "__main__":
    cleanup_package_generated_files()
