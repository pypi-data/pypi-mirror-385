"""
This module provides the alarm handler class and its related functionality.
"""

from __future__ import annotations

import enum
import threading
from collections import deque
from typing import TYPE_CHECKING

from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.utils import threadlocked

if TYPE_CHECKING:  # pragma: no cover
    from bec_lib import messages
    from bec_lib.redis_connector import RedisConnector


logger = bec_logger.logger


class Alarms(int, enum.Enum):
    WARNING = 0
    MINOR = 1
    MAJOR = 2


class AlarmException(Exception):
    pass


class AlarmBase(Exception):
    def __init__(
        self, alarm: messages.AlarmMessage, alarm_type: str, severity: Alarms, handled=False
    ) -> None:
        self.alarm = alarm
        self.severity = severity
        self.handled = handled
        self.alarm_type = alarm_type
        super().__init__(self.alarm.content)

    def __str__(self) -> str:
        return (
            f"An alarm has occured. Severity: {self.severity.name}. Source:"
            f" {self.alarm.content['source']}.\n{self.alarm_type}.\n\t"
            f" {self.alarm.content['msg']}"
        )


class AlarmHandler:
    def __init__(self, connector: RedisConnector) -> None:
        self.connector = connector
        self.alarms_stack = deque(maxlen=100)
        self._raised_alarms = deque(maxlen=100)
        self._lock = threading.RLock()

    def start(self):
        """start the alarm handler and its subscriptions"""
        self.connector.register(
            topics=MessageEndpoints.alarm(),
            name="AlarmHandler",
            cb=self._alarm_register_callback,
            parent=self,
        )

    @staticmethod
    def _alarm_register_callback(msg, *, parent, **_kwargs):
        parent.add_alarm(msg.value)

    @threadlocked
    def add_alarm(self, msg: messages.AlarmMessage):
        """Add a new alarm message to the stack.

        Args:
            msg (messages.AlarmMessage): Alarm message that should be added
        """
        severity = Alarms(msg.content["severity"])
        alarm = AlarmBase(
            alarm=msg, alarm_type=msg.content["alarm_type"], severity=severity, handled=False
        )
        if severity > Alarms.MINOR:
            self.alarms_stack.appendleft(alarm)
            logger.debug(alarm)
        else:
            logger.warning(alarm)

    @threadlocked
    def get_unhandled_alarms(self, severity=Alarms.WARNING) -> list:
        """Get all unhandled alarms equal or above a minimum severity.

        Args:
            severity (Alarms, optional): Minimum severity. Defaults to Alarms.WARNING.

        Returns:
            list: List of unhandled alarms

        """
        return [
            alarm for alarm in self.alarms_stack if not alarm.handled and alarm.severity >= severity
        ]

    @threadlocked
    def get_alarm(self, severity=Alarms.WARNING):
        """Get the next alarm

        Args:
            severity (Alarm, optional): Minimum severity. Defaults to Alarms.WARNING.

        Yields:
            AlarmBase: Alarm
        """
        alarms = self.get_unhandled_alarms(severity=severity)
        for alarm in alarms:
            yield alarm

    def raise_alarms(self, severity=Alarms.MAJOR):
        """Raise unhandled alarms with specified severity.

        Args:
            severity (Alarm, optional): Minimum severity. Defaults to Alarms.MAJOR.

        Raises:
            alarms: Alarm exception.
        """
        alarms = self.get_unhandled_alarms(severity=severity)
        if len(alarms) > 0:
            alarm = alarms.pop(0)
            self._raised_alarms.append(alarm)
            raise alarm

    @threadlocked
    def clear(self):
        """clear all alarms from stack"""
        self.alarms_stack.clear()

    def shutdown(self):
        """shutdown the alarm handler"""
        self.connector.shutdown()
