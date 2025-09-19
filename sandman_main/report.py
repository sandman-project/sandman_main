"""Everything needed to support reports.

Reports are automatically generated based on activity.
"""

import logging
import pathlib

_logger = logging.getLogger("sandman.report")


def bootstrap_reports(base_dir: str) -> None:
    """Handle bootstrapping for reports."""
    report_path = pathlib.Path(base_dir + "reports/")

    if report_path.exists() == True:
        return

    _logger.info("Creating missing report directory '%s'.", str(report_path))

    try:
        report_path.mkdir()

    except Exception:
        _logger.warning(
            "Failed to create report directory '%s'.", str(report_path)
        )
        return
