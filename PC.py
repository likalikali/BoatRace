#主机通过TCP网络通信，将GPS数据包（包头为0xAB和0xBA，包尾为0xCD和0xDC），MOV数据包（包头为0xDC和0xBA，包尾为0xFE和0xEF）发送给树莓派，
from socket import *
import time
import struct
import random


# GPS协议：将浮点数转换为字节的函数
def float_to_bytes(float_val):
    return struct.pack('<f', float_val)

# MOV协议：将整数转换为字节的函数
def int_to_bytes(int_val, num_bytes):
    return int_val.to_bytes(num_bytes, byteorder='little')

# PID协议：生成新的PID数据
def generate_new_pid_data():
    new_data = [int(time.time()) % 10000 for _ in range(18)]
    new_data_bytes = bytearray([0xAA, 0xBB])
    for val in new_data:
        new_data_bytes.extend(val.to_bytes(2, 'little'))
    new_data_bytes.extend([0xCC, 0xDD])
    return new_data_bytes

# 生成GPS协议数据包的函数
def generate_gps_packet(values):
    data_packet = bytearray([0xAB, 0xBA])
    for value in values:
        data_packet.extend(float_to_bytes(value))
    data_packet.extend([0xCD, 0xDC])
    return data_packet

# 生成MOV协议数据包的函数
def generate_mov_packet():
    data_values = [random.randint(0, 99) for _ in range(2)] + [random.randint(0, 2)] + [random.randint(0, 99) for _ in range(3)] + [random.randint(0, 2)]
    data_packet = bytearray([0xDC, 0xBA])
    for value in data_values[:-1]:
        data_packet.extend(int_to_bytes(value, 2))
    data_packet.extend(int_to_bytes(data_values[-1], 2))
    data_packet.extend([0xFE, 0xEF])
    return data_packet

#接收处理函数


def parse_data_sta(buf):
    # 将接收的字节按小端模式转换为整数
    gps_values = [int.from_bytes(buf[i:i+2], byteorder='little') for i in range(2, 12, 2)]
    gps = ''.join([str(val) for val in gps_values])  # 将整数合并为一个长字符串

    # 解析其他数据
    battery = int.from_bytes(buf[12:14], byteorder='little')
    speed = int.from_bytes(buf[14:16], byteorder='little')
    depth = int.from_bytes(buf[16:18], byteorder='little')
    temperature = int.from_bytes(buf[18:20], byteorder='little')
    humidity = int.from_bytes(buf[20:22], byteorder='little')
    water_temperature = int.from_bytes(buf[22:24], byteorder='little')
    roll = int.from_bytes(buf[24:26], byteorder='little')
    pitch = int.from_bytes(buf[26:28], byteorder='little')
    yaw = int.from_bytes(buf[28:30], byteorder='little')

    return {
        "GPS位置": gps,
        "电量": battery,
        "速度": speed,
        "深度": depth,
        "温度": temperature,
        "湿度": humidity,
        "水体温度": water_temperature,
        "ROLL": roll,
        "PITCH": pitch,
        "YAW": yaw
    }
#mod协议解析
def parse_data_mod(buf):

    # 解析数据
    touzhui_pitch = int.from_bytes(buf[2:4], byteorder='little')
    touzhui_roll = int.from_bytes(buf[4:6], byteorder='little')
    touzhui_yaw = int.from_bytes(buf[6:8], byteorder='little')
    shouzhui_pitch = int.from_bytes(buf[8:10], byteorder='little')
    shouzhui_roll = int.from_bytes(buf[10:12], byteorder='little')
    shouzhui_yaw = int.from_bytes(buf[12:14], byteorder='little')
    banjilidu_yaw = int.from_bytes(buf[14:16], byteorder='little')


    return {
        "头追pitch": touzhui_pitch,
        "头追roll": touzhui_roll,
        "头追yaw": touzhui_yaw,
        "手追pitch": shouzhui_pitch,
        "手追roll": shouzhui_roll,
        "手追yaw": shouzhui_yaw,
        "扳机力度yaw": banjilidu_yaw
    }



def bytes_to_int(bytes_val):
    return int.from_bytes(bytes_val, byteorder='little')

# 数据解析函数
def parse_data_pid(buf):
    # 检查数据长度和开始、结束标志
    if len(buf) == 40 and buf[-2:] == bytearray([0xCC, 0xDD]):
        pid_values = [bytes_to_int(buf[i:i+2]) for i in range(2, 38, 2)]
        pid_labels = [
            "PID-ROL-ANGLE-P", "PID-ROL-ANGLE-I", "PID-ROL-ANGLE-D",
            "PID-ROL-RATE-P", "PID-ROL-RATE-I", "PID-ROL-RATE-D",
            "PID-PITCH-ANGLE-P", "PID-PITCH-ANGLE-I", "PID-PITCH-ANGLE-D",
            "PID-PITCH-RATE-P", "PID-PITCH-RATE-I", "PID-PITCH-RATE-D",
            "PID-YAW-ANGLE-P", "PID-YAW-ANGLE-I", "PID-YAW-ANGLE-D",
            "PID-YAW-RATE-P", "PID-YAW-RATE-I", "PID-YAW-RATE-D"
        ]
        return dict(zip(pid_labels, pid_values))
    else:
        return "无效数据格式"
