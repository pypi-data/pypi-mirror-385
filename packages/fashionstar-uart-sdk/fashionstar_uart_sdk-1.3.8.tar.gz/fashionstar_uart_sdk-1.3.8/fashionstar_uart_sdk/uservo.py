'''
Fashion Star 总线伺服舵机Python SDK
--------------------------------------------------
 * 作者: 深圳市华馨京科技有限公司
 * 网站：https://fashionrobo.com/
 * 版本：V1.3.6
--------------------------------------------------
'''
import time
import logging
import serial
import struct
import math
# 设置日志等级
class Packet:
	'''数据包'''
	# 使用pkt_type来区分请求数据还是响应数据
	PKT_TYPE_REQUEST = 0 # 请求包
	PKT_TYPE_RESPONSE = 1 # 响应包
	HEADER_LEN = 2 # 帧头校验数据的字节长度
	HEADERS = [b'\x12\x4c', b'\x05\x1c']
	CODE_LEN = 1 # 功能编号长度
	SIZE_LEN = 1 # 字节长度
	CHECKSUM_LEN = 1 # 校验和长度

	@classmethod
	def calc_checksum(cls, code, param_bytes=b'', pkt_type=1):
		'''计算校验和'''
		header = cls.HEADERS[pkt_type]
		return sum(header + struct.pack('<BB', code, len(param_bytes)) + param_bytes) %256

	@classmethod
	def verify(cls, packet_bytes, pkt_type=1):
		'''检验数据是否合法'''
		# 获取帧头
		header = cls.HEADERS[pkt_type]	  
		# 帧头检验
		if packet_bytes[:cls.HEADER_LEN] != cls.HEADERS[pkt_type]:
			return False
		code, size = struct.unpack('<BB', packet_bytes[cls.HEADER_LEN : cls.HEADER_LEN + cls.CODE_LEN + cls.SIZE_LEN])		
		# 长度校验
		param_bytes = packet_bytes[cls.HEADER_LEN + cls.CODE_LEN + cls.SIZE_LEN : -cls.CHECKSUM_LEN]
		if len(param_bytes) != size:
			return False
		# 校验和检验
		checksum = packet_bytes[-cls.CHECKSUM_LEN]
		# logging.info('实际的Checksum : {} 计算得到的Checksum: {}'.format(checksum, cls.calc_checksum(code , param_bytes, pkt_type=pkt_type)))		
		# 校验和检查
		if checksum != cls.calc_checksum(code , param_bytes, pkt_type=pkt_type):
			return False		
		# 数据检验合格
		return True

	@classmethod
	def pack(cls, code, param_bytes=b''):
		'''数据打包为二进制数据'''
		size = len(param_bytes)
		checksum = cls.calc_checksum(code, param_bytes, pkt_type=cls.PKT_TYPE_REQUEST)
		frame_bytes = cls.HEADERS[cls.PKT_TYPE_REQUEST] + struct.pack('<BB', code, size) + param_bytes + struct.pack('<B', checksum)
		return frame_bytes
	
	@classmethod
	def unpack(cls, packet_bytes):
		'''二进制数据解包为所需参数'''
		if not cls.verify(packet_bytes, pkt_type=cls.PKT_TYPE_RESPONSE):
			# 数据非法
			return None
		code = struct.unpack('<B', packet_bytes[cls.HEADER_LEN:cls.HEADER_LEN+cls.CODE_LEN])[0]
		param_bytes = packet_bytes[cls.HEADER_LEN + cls.CODE_LEN + cls.SIZE_LEN : -cls.CHECKSUM_LEN]
		return code, param_bytes

