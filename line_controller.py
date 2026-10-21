#!/usr/bin/env python3
import math
import rospy

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class LineController:
    def __init__(self):
        rospy.init_node("line_controller")

        # 目标直线：默认 y = 8
        # axis = "y" 对应水平线
        # axis = "x" 对应竖直线
        self.axis = rospy.get_param("~axis", "y")
        self.target = rospy.get_param("~target", 8.0)

        # 固定线速度
        self.linear_speed = rospy.get_param("~linear_speed", 1.0)

        # 控制参数
        self.k_pos = rospy.get_param("~k_pos", 0.8)
        self.k_theta = rospy.get_param("~k_theta", 3.0)
        self.max_angular = rospy.get_param("~max_angular", 2.0)

        if self.axis not in ("x", "y"):
            raise ValueError("axis must be x or y")

        if self.linear_speed <= 0:
            raise ValueError("linear_speed must be positive")

        self.pose = None

        self.pub = rospy.Publisher(
            "/turtle1/cmd_vel", Twist, queue_size=10
        )

        self.sub = rospy.Subscriber(
            "/turtle1/pose", Pose, self.pose_callback
        )

        rospy.on_shutdown(self.stop)

    def pose_callback(self, msg):
        self.pose = msg

    @staticmethod
    def wrap_angle(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def control(self):
        rate = rospy.Rate(20)

        while not rospy.is_shutdown():
            if self.pose is None:
                rate.sleep()
                continue

            if self.axis == "y":
                # 跟踪水平线 y = target，沿 +x 方向
                error = self.target - self.pose.y
                desired_theta = math.atan(
                    self.k_pos * error
                )
            else:
                # 跟踪竖直线 x = target，沿 +y 方向
                error = self.target - self.pose.x
                desired_theta = (
                    math.pi / 2
                    - math.atan(self.k_pos * error)
                )

            theta_error = self.wrap_angle(
                desired_theta - self.pose.theta
            )

            omega = self.k_theta * theta_error

            # 限制角速度
            omega = max(
                -self.max_angular,
                min(self.max_angular, omega)
            )

            cmd = Twist()

            # 始终保持固定线速度
            cmd.linear.x = self.linear_speed

            # 只根据反馈调整角速度
            cmd.angular.z = omega

            self.pub.publish(cmd)

            rospy.loginfo_throttle(
                1.0,
                "error=%.3f, theta_error=%.3f, omega=%.3f",
                error, theta_error, omega
            )

            rate.sleep()

    def stop(self):
        # 节点退出时安全停车，不属于正常跟踪过程
        self.pub.publish(Twist())


if __name__ == "__main__":
    try:
        controller = LineController()
        controller.control()
    except rospy.ROSInterruptException:
        pass

