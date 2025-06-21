"""
Text Gauntlet - Modern Sentiment Analysis Application

A comprehensive sentiment analysis tool that provides multiple ways to analyze
text emotions and sentiments including direct text input, song lyrics analysis,
and movie reviews analysis.

Version: 2.0.0
Authors: Montaser Amoor aka sshussh
"""

import sys
import traceback
from pathlib import Path

# Add src directory to Python path for imports
srcPath = Path(__file__).parent
if str(srcPath) not in sys.path:
    sys.path.insert(0, str(srcPath))

# Import after path setup
from config.settings import settings  # noqa: E402
from utils.exceptions import TextGauntletError  # noqa: E402
from utils.logger import Logger, logger  # noqa: E402


def main() -> None:
    """Main entry point for Text Gauntlet application."""
    try:
        # Configure root logger for consistent formatting
        Logger.configure_root_logger()

        logger.info("Starting Text Gauntlet v2.0.0")
        logger.info(f"Configuration loaded: {settings.ui.defaultTheme} theme")

        # Initialize services
        from services.application_services import services

        services.initialize()
        logger.info("Services initialized successfully")

        # Import UI components after services are set up
        from ui.main_window import TextGauntletApp

        # Create and run application
        app = TextGauntletApp()
        logger.info("Application initialized successfully")

        # Start the main loop
        app.run()

        # Shutdown services when app closes
        services.shutdown()

    except TextGauntletError as e:
        logger.error(f"Application error: {e.message} (Code: {e.errorCode})")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        # Ensure services are shutdown
        try:
            from services.application_services import services

            services.shutdown()
        except Exception:
            pass
        sys.exit(0)

    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

    finally:
        logger.info("Text Gauntlet application ended")


if __name__ == "__main__":
    main()
