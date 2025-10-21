/*
 * ESP32 传感器控制系统 - DHT11传感器模块实现
 * 负责DHT11数字温湿度传感器的读取和管理
 */

#include "dht11_sensor.h"
#include <WiFi.h>

// 全局DHT11传感器实例定义
DHT11Sensor dht11_sensor;

// 构造函数
DHT11Sensor::DHT11Sensor() {
    dht = nullptr;
    lastTemperature = 0.0;
    lastHumidity = 0.0;
    lastReadTime = 0;
    lastSuccessTime = 0;
    lastStatus = DHT11_NOT_INITIALIZED;
    consecutiveErrors = 0;
}

// 析构函数
DHT11Sensor::~DHT11Sensor() {
    if (dht != nullptr) {
        delete dht;
        dht = nullptr;
    }
}

// 初始化传感器
bool DHT11Sensor::begin() {
    Serial.println("正在初始化DHT11传感器...");

    // 创建DHT对象
    dht = new DHT(DHT11_PIN, DHTTYPE);

    if (dht == nullptr) {
        Serial.println("错误: 无法创建DHT对象");
        lastStatus = DHT11_ERROR_CONNECT;
        return false;
    }

    // 启动传感器
    dht->begin();

    // 等待传感器稳定
    delay(1000);

    // 尝试读取一次测试
    float testTemp = dht->readTemperature();
    float testHumid = dht->readHumidity();

    if (isnan(testTemp) || isnan(testHumid)) {
        Serial.println("警告: DHT11传感器初始化测试失败，但传感器可能仍可工作");
        lastStatus = DHT11_ERROR_CONNECT;
        consecutiveErrors = 1;
        return false;
    }

    lastTemperature = testTemp;
    lastHumidity = testHumid;
    lastSuccessTime = millis();
    lastStatus = DHT11_OK;
    consecutiveErrors = 0;

    Serial.println("DHT11传感器初始化成功");
    Serial.print("测试温度: ");
    Serial.print(lastTemperature);
    Serial.print("°C, 湿度: ");
    Serial.print(lastHumidity);
    Serial.println("%");

    return true;
}

// 更新传感器数据（非阻塞）
bool DHT11Sensor::update() {
    unsigned long currentTime = millis();

    // 检查是否到了读取时间
    if (currentTime - lastReadTime < READ_INTERVAL) {
        return (lastStatus == DHT11_OK);
    }

    lastReadTime = currentTime;

    // 执行读取
    return forceRead();
}

// 强制读取传感器数据（阻塞）
bool DHT11Sensor::forceRead() {
    if (dht == nullptr) {
        lastStatus = DHT11_NOT_INITIALIZED;
        handleError(DHT11_NOT_INITIALIZED);
        return false;
    }

    // 读取温湿度
    float temp = dht->readTemperature();
    float humid = dht->readHumidity();

    // 检查读取是否成功
    if (isnan(temp) || isnan(humid)) {
        lastStatus = DHT11_ERROR_TIMEOUT;
        handleError(DHT11_ERROR_TIMEOUT);
        return false;
    }

    // 验证数据合理性
    if (!validateReading(temp, humid)) {
        lastStatus = DHT11_ERROR_CHECKSUM;
        handleError(DHT11_ERROR_CHECKSUM);
        return false;
    }

    // 数据有效，更新缓存
    lastTemperature = temp;
    lastHumidity = humid;
    lastSuccessTime = millis();
    lastStatus = DHT11_OK;
    consecutiveErrors = 0;

    return true;
}

// 获取温度值
float DHT11Sensor::getTemperature() {
    return lastTemperature;
}

// 获取湿度值
float DHT11Sensor::getHumidity() {
    return lastHumidity;
}

// 获取最后状态
DHT11Status DHT11Sensor::getStatus() {
    return lastStatus;
}

// 获取状态描述字符串
String DHT11Sensor::getStatusString() {
    switch (lastStatus) {
        case DHT11_OK:
            return "正常";
        case DHT11_ERROR_TIMEOUT:
            return "读取超时";
        case DHT11_ERROR_CHECKSUM:
            return "数据校验错误";
        case DHT11_ERROR_CONNECT:
            return "连接问题";
        case DHT11_NOT_INITIALIZED:
            return "未初始化";
        default:
            return "未知状态";
    }
}

// 检查传感器是否可用
bool DHT11Sensor::isAvailable() {
    return (dht != nullptr) && (lastStatus == DHT11_OK || consecutiveErrors < 5);
}

// 检查数据是否新鲜（有效期内）
bool DHT11Sensor::isDataFresh() {
    unsigned long currentTime = millis();
    return (currentTime - lastSuccessTime < READ_INTERVAL * 2);
}

// 获取最后成功读取时间
unsigned long DHT11Sensor::getLastSuccessTime() {
    return lastSuccessTime;
}

// 获取连续错误次数
int DHT11Sensor::getConsecutiveErrors() {
    return consecutiveErrors;
}

// 重置错误计数
void DHT11Sensor::resetErrorCount() {
    consecutiveErrors = 0;
}

// 获取传感器信息
String DHT11Sensor::getSensorInfo() {
    String info = "DHT11传感器信息:\\n";
    info += "  引脚: GPIO" + String(DHT11_PIN) + "\\n";
    info += "  类型: DHT11\\n";
    info += "  状态: " + getStatusString() + "\\n";
    info += "  当前温度: " + String(lastTemperature, 1) + "°C\\n";
    info += "  当前湿度: " + String(lastHumidity, 1) + "%\\n";
    info += "  最后成功读取: " + String(lastSuccessTime) + "ms\\n";
    info += "  连续错误: " + String(consecutiveErrors) + "次\\n";
    info += "  数据新鲜度: " + String(isDataFresh() ? "新鲜" : "过期");
    return info;
}

// 内部错误处理
void DHT11Sensor::handleError(DHT11Status status) {
    consecutiveErrors++;

    // 错误日志输出
    Serial.print("DHT11错误 [");
    Serial.print(consecutiveErrors);
    Serial.print("]: ");
    Serial.println(getStatusString());

    // 连续错误过多时的处理
    if (consecutiveErrors >= 10) {
        Serial.println("DHT11传感器连续错误过多，尝试重新初始化");
        // 可以在这里添加重新初始化逻辑
    }
}

// 验证读取数据的合理性
bool DHT11Sensor::validateReading(float temp, float humid) {
    // DHT11规格检查
    if (temp < 0.0 || temp > 50.0) {
        Serial.print("温度值超出范围: ");
        Serial.println(temp);
        return false;
    }

    if (humid < 20.0 || humid > 90.0) {
        Serial.print("湿度值超出范围: ");
        Serial.println(humid);
        return false;
    }

    // 检查数据是否有剧烈变化（可能表示通信错误）
    if (lastStatus == DHT11_OK) {
        float tempDiff = abs(temp - lastTemperature);
        float humidDiff = abs(humid - lastHumidity);

        // DHT11变化相对缓慢，单次变化过大可能有问题
        if (tempDiff > 10.0 || humidDiff > 20.0) {
            Serial.print("检测到数据剧烈变化 - 温度变化: ");
            Serial.print(tempDiff);
            Serial.print("°C, 湿度变化: ");
            Serial.print(humidDiff);
            Serial.println("%");
            return false;
        }
    }

    return true;
}