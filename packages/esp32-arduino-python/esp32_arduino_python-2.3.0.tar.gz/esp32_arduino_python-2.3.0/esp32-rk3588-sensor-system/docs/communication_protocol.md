# RK3588 ↔ ESP32 通信协议

## 协议格式
- 波特率: 115200
- 数据位: 8
- 停止位: 1
- 校验位: None
- 结束符: \n

## 命令格式
```
发送: CMD:PARAM\n
响应: OK:DATA\n 或 ERROR:MSG\n
```

## 支持的命令

### 1. 系统命令
- `PING:` - 测试连接
  - 响应: `OK:PONG`

- `INFO:` - 获取系统信息
  - 响应: `OK:ESP32_V1.0_MAC:xx:xx:xx:xx:xx:xx`

- `RESET:` - 重启ESP32
  - 响应: `OK:RESET`

### 2. 传感器命令
- `READ:TEMP` - 读取温度
  - 响应: `OK:25.6` 或 `ERROR:SENSOR_NOT_FOUND`

- `READ:HUMIDITY` - 读取湿度
  - 响应: `OK:60.2` 或 `ERROR:SENSOR_NOT_FOUND`

- `READ:ALL` - 读取所有传感器
  - 响应: `OK:TEMP:25.6,HUMIDITY:60.2`

### 3. GPIO命令
- `SET:LED:ON` - 开启LED
  - 响应: `OK:LED_ON`

- `SET:LED:OFF` - 关闭LED
  - 响应: `OK:LED_OFF`

- `GET:GPIO:2` - 读取GPIO2状态
  - 响应: `OK:HIGH` 或 `OK:LOW`

## 错误码
- `ERROR:UNKNOWN_CMD` - 未知命令
- `ERROR:INVALID_PARAM` - 参数错误
- `ERROR:SENSOR_ERROR` - 传感器错误
- `ERROR:TIMEOUT` - 超时错误 