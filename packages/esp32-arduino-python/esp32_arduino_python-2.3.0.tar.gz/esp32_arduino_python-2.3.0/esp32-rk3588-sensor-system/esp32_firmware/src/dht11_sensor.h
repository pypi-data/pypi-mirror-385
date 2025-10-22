/*
 * ESP32 传感器控制系统 - DHT11传感器模块
 * 负责DHT11数字温湿度传感器的读取和管理
 */

#ifndef DHT11_SENSOR_H
#define DHT11_SENSOR_H

#include <Arduino.h>
#include <DHT.h>
#include "pin_config.h"

// DHT11传感器状态枚举
enum DHT11Status {
    DHT11_OK = 0,           // 传感器正常
    DHT11_ERROR_TIMEOUT,    // 读取超时
    DHT11_ERROR_CHECKSUM,   // 校验和错误
    DHT11_ERROR_CONNECT,    // 连接问题
    DHT11_NOT_INITIALIZED   // 未初始化
};

// DHT11传感器类
class DHT11Sensor {
private:
    DHT* dht;                    // DHT传感器对象
    float lastTemperature;       // 最后读取的温度值
    float lastHumidity;          // 最后读取的湿度值
    unsigned long lastReadTime;  // 最后读取时间
    unsigned long lastSuccessTime; // 最后成功读取时间
    DHT11Status lastStatus;      // 最后的状态
    int consecutiveErrors;       // 连续错误计数
    const unsigned long READ_INTERVAL = 2000; // DHT11最小读取间隔2秒

    // 内部错误处理
    void handleError(DHT11Status status);
    bool validateReading(float temp, float humid);

public:
    // 构造函数
    DHT11Sensor();

    // 析构函数
    ~DHT11Sensor();

    // 初始化传感器
    bool begin();

    // 更新传感器数据（非阻塞）
    bool update();

    // 强制读取传感器数据（阻塞）
    bool forceRead();

    // 获取温度值
    float getTemperature();

    // 获取湿度值
    float getHumidity();

    // 获取最后状态
    DHT11Status getStatus();

    // 获取状态描述字符串
    String getStatusString();

    // 检查传感器是否可用
    bool isAvailable();

    // 检查数据是否新鲜（有效期内）
    bool isDataFresh();

    // 获取最后成功读取时间
    unsigned long getLastSuccessTime();

    // 获取连续错误次数
    int getConsecutiveErrors();

    // 重置错误计数
    void resetErrorCount();

    // 获取传感器信息
    String getSensorInfo();
};

// 全局DHT11传感器实例声明
extern DHT11Sensor dht11_sensor;

#endif // DHT11_SENSOR_H