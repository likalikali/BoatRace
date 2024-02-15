import pygame
import tkinter as tk

# 初始化pygame和手柄
pygame.init()
pygame.joystick.init()

joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("未发现手柄！")#
    exit()
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# 映射函数
def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# 更新手柄信息的函数
def update_joystick_info():
    # 获取键状态
    pygame.event.pump()  # 处理所有事件队列中的事件
    x_button = joystick.get_button(2)  # X键（2）的状态，B键（1）的状态，A键（0）的状态，Y键（3）的状态
    x_button_status.set(f"X键状态: {'按下' if x_button else '未按下'}")
    b_button = joystick.get_button(1)
    b_button_status.set(f"B键状态: {'按下' if b_button else '未按下'}")
    a_button = joystick.get_button(0)
    a_button_status.set(f"A键状态: {'按下' if a_button else '未按下'}")
    y_button = joystick.get_button(3)
    y_button_status.set(f"Y键状态: {'按下' if y_button else '未按下'}")
    lb_button = joystick.get_button(4)
    lb_button_status.set(f"LB键状态: {'按下' if lb_button else '未按下'}")
    rb_button = joystick.get_button(5)
    rb_button_status.set(f"RB键状态: {'按下' if rb_button else '未按下'}")

    hatx_button, haty_button = joystick.get_hat(0)
    hat_status = "Hat键状态: "

    if hatx_button == -1:
        hat_status += "左"
    elif hatx_button == 1:
        hat_status += "右"

    if haty_button == -1:
        hat_status += "下"
    elif haty_button == 1:
        hat_status += "上"

    if hatx_button == 0 and haty_button == 0:
        hat_status += "未按下"

    hat_button_status.set(hat_status)

    # 获取摇杆位置并映射
    left_0_axis = map_range(joystick.get_axis(0), -1, 1, 0, 99.9)
    left_1_axis = map_range(joystick.get_axis(1), -1, 1, 0, 99.9)
    left_2_axis = map_range(joystick.get_axis(2), -1, 1, 0, 99.9)
    left_3_axis = map_range(joystick.get_axis(3), -1, 1, 0, 99.9)
    left_4_axis = map_range(joystick.get_axis(4), -1, 1, -1, 1)
    left_5_axis = map_range(joystick.get_axis(5), -1, 1, -1, 1)

    # 更新标签
    joystick_0.set(f"摇杆Axls 0: {left_0_axis:.0f}")
    joystick_1.set(f"摇杆Axls 1: {left_1_axis:.0f}")
    joystick_2.set(f"摇杆Axls 2: {left_2_axis:.0f}")
    joystick_3.set(f"摇杆Axls 3: {left_3_axis:.0f}")
    joystick_4.set(f"摇杆Axls 4: {left_4_axis:.0f}")
    joystick_5.set(f"摇杆Axls 5: {left_5_axis:.0f}")

    # 每1毫秒更新一次
    root.after(1, update_joystick_info)

# 创建GUI窗口
root = tk.Tk()
root.title("手柄输入显示")

x_button_status = tk.StringVar(value="X键状态: 未按下")
b_button_status = tk.StringVar(value="B键状态: 未按下")
a_button_status = tk.StringVar(value="A键状态: 未按下")
y_button_status = tk.StringVar(value="Y键状态: 未按下")
lb_button_status = tk.StringVar(value="LB键状态: 未按下")
rb_button_status = tk.StringVar(value="RB键状态: 未按下")
hat_button_status = tk.StringVar(value="Hat键状态: 未按下")
joystick_0 = tk.StringVar(value="摇杆Axls 0: 1000.00")
joystick_1 = tk.StringVar(value="摇杆Axls 1: 1000.00")
joystick_2 = tk.StringVar(value="摇杆Axls 2: 1000.00")
joystick_3 = tk.StringVar(value="摇杆Axls 3: 1000.00")
joystick_4 = tk.StringVar(value="摇杆Axls 4: -1.00")
joystick_5 = tk.StringVar(value="摇杆Axls 5: -1.00")
tk.Label(root, textvariable=x_button_status).pack()
tk.Label(root, textvariable=b_button_status).pack()
tk.Label(root, textvariable=a_button_status).pack()
tk.Label(root, textvariable=y_button_status).pack()
tk.Label(root, textvariable=joystick_0).pack()
tk.Label(root, textvariable=joystick_1).pack()
tk.Label(root, textvariable=joystick_2).pack()
tk.Label(root, textvariable=joystick_3).pack()
tk.Label(root, textvariable=lb_button_status).pack()
tk.Label(root, textvariable=rb_button_status).pack()
tk.Label(root, textvariable=hat_button_status).pack()
tk.Label(root, textvariable=joystick_4).pack()
tk.Label(root, textvariable=joystick_5).pack()

# 启动手柄信息更新
root.after(1, update_joystick_info)

root.mainloop()
