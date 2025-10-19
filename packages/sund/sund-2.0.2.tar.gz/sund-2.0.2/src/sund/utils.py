# ruff: noqa: E501
# ignore line length as we have long error messages

"""Utility functions for the sund package.

All output previously printed to stdout now uses the standard ``logging``
framework. Configure logging in the host application, e.g.::

    import logging
    logging.basicConfig(level=logging.INFO)

"""

import importlib
import logging
import unittest
from pathlib import Path

logger = logging.getLogger(__name__)


def test_distribution():  # noqa: C901
    """
    Test that all essential sund modules can be imported.

    This function can be used to verify that the sund package
    has been correctly installed from a source or binary distribution.

    Returns:
        bool: True if all tests pass, False otherwise
    """

    temp_model_name = "temp_model_remove_me"
    logger.info("\n%s", "=" * 80)
    logger.info("Starting sund distribution test...")
    logger.info("This test verifies that all critical modules can be imported.")
    logger.info("%s\n", "=" * 80)

    class _PackageInstallTest(unittest.TestCase):
        def test_module_imports(self):
            """Test that all critical modules can be imported."""
            # Test core module imports
            modules = [
                "sund._Activity",
                "sund._debug",
                "sund._Models",
                "sund._Simulation",
                "sund._StringList",
            ]

            for module_name in modules:
                try:
                    importlib.import_module(module_name)
                    logger.info("✓ Successfully imported %s", module_name)
                except ImportError as e:
                    logger.exception("✗ Failed to import %s", module_name)
                    self.fail(f"Failed to import {module_name}: {e}")

            # Verify version attribute exists
            import sund  # noqa: PLC0415

            if not hasattr(sund, "__version__"):
                msg = "sund package is missing __version__ attribute"
                raise RuntimeError(msg)

            logger.info("✓ Found sund package version: %s", sund.__version__)

        def test_model_compilation_and_simulation(self):
            """Test that all critical modules can be imported."""

            temp_model_file = f"{temp_model_name}.txt"

            # Create a temporary model file
            try:
                import sund  # noqa: PLC0415

                sund.save_model_template(file_name=temp_model_file, model_name=temp_model_name)
                logger.info("✓ Model template %s saved successfully", temp_model_name)
            except Exception as e:
                logger.exception("✗ Failed to save model template %s", temp_model_name)
                self.fail(f"Failed to save model template {temp_model_name}: {e}")

            # Install the model file
            try:
                sund.install_model(temp_model_file)
                logger.info("✓ Model %s installed successfully", temp_model_name)
            except Exception as e:
                logger.exception("✗ Failed to install model %s", temp_model_name)
                self.fail(f"Failed to install model {temp_model_name}: {e}")

            # Load the model
            try:
                model = sund.load_model(temp_model_name)
                logger.info("✓ Model %s loaded successfully", temp_model_name)
            except Exception as e:
                logger.exception("✗ Failed to load model %s", temp_model_name)
                self.fail(f"Failed to load model {temp_model_name}: {e}")

            # Create a simulation
            try:
                simulation = sund.Simulation(models=[model], time_vector=[0, 1, 2])
                logger.info("✓ Simulation for model %s created successfully", temp_model_name)
            except Exception as e:
                logger.exception("✗ Failed to create simulation for model %s", temp_model_name)
                self.fail(f"Failed to create simulation for model {temp_model_name}: {e}")

            # Simulate the model
            try:
                simulation.simulate()
                logger.info("✓ Simulation for model %s completed successfully", temp_model_name)
            except Exception as e:
                logger.exception("✗ Failed to simulate model %s", temp_model_name)
                self.fail(f"Failed to simulate model {temp_model_name}: {e}")

            # Validate the simulation
            try:
                value = simulation.feature_values[-1, 0]
            except Exception as e:
                logger.exception("✗ Failed to access feature values for model %s", temp_model_name)
                self.fail(f"Failed to validate simulation for model {temp_model_name}: {e}")
            else:
                if value <= 0:
                    msg = f"Expected feature value at [-1, 0] to be > 0 (got {value})"
                    logger.error(
                        "✗ Failed to validate simulation for model %s: %s",
                        temp_model_name,
                        msg,
                    )
                    self.fail(f"Failed to validate simulation for model {temp_model_name}: {msg}")
                else:
                    logger.info("✓ Simulation for model %s validated successfully", temp_model_name)

            # Clean up the temporary model file
            try:
                Path(temp_model_file).unlink()
                logger.info("✓ Temporary model file %s removed successfully", temp_model_file)
            except Exception as e:
                logger.exception("✗ Failed to remove temporary model file %s", temp_model_file)
                self.fail(f"Failed to remove temporary model file {temp_model_file}: {e}")

    # Run the tests but capture the result
    suite = unittest.TestLoader().loadTestsFromTestCase(_PackageInstallTest)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    success = result.wasSuccessful()

    logger.info(
        "\nNOTE: it is not possible to remove the compiled model that was installed during this test without restarting python.\nRemove the model by running:\nsund.uninstall_model('%s')",
        temp_model_name,
    )

    logger.info("\n%s", "=" * 80)
    if success:
        logger.info(
            "✅ DISTRIBUTION TEST PASSED: All sund modules imported successfully, and model simulation completed without errors.",
        )
    else:
        logger.error(
            "❌ DISTRIBUTION TEST FAILED: Some sund modules could not be imported, or model simulation encountered errors.",
        )
    logger.info("%s\n", "=" * 80)

    return success
