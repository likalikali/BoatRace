import serial
import time
import socket

#主机发送给树莓派，树莓派接收并发送数据给STM32，
# 设置串口参数
port = 'COM5'  # 串口号
baudrate = 115200  # 波特率

# 尝试连接串口
try:
    ser = serial.Serial(port, baudrate, timeout=0)

    print(f"已连接到波特率为 {baudrate} 的串口 {port}")

except Exception as e:
    print(f"连接端口错误: {e}")

# 主机的IP地址和端口
host = '127.0.0.1'  # 你的主机IP地址
port = 8889
# 创建一个TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 绑定IP地址和端口
server_socket.bind((host, port))
# 开始监听连接
server_socket.listen()
print(f"正在监听IP地址 {host}，端口 {port} 的连接...")




'''
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
    data_values = [random.randint(0, 99) for _ in range(6)] + [random.randint(0, 2)]
    data_packet = bytearray([0xDC, 0xBA])
    for value in data_values[:-1]:
        data_packet.extend(int_to_bytes(value, 2))
    data_packet.extend(int_to_bytes(data_values[-1], 2))
    data_packet.extend([0xFE, 0xEF])
    return data_packet
'''



while True:
    cs, client_address = server_socket.accept()
    print(f"接收到来自 {client_address} 的连接")
    if client_address:
        break
