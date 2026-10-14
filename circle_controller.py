
#!/usr/bin/env python3

import rospy
import math
from geometry_msgs.msg import Twist


def main():

    # 初始化ROS节点
    rospy.init_node('circle_controller')

    # 创建速度指令发布者
    pub = rospy.Publisher(
        '/turtle1/cmd_vel',
        Twist,
        queue_size=10
    )

    # 设置发布频率
    publish_rate = rospy.get_param('~publish_rate', 20.0)
    rate = rospy.Rate(publish_rate)

    rospy.loginfo("Circle controller started!")

    # 循环发布控制指令
    while not rospy.is_shutdown():

        # 从ROS参数服务器读取周期和幅值
        period = float(rospy.get_param('~period', 10.0))
        amplitude = float(rospy.get_param('~amplitude', 2.0))

        if period <= 0 or amplitude <= 0:
            rospy.logwarn("Invalid parameters!")
            pub.publish(Twist())
            rate.sleep()
            continue

        # 计算角速度和线速度
        angular_velocity = 2.0 * math.pi / period
        linear_velocity = angular_velocity * amplitude

        # 创建速度消息
        msg = Twist()
        msg.linear.x = linear_velocity
        msg.angular.z = angular_velocity

        # 发布速度指令
        pub.publish(msg)

        # 输出运行状态（每5秒最多输出一次）
        rospy.loginfo_throttle(
            5,
            "Publishing: linear=%.3f, angular=%.3f" %
            (linear_velocity, angular_velocity)
        )

        rate.sleep()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

