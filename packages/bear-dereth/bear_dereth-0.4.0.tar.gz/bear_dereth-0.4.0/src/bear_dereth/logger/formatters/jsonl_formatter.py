"""Module providing a JSON Lines formatter for log records."""

import json

from bear_dereth.logger.protocols.formatter import Formatter
from bear_dereth.logger.records.record import LoggerRecord


class JSONLFormatter(Formatter):
    """A formatter that outputs log records in JSON Lines format."""

    # TODO: Make this configurable to include/exclude certain fields

    def format(self, record: LoggerRecord, **kwargs) -> str:  # type: ignore[override]
        """Format a log record as a JSON Lines string."""
        log_entry = super().format(record, as_dict=True, **kwargs)
        return json.dumps(log_entry)
