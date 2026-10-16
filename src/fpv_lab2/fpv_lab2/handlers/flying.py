import math
import time
from typing import TYPE_CHECKING

from geometry_msgs.msg import TwistStamped

from ..flight_state import FlightState
from .handler import FlightStateHandler

if TYPE_CHECKING:
    from ..flight_test_node import FlightTestNode


class FlyingHandler(FlightStateHandler):
    DELTA_X = 8.2
    DELTA_Y = 0.8

    MAX_SPEED = 1.0     
    GAIN = 0.5          
    TOLERANCE = 0.2     
    SETTLE_TIME = 8.0   
    LOG_PERIOD = 1.0    

    def __init__(self):
        self.publisher = None
        self.start = None
        self.target = None
        self.reached_at = None
        self.last_log = 0.0

    def handle(self, node: "FlightTestNode") -> None:
        if node.status is None or not node.status.armed:
            node.fail("Drone disarmed unexpectedly during flight")
            return

        if node.odometry is None:
            return

        if self.publisher is None:
            self.publisher = node.create_publisher(
                TwistStamped, "/ap/v1/cmd_vel", 10
            )

        position = node.odometry.pose.pose.position

        if self.target is None:
            self.start = (position.x, position.y)
            self.target = (
                position.x - self.DELTA_X,
                position.y - self.DELTA_Y,
            )
            node.get_logger().info(
                f"Start position: ({self.start[0]:.2f}; {self.start[1]:.2f})"
            )
            node.get_logger().info(
                f"Target position: ({self.target[0]:.2f}; {self.target[1]:.2f})"
            )

        dx = self.target[0] - position.x
        dy = self.target[1] - position.y
        distance = math.hypot(dx, dy)

        # Ціль досягнута: зупиняємось і чекаємо стабілізації
        if self.reached_at is not None or distance <= self.TOLERANCE:
            self.send_velocity(node, 0.0, 0.0)
            if self.reached_at is None:
                self.reached_at = time.monotonic()
                node.get_logger().info(
                    f"Target reached (distance {distance:.2f} m), stopping"
                )
                return
            if time.monotonic() - self.reached_at >= self.SETTLE_TIME:
                self.finish(node, position)
            return

        speed = min(self.MAX_SPEED, self.GAIN * distance)
        self.send_velocity(node, speed * dx / distance, speed * dy / distance)

        now = time.monotonic()
        if now - self.last_log >= self.LOG_PERIOD:
            self.last_log = now
            node.get_logger().info(
                f"Position: ({position.x:.2f}; {position.y:.2f}), "
                f"(dx; dy; distance): ({dx:.2f}; {dy:.2f}; {distance:.2f}), "
                f"speed: {speed:.2f} m/s"
            )

    def send_velocity(self, node: "FlightTestNode", vx: float, vy: float) -> None:
        message = TwistStamped()
        message.header.stamp = node.get_clock().now().to_msg()
        message.header.frame_id = "map"
        message.twist.linear.x = vx
        message.twist.linear.y = vy
        message.twist.linear.z = 0.0
        self.publisher.publish(message)

    def finish(self, node: "FlightTestNode", position) -> None:
        error = math.hypot(
            position.x - self.target[0], position.y - self.target[1]
        )
        node.get_logger().info(
            f"Actual position before landing: "
            f"({position.x:.2f}; {position.y:.2f})"
        )
        node.get_logger().info(
            f"Target position: ({self.target[0]:.2f}; {self.target[1]:.2f})"
        )
        node.get_logger().info(f"Positioning error: {error:.3f} m")
        node.get_logger().info("Flight to target completed, starting landing")
        node.state = FlightState.LANDING