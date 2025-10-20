"""
This module contains the ScanHistory class, which is used to manage the scan history.
"""

from __future__ import annotations

import os
import threading
from typing import TYPE_CHECKING

from bec_lib.callback_handler import EventType
from bec_lib.endpoints import MessageEndpoints
from bec_lib.scan_data_container import ScanDataContainer

if TYPE_CHECKING:  # pragma: no cover
    from bec_lib import messages
    from bec_lib.client import BECClient


class ScanHistory:
    """Class to manage the scan history."""

    def __init__(self, client: BECClient, load_threaded: bool = True) -> None:
        """
        Initialize the ScanHistory class.

        Args:
            client (BECClient): The BEC client providing the redis connector.
            load_threaded (bool, optional): Whether to load the scan history in a separate thread. Defaults to
                True.
        """
        self._connector = client.connector
        self._client = client
        self._load_threaded = load_threaded
        self._scan_data = {}
        self._scan_ids = []
        self._scan_numbers = []
        self._scan_data_lock = threading.RLock()
        self._scan_history_loaded_event = threading.Event()
        self._loaded = False
        self._loading_thread = None
        self._max_scans = 10000
        self._start_retrieval()

    def _start_retrieval(self) -> None:
        if self._load_threaded:
            self._loading_thread = threading.Thread(
                target=self._load_data, daemon=True, name="ScanHistoryLoader"
            )
            self._loading_thread.start()
        else:
            self._load_data()
        self._connector.register(
            MessageEndpoints.scan_history(), cb=self._on_scan_history_update, parent=self
        )

    def _load_data(self) -> None:
        data = self._connector.xread(
            MessageEndpoints.scan_history(), from_start=True, user_id="ScanHistoryLoader"
        )
        if not data:
            self._scan_history_loaded_event.set()
            return
        with self._scan_data_lock:
            for entry in data:
                msg: messages.ScanHistoryMessage = entry["data"]
                if not os.access(msg.file_path, os.R_OK):
                    # If the file is not readable, we skip adding it to the history
                    continue
                self._scan_data[msg.scan_id] = msg
                self._scan_ids.append(msg.scan_id)
                self._scan_numbers.append(msg.scan_number)
                self._remove_oldest_scan()
            self._client.callbacks.run(
                event_type=EventType.SCAN_HISTORY_LOADED,
                history_msgs=[self._scan_data[scan_id] for scan_id in self._scan_ids],
            )
            self._scan_history_loaded_event.set()

    def _remove_oldest_scan(self) -> None:
        while len(self._scan_ids) > self._max_scans:
            scan_id = self._scan_ids[0]
            self._scan_data.pop(scan_id, None)
            self._scan_ids.pop(0)
            if self._scan_numbers:
                self._scan_numbers.pop(0)

    @staticmethod
    def _on_scan_history_update(msg: dict, parent: ScanHistory) -> None:
        # pylint: disable=protected-access
        with parent._scan_data_lock:
            msg: messages.ScanHistoryMessage = msg["data"]
            if not os.access(msg.file_path, os.R_OK):
                # If the file is not readable, we skip adding it to the history
                return
            parent._client.callbacks.run(event_type=EventType.SCAN_HISTORY_UPDATE, history_msg=msg)
            parent._scan_data[msg.scan_id] = msg
            parent._scan_ids.append(msg.scan_id)
            parent._scan_numbers.append(msg.scan_number)
            parent._remove_oldest_scan()

    def get_by_scan_id(self, scan_id: str) -> ScanDataContainer | None:
        """Get the scan data by scan ID."""
        with self._scan_data_lock:
            target_id = self._scan_data.get(scan_id)
            if not target_id:
                return None
            return ScanDataContainer(file_path=target_id.file_path, msg=target_id)

    def get_by_scan_number(
        self, scan_number: int
    ) -> ScanDataContainer | list[ScanDataContainer] | None:
        """Get the scan data by scan number."""
        out = []
        with self._scan_data_lock:
            for scan in self._scan_data.values():
                if scan.scan_number == scan_number:
                    out.append(ScanDataContainer(file_path=scan.file_path, msg=scan))
        if len(out) == 1:
            return out[0]
        return out if out else None

    def get_by_dataset_number(self, dataset_number: str) -> list[ScanDataContainer] | None:
        """Get the scan data by dataset number."""
        with self._scan_data_lock:
            out: list[ScanDataContainer] = []
            for scan in self._scan_data.values():
                if scan.dataset_number == dataset_number:
                    out.append(ScanDataContainer(file_path=scan.file_path, msg=scan))
            if out:
                return out
        return None

    def __len__(self) -> int:
        with self._scan_data_lock:
            return len(self._scan_ids)

    def __getitem__(self, index: int | slice) -> ScanDataContainer | list[ScanDataContainer]:
        with self._scan_data_lock:
            if isinstance(index, int):
                target_id = self._scan_ids[index]
                return self.get_by_scan_id(target_id)
            if isinstance(index, slice):
                return [self.get_by_scan_id(scan_id) for scan_id in self._scan_ids[index]]
            raise TypeError("Index must be an integer or slice.")

    def _shutdown(self) -> None:
        """Shutdown the ScanHistory."""
        if self._loading_thread and self._loading_thread.is_alive():
            self._loading_thread.join()
