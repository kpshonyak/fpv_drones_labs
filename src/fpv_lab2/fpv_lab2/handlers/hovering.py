import time
from typing import TYPE_CHECKING

from ..flight_state import FlightState
from .handler import FlightStateHandler

if TYPE_CHECKING:
    from ..flight_test_node import FlightTestNode


class HoveringHandler(FlightStateHandler):
    def __init__(self):
        # Повідомлення статусу, яке було актуальним на початку зависання
        self._status_at_start = None

    def handle(self, node: "FlightTestNode") -> None:
        if node.status is None:
            return

        if self._status_at_start is None:
            self._status_at_start = node.status

        # Перевіряємо armed лише коли прийшло СВІЖЕ повідомлення статусу:
        # старе могло бути отримане ще до озброєння (armed=False)
        status_is_fresh = node.status is not self._status_at_start
        if status_is_fresh and not node.status.armed:
            node.fail("Drone disarmed unexpectedly during flight")
            return

        if node.odometry is not None:
            altitude = node.odometry.pose.pose.position.z
            node.get_logger().debug(
                f"Gazebo altitude: {altitude:.2f} m"
            )

        elapsed = time.monotonic() - node.hover_started_at
        if elapsed >= node.HOVER_DURATION:
            node.get_logger().info("Hover completed, starting flight to target")
            node.state = FlightState.FLYING