# 修改PID数据
def generate_new_pid_data():
    # 基于当前时间戳或其他逻辑生成新数据
    new_data = [int(time.time()) % 10000 for _ in range(18)]
    new_data_bytes = bytearray([0xAA, 0xBB])
    for val in new_data:
        new_data_bytes.extend(val.to_bytes(2, 'little'))
    new_data_bytes.extend([0xCC, 0xDD])
    return new_data_bytes







addr=('127.0.0.1', 8889)
cs=socket(AF_INET,SOCK_STREAM,0)
cs.connect(addr)

# 主循环
try:
    BUF_SIZE = 0
    buf = bytearray(BUF_SIZE)  # 初始化缓冲区
    c1 = ib = flag = 0  # 初始化控制变量
    while True:
        protocol_choice = random.choice(['GPS', 'MOV'])
        if protocol_choice == 'GPS':
            # GPS协议
            timestamp_values = [time.time()] * 6
            gps_packet = generate_gps_packet(timestamp_values)



            cs.sendall(bytes(gps_packet))
            print(f"主机通过TCP已向树莓派发送GPS数据包: {gps_packet.hex()}")
        elif protocol_choice == 'MOV':
            mov_packet = generate_mov_packet()



            cs.sendall(bytes(mov_packet))
            print(f"主机通过TCP已向树莓派发送MOV数据包: {mov_packet.hex()}")
        else:
            pass
        '''
        else:
            # PID协议（随机生成的之后要删）
            pid_packet = generate_new_pid_data()


            cs.sendall(bytes(pid_packet))
            print(f"主机通过TCP已向树莓派发送PID数据包: {pid_packet.hex()}")
        '''
        if cs:
            cs.setblocking(False)
            try:
                R = cs.recv(1)  # 你可以根据你的数据包大小进行调整
                if R == b'':
                    print("读取失败")
                    cs.close()
                    break
                c = int.from_bytes(R, byteorder='big')  # 将字节转换为整数
                if flag > 0:
                    if ib < BUF_SIZE:
                        buf[ib] = c
                        ib += 1
                    if ib == BUF_SIZE:
                        # 判断包尾
                        if buf[-2] == 0xEF and buf[-1] == 0xFE:
                            buf[0] = 0xAB
                            buf[1] = 0xCD
                            print(f"接收到树莓派发来的STA原始数据包: {buf.hex()}")
                            parsed_data = parse_data_sta(buf)
                            print(f"主机解析后的STA数据: {parsed_data}")

                        elif buf[-2] == 0xCC and buf[-1] == 0xDD:
                            buf[0] = 0xAA
                            buf[1] = 0xBB
                            print(f"接收到树莓派发来的PID原始数据:{buf.hex()}")
                            parsed_data = parse_data_pid(buf)
                            print(f"主机解析后的PID数据: {parsed_data}")

                            modified_data = generate_new_pid_data()


                            cs.sendall(bytes(modified_data))
                            print(f"主机通过TCP已向树莓派发送PID修改后的PID数据包: {modified_data.hex()}")
                        elif buf[-2] == 0xEE and buf[-1] == 0xFF:
                            buf[0] = 0xAC
                            buf[1] = 0xBD
                            print(f"接收到体感模块发来的MOD原始数据:{buf.hex()}")
                            parsed_data = parse_data_mod(buf)
                            print(f"主机解析后的MOD数据: {parsed_data}")
                        else:
                            print("数据校验失败")
                        flag = 0  # 重置标志位
                if flag == 0:
                    if c1 == 0xAB and c == 0xCD:
                        flag = 1  # 设置标志位开始接收数据
                        ib = 2  # 设置缓冲区索引
                        BUF_SIZE = 32
                        buf = bytearray(BUF_SIZE)  # 初始化缓冲区
                    elif c1 == 0xAA and c == 0xBB:
                        flag = 1  # 设置标志位开始接收数据
                        ib = 2  # 设置缓冲区索引
                        BUF_SIZE = 40
                        buf = bytearray(BUF_SIZE)  # 初始化缓冲区
                    elif c1 == 0xAC and c == 0xBD:
                        flag = 1  # 设置标志位开始接收数据
                        ib = 2  # 设置缓冲区索引
                        BUF_SIZE = 18
                        buf = bytearray(BUF_SIZE)  # 初始化缓冲区
                c1 = c  # 更新前一个字节
            except BlockingIOError:
                # 没有数据可读时的处理
                pass


        time.sleep(0.001)  # 短暂休眠，减少CPU负荷
except KeyboardInterrupt:
    cs.close()
    print("TCP服务器已关闭.")