class PacketBuffer:
	'''Packet中转站'''
	def __init__(self, is_debug=False):
		self.is_debug = is_debug
		self.packet_bytes_list = []
		# 清空缓存区域
		self.empty_buffer()
	
	def update(self, next_byte):
		'''将新的字节添加到Packet中转站'''
		if self.is_debug:
			logging.info('[INFO]: next byte: 0x%02x'%next_byte[0])
		if not self.header_flag:
			# 填充头部字节
			if len(self.header) < Packet.HEADER_LEN:
				# 向Header追加字节
				self.header += next_byte
				if len(self.header) == Packet.HEADER_LEN and self.header == Packet.HEADERS[Packet.PKT_TYPE_RESPONSE]:
					self.header_flag = True
			elif len(self.header) == Packet.HEADER_LEN:
				# 首字节出队列
				self.header = self.header[1:] + next_byte
				# 查看Header是否匹配
				if self.header == Packet.HEADERS[Packet.PKT_TYPE_RESPONSE]:
					self.header_flag = True
		elif self.header_flag and not self.code_flag:
			# 填充Code
			if len(self.code) < Packet.CODE_LEN:
				self.code += next_byte
				if len(self.code) == Packet.CODE_LEN:
					self.code_flag = True

		elif self.code_flag and not self.size_flag:
			# 填充参数尺寸
			if len(self.size) < Packet.SIZE_LEN:
				self.size += next_byte
				if len(self.size) == Packet.SIZE_LEN:
					self.size_flag = True
					# 更新参数个数
					self.param_len = struct.unpack('<B', self.size)[0]

		elif self.size_flag and not self.param_bytes_flag:
			# 填充参数
			if len(self.param_bytes) < self.param_len:
				self.param_bytes += next_byte
				if len(self.param_bytes) == self.param_len:
					self.param_bytes_flag = True

		elif self.param_bytes_flag:
			# 填充校验和
			self.checksum = next_byte
			# 构建一个完整的Packet
			tmp_packet_bytes = self.header + self.code + self.size + self.param_bytes + self.checksum
			# 验证数据帧
			if Packet.verify(tmp_packet_bytes, pkt_type=Packet.PKT_TYPE_RESPONSE):
				# 将新的Packet数据添加到中转列表里
				self.packet_bytes_list.append(tmp_packet_bytes)
            # 重新清空缓冲区
			self.empty_buffer()
		
	def empty_buffer(self):
		# 数据帧是否准备好
		self.param_len = None
		self.header = b''
		self.header_flag = False
		self.code = b''
		self.code_flag = False
		self.size = b''
		self.size_flag = False
		self.param_bytes = b''
		self.param_bytes_flag = False
	
	def has_valid_packet(self):
		'''是否有有效的包'''
		return len(self.packet_bytes_list) > 0
	
	def get_packet(self):
		'''获取队首的Bytes'''
		return self.packet_bytes_list.pop(0)


class UartServoInfo:
	'''串口舵机的信息'''
	SERVO_DEADBLOCK = 1.0 # 舵机死区
	SERVO_ANGLE_LOWERB = -135 # 舵机角度下限
	SERVO_ANGLE_UPPERB = 135 # 舵机角度上限 
	
	def __init__(self, id, lowerb=None, upperb=None):
		self.id = id # 舵机的ID
		self.cur_angle = None # 当前的角度
		self.target_angle = None # 目标角度
		self.is_online = False # 舵机是否在线 
		# 舵机角度上下限
		self.lowerb = lowerb if lowerb is not None else None # self.SERVO_ANGLE_LOWERB
		self.upperb = upperb if upperb is not None else None # self.SERVO_ANGLE_UPPERB
		self.last_angle_error = None    # 上一次的角度误差
		self.last_sample_time = None    # 上一次的采样时间
		# 内存表数据
		self.data_table_raw_dict = {} # 原始数据 字典类型
		# 内存表写入标志位
		self.data_write_success = False
		# 是否开启多圈模式
		self.is_mturn = False
		self.voltage = None
		self.current = None
		self.power = None
		self.temp = None
		self.status = None
		self.angle_monitor = None
		self.turn = None

	
	@property
	def angle(self):
		'''获取当前舵机的角度'''
		return self.cur_angle
	
	def move(self, angle):
		'''设置舵机的目标角度'''
		# 角度边界约束
		if self.lowerb is not None:
			angle = self.lowerb if angle < self.lowerb else angle
		if self.upperb is not None:
			angle = self.upperb if angle > self.upperb else angle
		# 设置目标角度
		self.target_angle = angle

	def update(self, angle):
		'''更新当前舵机的角度'''
		self.cur_angle = angle

	def __str__(self):
		return "目标角度:{:.1f} 实际角度:{:.1f} 角度误差:{:.2f}".format(self.target_angle, self.angle, self.target_angle-self.angle)

