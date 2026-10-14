
#!/usr/bin/env python3

import os
import sys
import rosbag
import matplotlib

# 使用非交互式绘图后端，确保可以保存图片
matplotlib.use('Agg')

import matplotlib.pyplot as plt


def main():

    # 1. 指定bag文件位置
    bag_path = os.path.expanduser(
        '~/catkin_ws/bagfiles/turtle_circle.bag'
    )

    # 2. 检查文件是否存在
    if not os.path.exists(bag_path):
        print("Error: bag file not found!")
        print(bag_path)
        sys.exit(1)

    # 3. 创建数据存储列表
    cmd_time = []
    linear_cmd = []
    angular_cmd = []

    pose_time = []
    x_position = []
    y_position = []
    theta = []
    linear_actual = []
    angular_actual = []

    print("Reading rosbag data...")

    # 4. 打开并读取bag文件
    with rosbag.Bag(bag_path, 'r') as bag:

        for topic, msg, t in bag.read_messages(
            topics=[
                '/turtle1/cmd_vel',
                '/turtle1/pose'
            ]
        ):

            time = t.to_sec()

            # 提取速度指令
            if topic == '/turtle1/cmd_vel':

                cmd_time.append(time)
                linear_cmd.append(msg.linear.x)
                angular_cmd.append(msg.angular.z)

            # 提取位置与实际速度
            elif topic == '/turtle1/pose':

                pose_time.append(time)

                x_position.append(msg.x)
                y_position.append(msg.y)
                theta.append(msg.theta)

                linear_actual.append(
                    msg.linear_velocity
                )

                angular_actual.append(
                    msg.angular_velocity
                )

    # 5. 检查数据完整性
    if len(cmd_time) == 0 or len(pose_time) == 0:
        print("Error: Missing topic data!")
        sys.exit(1)

    # 6. 将时间转换为相对时间
    start_time = min(cmd_time[0], pose_time[0])

    cmd_time = [
        t - start_time for t in cmd_time
    ]

    pose_time = [
        t - start_time for t in pose_time
    ]

    print("Data loaded successfully!")

    print("Velocity messages:", len(cmd_time))
    print("Pose messages:", len(pose_time))

    # 7. 创建2行2列的绘图窗口
    fig, axes = plt.subplots(
        2, 2, figsize=(12, 8)
    )

    # 图1：线速度与时间
    axes[0, 0].plot(
        cmd_time,
        linear_cmd,
        label='Command Linear Velocity'
    )

    axes[0, 0].plot(
        pose_time,
        linear_actual,
        '--',
        label='Actual Linear Velocity'
    )

    axes[0, 0].set_title(
        'Linear Velocity vs Time'
    )

    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('Linear Velocity')
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # 图2：角速度与时间
    axes[0, 1].plot(
        cmd_time,
        angular_cmd,
        label='Command Angular Velocity'
    )

    axes[0, 1].plot(
        pose_time,
        angular_actual,
        '--',
        label='Actual Angular Velocity'
    )

    axes[0, 1].set_title(
        'Angular Velocity vs Time'
    )

    axes[0, 1].set_xlabel('Time (s)')
    axes[0, 1].set_ylabel('Angular Velocity (rad/s)')
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # 图3：X、Y位置随时间变化
    axes[1, 0].plot(
        pose_time,
        x_position,
        label='X Position'
    )

    axes[1, 0].plot(
        pose_time,
        y_position,
        label='Y Position'
    )

    axes[1, 0].set_title(
        'Position vs Time'
    )

    axes[1, 0].set_xlabel('Time (s)')
    axes[1, 0].set_ylabel('Position')
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    # 图4：二维圆周运动轨迹
    axes[1, 1].plot(
        x_position,
        y_position,
        label='Turtle Trajectory'
    )

    axes[1, 1].scatter(
        x_position[0],
        y_position[0],
        color='red',
        label='Start Position'
    )

    axes[1, 1].set_title(
        'XY Trajectory'
    )

    axes[1, 1].set_xlabel('X Position')
    axes[1, 1].set_ylabel('Y Position')
    axes[1, 1].axis('equal')
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    # 8. 调整图像布局
    plt.tight_layout()

    # 9. 设置图片保存路径
    output_path = os.path.expanduser(
        '~/catkin_ws/bagfiles/turtle_analysis.png'
    )

    # 10. 保存图像
    plt.savefig(
        output_path,
        dpi=300
    )

    plt.close(fig)

    print("Analysis completed!")
    print("Figure saved to:")
    print(output_path)


if __name__ == '__main__':
    main()