# 循环发送数据包
try:
    #网口变量
    BUF_SIZE = 0
    buf = bytearray(BUF_SIZE)  # 初始化缓冲区
    c1 = ib = flag = 0  # 初始化控制变量
    #串口变量
    BUF_SIZE2 = 0
    buf2 = bytearray(BUF_SIZE2)  # 初始化缓冲区
    c12 = ib2 = flag2 = 0  # 初始化控制变量

    while True:
        if ser.in_waiting > 0 :
            R2 = ser.read(1)  # 从串口读取一个字节

            if R2 == b'':
                print("读取失败")
                ser.close()
                break

            c2 = int.from_bytes(R2, byteorder='big')  # 将字节转换为整数

            if flag2 > 0:
                if ib2 < BUF_SIZE2:
                    buf2[ib2] = c2
                    ib2 += 1
                if ib2 == BUF_SIZE2:
                    # 判断包尾
                    if buf2[-2] == 0xEF and buf2[-1] == 0xFE:
                        buf2[0] = 0xAB
                        buf2[1] = 0xCD
                        print(f"已接收到STM32发送来的原始STA数据包: {buf2.hex()}")
                        #parsed_data = parse_data_sta(buf)

                        #print(parsed_data)

                        cs.sendall(bytes(buf2))
                        print(f"树莓派已通过TCP向主机发送STA数据包: {buf2.hex()}")
                    elif buf2[-2] == 0xCC and buf2[-1] == 0xDD:
                        buf2[0] = 0xAA
                        buf2[1] = 0xBB
                        print(f"已接收到STM32发送来的原始PID数据包:{buf2.hex()}")
                        #parsed_data = parse_data_pid(buf)
                        #print(f"解析后的数据: {parsed_data}")


                        cs.sendall(bytes(buf2))
                        print(f"树莓派已通过TCP向主机发送PID数据包: {buf2.hex()}")

                        '''
                        modified_data = cs.recv(1024)
                        for byte in modified_data:
                            ser.write(byte.to_bytes(1, 'big'))
                        print(f"向STM32发送的修改后的PID数据包: {modified_data.hex()}")
                        '''
                    elif buf2[-2] == 0xCD and buf2[-1] == 0xDC:
                        buf2[0] = 0xAB
                        buf2[1] = 0xBA
                        print(f"已接收到STM32发送来的原始GPS数据包:{buf2.hex()}")
                    elif buf2[-2] == 0xFE and buf2[-1] == 0xEF:
                        buf2[0] = 0xDC
                        buf2[1] = 0xBA
                        print(f"已接收到STM32发送来的原始MOV数据包:{buf2.hex()}")
                    else:
                        print("数据校验失败2")
                    flag2 = 0  # 重置标志位
            if flag2 == 0:
                if c12 == 0xAB and c2 == 0xCD:
                    flag2 = 1  # 设置标志位开始接收数据
                    ib2 = 2  # 设置缓冲区索引
                    BUF_SIZE2 = 32
                    buf2 = bytearray(BUF_SIZE2)  # 初始化缓冲区

                elif c12 == 0xAA and c2 == 0xBB:
                    flag2 = 1  # 设置标志位开始接收数据
                    ib2 = 2  # 设置缓冲区索引
                    BUF_SIZE2 = 40
                    buf2 = bytearray(BUF_SIZE2)  # 初始化缓冲区
                elif c12 == 0xAB and c2 == 0xBA:
                    flag2 = 1  # 设置标志位开始接收数据
                    ib2 = 2  # 设置缓冲区索引
                    BUF_SIZE2 = 28
                    buf2 = bytearray(BUF_SIZE2)  # 初始化缓冲区
                elif c12 == 0xDC and c2 == 0xBA:
                    flag2 = 1  # 设置标志位开始接收数据
                    ib2 = 2  # 设置缓冲区索引
                    BUF_SIZE2 = 18
                    buf2 = bytearray(BUF_SIZE2)  # 初始化缓冲区

            c12 = c2  # 更新前一个字节
        if cs:
            R = cs.recv(1)  # 你可以根据你的数据包大小进行调整
            if R == b'':
                print("读取失败")
                cs.close()
                break
            #protocol_choice = random.choice(['GPS', 'MOV', 'PID'])
            c = int.from_bytes(R, byteorder='big')  # 将字节转换为整数
            if flag > 0:
                if ib < BUF_SIZE:
                    buf[ib] = c
                    ib += 1
                if ib == BUF_SIZE:
                    # 判断包尾
                    if buf[-2] == 0xCD and buf[-1] == 0xDC:
                        buf[0] = 0xAB
                        buf[1] = 0xBA
                #if protocol_choice == 'GPS':
                        gps_packet = buf
                        # GPS协议
                        #timestamp_values = [time.time()] * 6
                        #gps_packet = generate_gps_packet(timestamp_values)
                        print(f"从主机接收到的原始GPS数据: {buf.hex()}")
                        for byte in gps_packet:
                            ser.write(byte.to_bytes(1, 'big'))
                        print(f"向STM32发送GPS数据包: {gps_packet.hex()}")
                    #elif protocol_choice == 'MOV':
                    elif buf[-2] == 0xFE and buf[-1] == 0xEF:
                        # MOV协议
                        buf[0] = 0xDC
                        buf[1] = 0xBA
                        mov_packet = buf
                        #mov_packet = generate_mov_packet()
                        print(f"从主机接收到的原始MOV数据:{buf.hex()}")
                        for byte in mov_packet:
                            ser.write(byte.to_bytes(1, 'big'))
                        print(f"向STM32发送MOV数据包: {mov_packet.hex()}")
                    elif buf[-2] == 0xCC and buf[-1] == 0xDD:
                        # PID协议
                        buf[0] = 0xAA
                        buf[1] = 0xBB
                        pid_packet = buf
                        #pid_packet = generate_new_pid_data()
                        print(f"从主机接收到的修改后的PID的原始数据:{buf.hex()}")

                        for byte in pid_packet:
                            ser.write(byte.to_bytes(1, 'big'))
                        print(f"向STM32发送修改后的PID数据包: {pid_packet.hex()}")
                    else:
                        print("数据校验失败1")
                    flag = 0  # 重置标志位
            if flag == 0:
                if c1 == 0xAB and c == 0xBA:
                    flag = 1  # 设置标志位开始接收数据
                    ib = 2  # 设置缓冲区索引
                    BUF_SIZE = 28
                    buf = bytearray(BUF_SIZE)  # 初始化缓冲区
                elif c1 == 0xDC and c == 0xBA:
                    flag = 1  # 设置标志位开始接收数据
                    ib = 2  # 设置缓冲区索引
                    BUF_SIZE = 18
                    buf = bytearray(BUF_SIZE)  # 初始化缓冲区
                elif c1 == 0xAA and c == 0xBB:
                    flag = 1  # 设置标志位开始接收数据
                    ib = 2  # 设置缓冲区索引
                    BUF_SIZE = 40
                    buf = bytearray(BUF_SIZE)  # 初始化缓冲区
            c1 = c  # 更新前一个字节

        time.sleep(0.001)  # 每0.5秒发送一次数据包

except KeyboardInterrupt:
    ser.close()
    print("串口连接已关闭.")