class UartServoManager:
	'''串口舵机管理器'''
	UPDATE_INTERVAL_MS = 10 # ms
	# 指令定义
	CODE_PING = 1 # 舵机检测
	CODE_RESET_USER_DATA = 2 # 用户表数据重置
	CODE_READ_DATA = 3 # 读取内存表
	CODE_WRITE_DATA = 4 # 写入内存表
	CODE_QUERY_SERVO_INFO = 5 # 查询舵机所有的信息 (未使用)
	CODE_SET_SPIN = 7 # 设置轮式模式
	CODE_SET_SERVO_ANGLE = 8 # 设置舵机角度
	CODE_SET_DAMPING = 9 # 设置阻尼模式
	CODE_QUERY_SERVO_ANGLE = 10 # 查询舵机的角度
	CODE_SET_SERVO_ANGLE_BY_INTERVAL = 11 # 角度设置(指定周期)
	CODE_SET_SERVO_ANGLE_BY_VELOCITY = 12 # 角度设置(指定转速)
	CODE_SET_SERVO_ANGLE_MTURN = 13 # 多圈角度设置
	CODE_SET_SERVO_ANGLE_MTURN_BY_INTERVAL = 14 # 多圈角度设置(指定周期)
	CODE_SET_SERVO_ANGLE_MTURN_BY_VELOCITY = 15 # 多圈角度设置(指定转速)
	CODE_QUERY_SERVO_ANGLE_MTURN = 16 # 查询舵机角度(多圈)
	CODE_RESET_MULTI_TURN_ANGLE = 17 # 多圈角度重置
	CODE_BEGIN_ASYNC = 18 # 开始异步命令
	CODE_END_ASYNC = 19 # 结束异步命令
	CODE_QUERY_SERVO_MONITOR = 22   #舵机数据监控 
	CODE_SET_ORIGIN_POINT = 23 # 设置原点
	CODE_SET_STOP_ON_CONTROL = 24 #控制模式停止指令
	CODE_SYNC_COMMAND =25	# 同步命令 
	# 响应数据包黑名单
	RESPONSE_CODE_NEGLECT = []
	# 定义轮式模式的四种控制方法
	WHEEL_MODE_STOP = 0x00 # 停止
	WHEEL_MODE_NORMAL = 0x01 # 常规模式
	WHEEL_MODE_TURN = 0x02 # 定圈
	WHEEL_MODE_TIME = 0x03 # 定时
	# 内存表
	ADDRESS_VOLTAGE = 1
	ADDRESS_CURRENT = 2
	ADDRESS_POWER = 3
	ADDRESS_TEMPERATURE = 4
	ADDRESS_STATUS = 5
	def __init__(self, uart, srv_num=254, mean_dps=100, is_debug=False):
		self.is_debug = is_debug
		self.uart = uart
		self.pkt_buffer = PacketBuffer()
		self.mean_dps = mean_dps # 默认的舵机旋转角速度
		self.loss_uservo = 0 
		self.loss_uservo_record_time = 0
		# 存放舵机信息
		self.servos = {}
		# 返回的CODE与函数的映射
		self.response_handle_funcs = {
			self.CODE_QUERY_SERVO_ANGLE: self.response_query_servo_angle,
			self.CODE_QUERY_SERVO_ANGLE_MTURN: self.response_query_servo_angle_mturn,
			self.CODE_QUERY_SERVO_MONITOR: self.response_query_servo_monitor,
			self.CODE_PING: self.response_ping,
			self.CODE_RESET_USER_DATA: self.response_reset_user_data,
			self.CODE_READ_DATA: self.response_read_data,
			self.CODE_WRITE_DATA: self.response_write_data,
		}
		for servo_id in range(254):
			self.servos[servo_id] = UartServoInfo(servo_id)
			# self.servos[servo_id].is_online = False # 设置舵机在线的标志位

	def send_request(self, code, param_bytes):
		'''发送请数据'''
		packet_bytes = Packet.pack(code, param_bytes)
		try:
			# while self.uart.in_waiting > 0:
			# 	time.sleep(0.001)  # 等待接收缓冲区清空
			self.uart.write(packet_bytes)
		except serial.SerialException as e:
			logging.error('串口数据发送异常, 请检查是否是USB口松动或设备号变更, 需重新初始化舵机')

	def ping(self, servo_id:int):
		'''发送Ping请求'''
		self.send_request(self.CODE_PING, struct.pack('<B', servo_id))
		if self.is_debug:
			logging.info('PING 舵机 id={}'.format(servo_id))
		self.servos[servo_id].is_online = False # 设置舵机在线的标志位
		self.update(wait_response=True)
		return self.servos[servo_id].is_online

	def scan_servo(self, srv_num=254):
		'''扫描所有的舵机'''
		#ping所有的舵机
		for servo_id in range(srv_num):
			#发送ping请求
			self.ping(servo_id)
		if self.is_debug:
			logging.info("有效的舵机ID列表: {}".format(list(self.servos.keys())))
	
	def response_ping(self, param_bytes):
		'''响应PING请求'''
		servo_id, = struct.unpack('<B', param_bytes)
		if servo_id not in self.servos:
			self.servos[servo_id] = UartServoInfo(servo_id)
			self.servos[servo_id].is_online = True # 设置舵机在线的标志位
			if self.is_debug:
				logging.info('[fs_uservo]ECHO 添加一个新的舵机 id={}'.format(servo_id))
		else:
			self.servos[servo_id].is_online = True # 设置舵机在线的标志位
			if self.is_debug:
				logging.info('[fs_uservo]ECHO 已知舵机 id={}'.format(servo_id))
		

	def query_servo_angle(self, servo_id):
		'''更新单个舵机的角度'''
		if self.is_debug:
			logging.info('查询单个舵机的角度 id={}'.format(servo_id))

		self.send_request(self.CODE_QUERY_SERVO_ANGLE, struct.pack('<B', servo_id))
		self.update(wait_response=True) # 等待数据回传
		return self.servos[servo_id].angle

	def query_servo_mturn_angle(self, servo_id):
		'''更新单个舵机的ex角度'''
		if self.is_debug:
			logging.info('查询单个舵机的角度 id={}'.format(servo_id))
			# 多圈模式
		self.send_request(self.CODE_QUERY_SERVO_ANGLE_MTURN, struct.pack('<B', servo_id))
		self.update(wait_response=True) # 等待数据回传
		return self.servos[servo_id].angle


	def query_all_srv_angle(self):
		'''更新所有的舵机角度'''
		for servo_id in self.servos:
			self.query_servo_angle(servo_id)

	def response_query_servo_angle(self, param_bytes):
		'''响应查询单个舵机角度'''
		# 数据解包
		servo_id, angle = struct.unpack('<Bh', param_bytes)
		# 舵机的分辨率是0.1度
		angle /= 10
		# print("查询到角度单圈: {}".format(angle))
		if servo_id not in self.servos:
			pass
		else:
			# 更新当前的角度
			self.servos[servo_id].update(angle)
			if self.is_debug:
				logging.info('[INFO] 更新舵机角度 id={}  角度: {:.2f} deg'.format(servo_id, angle))
	def response_query_servo_angle_mturn(self, param_bytes):
		'''响应舵机角度查询角度(多圈)'''
		# 数据解包
		servo_id, angle, mturn = struct.unpack('<Bih', param_bytes)
  		# 舵机的分辨率是0.1度
		angle /= 10.0
		if servo_id not in self.servos:
			pass
		else:
			# 更新当前的角度
			self.servos[servo_id].update(angle)
			if self.is_debug:
				logging.info('[INFO] 更新舵机角度 id={}  角度: {:.2f} deg'.format(servo_id, angle))
	
	def refresh_srv_list(self, max_servo_id=254):
		'''刷新当前的舵机列表'''
		# 清空已有的字典
		self.servos = {}
		for servo_idx in range(max_servo_id):
			self.ping(servo_idx)
			for ti in range(20):
				# 查询一个舵机最多等待1000ms
				self.update()
				if servo_idx in self.servos:
					break	
				time.sleep(0.05)

	def query_srv_info(self, servo_id):
		'''查询单个舵机的所有配置'''
		self.send_request(self.CODE_QUERY_SERVO_INFO, struct.pack('<B', servo_id))
		# logging.info('查询单个舵机的所有配置 id={}'.format(servo_id))
		self.update(wait_response=True)

	def set_servo_angle(self, servo_id:int, angle:float, is_mturn:bool=False, interval:float=None, velocity:float=None, t_acc:int=20, t_dec:int=20,  power:int=0, mean_dps:float=100.0):
		'''发送舵机角度控制请求
		@param servo_id 
			舵机的ID号
		@param angle 
			舵机的目标角度
		@param is_mturn
			是否开启多圈模式
		@param interval 
			中间间隔 单位ms
		@param velocity 
			目标转速，单位dps
		@param t_acc
			加速时间，在指定目标转速时有效. 单位ms
		@param t_dec
			减速时间, 在指定减速时间时有效. 单位ms
		@param power
			功率限制, 单位mW
		@param mean_dps
			平均转速, 单位dps
		'''
		if servo_id not in self.servos:
			logging.warning('未知舵机序号: {}'.format(servo_id))
			return False
		# 同步修改srv_info
		self.servos[servo_id].move(angle)
		# 发送控制指令
		# 单位转换为0.1度
		angle = int(angle * 10)
		# 角度约束
		if is_mturn:
			if angle < -3686400:
				angle = -3686400
			elif angle > 3686400:
				angle = 3686400
		else:
			if angle < -1800:
				angle = -1800
			elif angle > 1800:
				angle = 1800
		# 加减速时间约束
		if t_acc < 20:
			t_acc = 20
		if t_dec < 20:
			t_dec = 20
		# 获取舵机信息
		srv_info = self.servos[servo_id]
		self.servos[servo_id].is_mturn = is_mturn
		if interval is not None and interval != 0:
			# 指定周期
			# 判断周期设定是否合法
			interval = int(interval)             
			if is_mturn:
				if interval < t_acc + t_dec:
					interval = t_acc + t_dec
				elif interval > 4096000:
					interval = 4096000
				param_bytes = struct.pack('<BiIHHH', servo_id, angle, interval, t_acc, t_dec, power)
				self.send_request(self.CODE_SET_SERVO_ANGLE_MTURN_BY_INTERVAL, param_bytes)
			else:
				param_bytes = struct.pack('<BhHHHH', servo_id, angle, interval, t_acc, t_dec, power)
				self.send_request(self.CODE_SET_SERVO_ANGLE_BY_INTERVAL, param_bytes)
		elif velocity is not None:
			# 指定目标转速
			# 转速约束
			if velocity < 1.0:
				velocity = 1.0
			elif velocity > 750.0:
				velocity = 750.0
			velocity = int(velocity*10.0) # 单位dps -> 0.1dps	
			if is_mturn:
				param_bytes = struct.pack('<BiHHHH', servo_id, angle, velocity, t_acc, t_dec, power)
				self.send_request(self.CODE_SET_SERVO_ANGLE_MTURN_BY_VELOCITY, param_bytes)
			else:
				param_bytes = struct.pack('<BhHHHH', servo_id, angle, velocity, t_acc, t_dec, power)
				self.send_request(self.CODE_SET_SERVO_ANGLE_BY_VELOCITY, param_bytes)
		else:
			# 根据平均转速，计算周期
			if interval is None:
				# if srv_info.angle is None:
				# 查询角度
				srv_info.update(self.query_servo_angle(servo_id))
				interval = int((abs(angle*0.1 - srv_info.angle) / mean_dps) * 1000)
			if is_mturn:
				param_bytes = struct.pack('<BiIH', servo_id, angle, interval, power)
				self.send_request(self.CODE_SET_SERVO_ANGLE_MTURN, param_bytes)
			else:
				param_bytes = struct.pack('<BhHH', servo_id, angle, interval, power)
				self.send_request(self.CODE_SET_SERVO_ANGLE, param_bytes)		
		return True
		
	def set_wheel(self, servo_id, mode, value=0, is_cw=True, mean_dps=None):
		'''设置舵机轮式模式控制
		@param servo_id
			舵机的ID号
		@param mode
			舵机的模式 取值范围[0,3]
		@param value 
			定时模式下代表时间(单位ms)
			定圈模式下代表圈数(单位圈)
		＠param is_cw
			轮子的旋转方向, is_cw代表是否是顺指针旋转
		@param speed
			轮子旋转的角速度, 单位 °/s
		'''
		# 轮式模式的控制方法
		method = mode | 0x80 if is_cw else mode
		# 设置旋转的角速度
		mean_dps = self.mean_dps if mean_dps is None else mean_dps
		mean_dps = int(mean_dps)
		# 发送请求
		self.send_request(self.CODE_SET_SPIN, struct.pack('<BBHH', servo_id, method, mean_dps, value))
	
	def wheel_stop(self, servo_id):
		'''停止'''
		self.set_wheel(servo_id, self.WHEEL_MODE_STOP, 0, False, 0)
	
	def set_wheel_norm(self, servo_id, is_cw=True, mean_dps=None):
		'''设置轮式为普通模式, 转速单位: °/s'''
		self.set_wheel(servo_id, self.WHEEL_MODE_NORMAL, value=0, is_cw=is_cw, mean_dps=mean_dps)
		
	def set_wheel_turn(self, servo_id, turn=1, is_cw=True, mean_dps=None, is_wait=True):
		'''设置轮式为定圈模式, 圈数单位: 圈数'''
		if mean_dps is None:
			mean_dps = self.mean_dps
		self.set_wheel(servo_id, self.WHEEL_MODE_TURN, value=turn, is_cw=is_cw, mean_dps=mean_dps)
		# 根据圈数与转速, 估计延时的时间
		if is_wait:
			time.sleep(turn*360.0 / mean_dps)

	def set_wheel_time(self, servo_id, interval=1000, is_cw=True, mean_dps=None, is_wait=True):
		'''设置轮子为定时模式，时间单位: ms'''
		self.set_wheel(servo_id, self.WHEEL_MODE_TIME, value=interval, is_cw=is_cw, mean_dps=mean_dps)
		if is_wait:
			time.sleep(interval/1000.0)

	def set_damping(self, servo_id, power=0):
		'''设置阻尼模式
		@param servo_id
			舵机ID
		@param power
			舵机保持功率
		'''
		self.send_request(self.CODE_SET_DAMPING, struct.pack('<BH', servo_id, power))
	
	def reset_user_data(self, servo_id):
		'''用户表数据重置'''
		# 发送请求数据
		self.send_request(self.CODE_RESET_USER_DATA, struct.pack('<B', servo_id))
		return True

	def response_reset_user_data(self, param_bytes):
		'''用户数据重置响应'''
		servo_id, result = struct.unpack('<BB', param_bytes)
		if self.is_debug:
			# logging.info("舵机用户数据重置 舵机ID={} 是否成功={}".format(servo_id, result))
			print("舵机用户数据重置 舵机ID={} 是否成功={}".format(servo_id, result))

	def read_data(self, servo_id, address):
		'''读取内存表数据
		注: 返回的是字节流数据, 需要进一步处理
		'''
		# 发送请求
		self.send_request(self.CODE_READ_DATA, struct.pack('<BB', servo_id, address))
		self.update(wait_response=True) # 等待数据回传
		if self.is_debug:
			logging.info("READ DATA 舵机ID={} Address={}".format(servo_id, address))
			logging.info("DATA : {}".format(self.servos[servo_id].data_table_raw_dict[address]))
		# 返回读取到的数据
		return self.servos[servo_id].data_table_raw_dict[address]

	def response_read_data(self, param_bytes):
		'''处理内存表数据读取回传'''
		# 数据提取
		servo_id, address = struct.unpack('<BB', param_bytes[:2])
		content = param_bytes[2:]
		self.servos[servo_id].data_table_raw_dict[address] = content

	def write_data(self, servo_id, address, content):
		'''写入数据'''
		# 发送请求
		self.send_request(self.CODE_WRITE_DATA, struct.pack('<BB', servo_id, address)+content)
		# 初始化标志位
		self.servos[servo_id].data_write_success = False
		if self.is_debug:
			logging.info("WRITE DATA 舵机ID={} Address={} Value={}".format(servo_id, address, content))
		# 等待数据回传
		self.update(wait_response=True) 
		return self.servos[servo_id].data_write_success

	def response_write_data(self, param_bytes):
		'''处理写入数据回传'''
		servo_id, address, result = struct.unpack('<BBB', param_bytes)
		self.servos[servo_id].data_write_success = result == 1
		if self.is_debug:
			logging.info("WRITE DATA 舵机ID={} Address={} Result={}".format(servo_id, address, result))

	def query_voltage(self, servo_id):
		'''查询总线电压,单位V'''
		voltage_bytes = self.read_data(servo_id, self.ADDRESS_VOLTAGE)
		return struct.unpack('<H', voltage_bytes)[0] / 1000.0

	def query_current(self, servo_id):
		'''查询电流, 单位A'''
		current_bytes = self.read_data(servo_id, self.ADDRESS_CURRENT)
		return struct.unpack('<H', current_bytes)[0] / 1000.0

	def query_power(self, servo_id):
		'''查询功率, 单位W'''
		power_bytes = self.read_data(servo_id, self.ADDRESS_POWER)
		return struct.unpack('<H', power_bytes)[0] / 1000.0
	
	def query_temperature(self, servo_id):
		'''查询温度,为实际温度℃'''
		temp_bytes = self.read_data(servo_id, self.ADDRESS_TEMPERATURE)
		return float(1/((math.log(10000*(struct.unpack('<H', temp_bytes)[0])/(10000*(4096-(struct.unpack('<H', temp_bytes)[0]))))/3435)+1/(273.15+25))-273.15)

	#  舵机工作状态标志位
	#  BIT[0] - 执行指令置1，执行完成后清零。
	#  BIT[1] - 执行指令错误置1，在下次正确执行后清零。
	#  BIT[2] - 堵转错误置1，解除堵转后清零。
	#  BIT[3] - 电压过高置1，电压恢复正常后清零。
	#  BIT[4] - 电压过低置1，电压恢复正常后清零。
	#  BIT[5] - 电流错误置1，电流恢复正常后清零。
	#  BIT[6] - 功率错误置1，功率恢复正常后清零。
	#  BIT[7] - 温度错误置1，温度恢复正常后清零。
	def query_status(self, servo_id):
		'''查询工作状态'''
		status_bytes = self.read_data(servo_id, self.ADDRESS_STATUS)
		return struct.unpack('<B', status_bytes)[0]

	def set_origin_point(self, servo_id:int):
		'''发送设置原点请求'''
		self.send_request(self.CODE_SET_ORIGIN_POINT, struct.pack('<BB', servo_id, 0))

	def reset_multi_turn_angle(self, servo_id:int):
		'''发送重设多圈角度请求'''
		self.send_request(self.CODE_RESET_MULTI_TURN_ANGLE, struct.pack('<B', servo_id))
	
	def disable_torque(self, servo_id:int):
		'''发送禁用力矩请求'''
		self.wheel_stop(servo_id)

		##请求数据监控
	def query_servo_monitor(self, servo_id):   
		if self.is_debug:
			logging.info('单个舵机 id={}'.format(servo_id))
		self.send_request(self.CODE_QUERY_SERVO_MONITOR, struct.pack('<B', servo_id))
		self.update(wait_response=True) # 等待数据回传
		servo_info = self.servos.get(servo_id)   
		if servo_info:
			return {
				"voltage": servo_info.voltage,
				"current": servo_info.current,
				"power": servo_info.power,
				"temp": servo_info.temp,
				"status": servo_info.status,
				"angle": servo_info.angle_monitor,
				"turn": servo_info.turn
			}
		else:
			return None

		##反馈数据监控数据
	def response_query_servo_monitor(self, param_bytes):
		# 数据解包
		servo_id, voltage, current, power, temp_raw, status, angle, turn = struct.unpack('<BHHHHBih', param_bytes)
		# 舵机的分辨率是0.1度
		angle /= 10.0

		# 计算对数的参数
		log_param = ( temp_raw) /   (4096 - temp_raw)
		
		# 检查参数是否为正数，避免math domain error
		if log_param > 0:	
			# 计算温度
			temp = float(1 / ((math.log(log_param) / 3435) + 1 / (273.15 + 25)) - 273.15)
		else :
			temp =0


		if servo_id not in self.servos:
			return
        # 更新
		self.servos[servo_id].voltage = voltage
		self.servos[servo_id].current = current
		self.servos[servo_id].power = power
		self.servos[servo_id].temp = temp
		self.servos[servo_id].status = status
		self.servos[servo_id].angle_monitor = angle
		self.servos[servo_id].turn = turn
		if self.is_debug:
			logging.info('舵机电压: {:.2f} V电流: {:.2f}A 功率: {:.2f} W温度: {:.2f} ℃ 状态: {:.2f} 角度: {:.2f} ° 圈数: {:.0f} '.format(voltage/1000, current/1000, power/1000, temp, status, angle, turn))

		##停止指令
	def stop_on_control_mode(self, servo_id, method, power):
		'''
		@param servo_id
			舵机的ID号
		@param method
			舵机停止指令的执行模式 
			0x10-停止后卸力(失锁)
			0x11-停止后保持锁力
			0x12-停止后进入阻尼状态
		@param power
			保持的功率
		'''
		if self.is_debug:
			logging.info('控制模式停止指令 id={} method={} power={} mW'.format(servo_id, method, power))		
        # 打包请求数据
		param_bytes = struct.pack('<BBH', servo_id, method, power)
		self.send_request(self.CODE_SET_STOP_ON_CONTROL, param_bytes)
		
		##同步命令角度模式控制
	def send_sync_angle(self, command_id, servo_num, command_data_list):
		'''发送同步命令
		@param command_id
			命令编号
		@param servo_num
			舵机个数
		@param command_data_list
			命令数据列表，每个元素为一个舵机的命令数据
		'''
		# 计算命令数据的总长度
		total_data_length =  7               
		# 构建参数字节流
		param_bytes = struct.pack('<BBB', command_id, total_data_length, servo_num)
		for command_data in command_data_list:
			param_bytes += command_data
		# 发送请求
		self.send_request(self.CODE_SYNC_COMMAND, param_bytes)

		##同步命令角度模式控制(基于加减速时间)
	def send_sync_anglebyinterval(self, command_id, servo_num, command_data_list):
		'''发送同步命令
		@param command_id
			命令编号
		@param servo_num
			舵机个数
		@param command_data_list
			命令数据列表，每个元素为一个舵机的命令数据
		'''
		# 计算命令数据的总长度
		total_data_length =  11               
		# 构建参数字节流
		param_bytes = struct.pack('<BBB', command_id, total_data_length, servo_num)
		for command_data in command_data_list:
			param_bytes += command_data
		# 发送请求
		self.send_request(self.CODE_SYNC_COMMAND, param_bytes)

		##同步命令角度模式控制(基于目标速度)
	def send_sync_anglebyvelocity(self, command_id, servo_num, command_data_list):
		'''发送同步命令
		@param command_id
			命令编号
		@param servo_num
			舵机个数
		@param command_data_list
			命令数据列表，每个元素为一个舵机的命令数据
		'''
		# 计算命令数据的总长度
		total_data_length =  11               
		# 构建参数字节流
		param_bytes = struct.pack('<BBB', command_id, total_data_length, servo_num)
		for command_data in command_data_list:
			param_bytes += command_data
		# 发送请求
		self.send_request(self.CODE_SYNC_COMMAND, param_bytes)
		time.sleep(0.001)

		##同步命令多圈角度模式控制
	def send_sync_multiturnangle(self, command_id, servo_num, command_data_list):
		'''发送同步命令
		@param command_id
			命令编号
		@param servo_num
			舵机个数
		@param command_data_list
			命令数据列表，每个元素为一个舵机的命令数据
		'''
		# 计算命令数据的总长度
		total_data_length =  11               
		# 构建参数字节流
		param_bytes = struct.pack('<BBB', command_id, total_data_length, servo_num)
		for command_data in command_data_list:
			param_bytes += command_data
		# 发送请求
		self.send_request(self.CODE_SYNC_COMMAND, param_bytes)

		##同步命令多圈角度模式控制(基于加减速时间)
	def send_sync_multiturnanglebyinterval(self, command_id, servo_num, command_data_list):
		'''发送同步命令
		@param command_id
			命令编号
		@param servo_num
			舵机个数
		@param command_data_list
			命令数据列表，每个元素为一个舵机的命令数据
		'''
		# 计算命令数据的总长度
		total_data_length =  15               
		# 构建参数字节流
		param_bytes = struct.pack('<BBB', command_id, total_data_length, servo_num)
		for command_data in command_data_list:
			param_bytes += command_data
		# 发送请求
		self.send_request(self.CODE_SYNC_COMMAND, param_bytes)

		##同步命令多圈角度模式控制(基于目标速度)
	def send_sync_multiturnanglebyvelocity(self, command_id, servo_num, command_data_list):
		'''发送同步命令
		@param command_id
			命令编号
		@param servo_num
			舵机个数
		@param command_data_list
			命令数据列表，每个元素为一个舵机的命令数据
		'''
		# 计算命令数据的总长度
		total_data_length =  13               
		# 构建参数字节流
		param_bytes = struct.pack('<BBB', command_id, total_data_length, servo_num)
		for command_data in command_data_list:
			param_bytes += command_data
		# 发送请求
		self.send_request(self.CODE_SYNC_COMMAND, param_bytes)

		##同步命令数据监控
	def send_sync_servo_monitor(self, servo_ids):
		'''发送同步命令多个舵机的数据监控
		@param servo_ids
		舵机个数
		'''
		command_id = 0x16  
		# 舵机ID数量 		
		servo_num = len(servo_ids)
		# 构建参数字节流
		param_bytes = struct.pack('<BBB', command_id, 1,servo_num)  # 包含命令编号和舵机ID数量
		for servo_id in servo_ids:
			param_bytes += struct.pack('<B', servo_id)  # 每个舵机ID单独打包
		# 发送请求
		self.send_request(self.CODE_SYNC_COMMAND, param_bytes)
		self.monitor_update(servo_num)
		# 收集所有舵机的监控数据
		return {servo_id: self.servos.get(servo_id) for servo_id in servo_ids}

		##开始异步命令
	def begin_async(self):
		self.send_request(self.CODE_BEGIN_ASYNC,b'')

		##结束异步命令
	def end_async(self, cancel:int):
		self.send_request(self.CODE_END_ASYNC, struct.pack('<B', cancel))

	def update(self, is_empty_buffer=False, wait_response=False, timeout=0.1):
		'''舵机管理器的定时器回调函数'''
		t_start = time.time() # 获取开始时间
		# idle_threshold = 0.0002  # 0.2ms空闲认为数据结束
		# last_data_time = t_start
		buffer = bytearray()
		while True:
			bytes_waiting = self.uart.in_waiting
			if bytes_waiting:
				data = self.uart.read(bytes_waiting)
				buffer.extend(data)
			else :
				if (time.time() - t_start) > timeout:
					break

		# 相应回调数据
		for b in buffer:
			self.pkt_buffer.update(struct.pack('<B', b))
		while self.pkt_buffer.has_valid_packet():
			# 处理现有的返回数据帧
			response_bytes = self.pkt_buffer.get_packet()
			result = Packet.unpack(response_bytes)
			if result is None:
				continue
			# 解包
			code, param_bytes = result
			# 根据code找到相应处理函数
			handler = self.response_handle_funcs.get(code)
			if handler:
				handler(param_bytes)
			else:
				logging.warning('未知功能码 : {}'.format(code))		
		# 清空原来的缓冲区
		if is_empty_buffer:
			self.pkt_buffer.empty_buffer()		

	



	def monitor_update(self,servo_num , timeout=0.1):
		'''舵机管理器的定时器回调函数'''
		t_start = time.time() # 获取开始时间
		buffer = bytearray()
		start_flag = 0
		ok_flag = 0
		bytes_waiting = 0
		if t_start - self.loss_uservo_record_time > 1:
			# print("check",self.loss_uservo)
			self.loss_uservo_record_time = t_start
			if self.loss_uservo >10:
				raise OSError(f"Please restore the robotic arm to the standby position and power it on again.")
			else:
				self.loss_uservo = 0

		while True:
			bytes_waiting = self.uart.in_waiting
			if bytes_waiting:
				if ok_flag == 0:
					data = self.uart.read(1)
					if data == b'\x05':
						start_flag = 1
					elif data == b'\x1c' and start_flag == 1:
						ok_flag = 1
						buffer.extend(b'\x05')
						buffer.extend(b'\x1c')	
				elif ok_flag == 1:
					if bytes_waiting >= 19:
						data = self.uart.read(19)
						buffer.extend(data)		
						ok_flag = 2			
				elif ok_flag == 2:
					if bytes_waiting >= 21:
						data = self.uart.read(21)
						buffer.extend(data)		
					else:
						if len(buffer) >=servo_num*21:
							break
				if (time.time() - t_start) > timeout:
					# print(f"{self.uart},monitor_update timeout")
					break	
					
			else :
				if len(buffer) >=servo_num*21:
					break
				if (time.time() - t_start) > timeout:
					if len(buffer) == 0:
						self.loss_uservo +=1
					# print(f"{self.uart},miss {int((servo_num*21 - len(buffer))/21)} servo")
					break
		# 相应回调数据
		for b in buffer:
			self.pkt_buffer.update(struct.pack('<B', b))
		while self.pkt_buffer.has_valid_packet():
			# 处理现有的返回数据帧
			response_bytes = self.pkt_buffer.get_packet()
			result = Packet.unpack(response_bytes)
			if result is None:
				continue
			# 解包
			code, param_bytes = result
			# 根据code找到相应处理函数
			handler = self.response_handle_funcs.get(code)
			if handler:
				handler(param_bytes)
			else:
				logging.warning('未知功能码 : {}'.format(code))		
		# 清空原来的缓冲区
		self.pkt_buffer.empty_buffer()	
