/*
 * ESP32 传感器控制系统 - 传感器管理模块
 * 负责读取和管理传感器数据
 */

#include "sensor_manager.h"
#include "dht11_sensor.h"
#include "driver/adc.h"

// 全局变量
float temperature = 25.0;
float humidity = 60.0;
unsigned long last_sensor_read = 0;
SensorMode current_sensor_mode = SENSOR_MODE_DHT11;
bool dht11_available = false;
bool adc_initialized = false;

void init_sensors() {
  Serial.println("正在初始化传感器系统...");

  // 首先尝试初始化DHT11
  Serial.println("尝试初始化DHT11传感器...");
  if (dht11_sensor.begin()) {
    dht11_available = true;
    current_sensor_mode = SENSOR_MODE_DHT11;
    Serial.println("DHT11传感器初始化成功，将作为主要传感器");
  } else {
    Serial.println("DHT11传感器初始化失败，将使用ADC模拟传感器");
    dht11_available = false;
    current_sensor_mode = SENSOR_MODE_ADC;

    // 初始化ADC作为备用
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(TEMP_ADC_CHANNEL, ADC_ATTEN_DB_12);   // 温度传感器ADC通道
    adc1_config_channel_atten(HUMID_ADC_CHANNEL, ADC_ATTEN_DB_12);  // 湿度传感器ADC通道
    adc_initialized = true;
  }

  Serial.print("传感器系统初始化完成，当前模式: ");
  Serial.println(current_sensor_mode == SENSOR_MODE_DHT11 ? "DHT11数字传感器" : "ADC模拟传感器");
}

void update_sensors() {
  unsigned long current_time = millis();
  if (current_time - last_sensor_read >= SENSOR_INTERVAL) {

    if (current_sensor_mode == SENSOR_MODE_DHT11 && dht11_available) {
      // 使用DHT11传感器
      if (dht11_sensor.update()) {
        temperature = dht11_sensor.getTemperature();
        humidity = dht11_sensor.getHumidity();
      } else {
        // DHT11读取失败，检查是否需要切换到ADC模式
        if (dht11_sensor.getConsecutiveErrors() > 5) {
          Serial.println("DHT11连续错误过多，切换到ADC模拟传感器");
          current_sensor_mode = SENSOR_MODE_ADC;
          if (!adc_initialized) {
            adc1_config_width(ADC_WIDTH_BIT_12);
            adc1_config_channel_atten(TEMP_ADC_CHANNEL, ADC_ATTEN_DB_12);
            adc1_config_channel_atten(HUMID_ADC_CHANNEL, ADC_ATTEN_DB_12);
            adc_initialized = true;
          }
        }
      }
    } else {
      // 使用ADC模拟传感器
      temperature = read_temperature();
      humidity = read_humidity();

      // 定期检查DHT11是否恢复
      if (dht11_available && dht11_sensor.getConsecutiveErrors() > 0) {
        if (dht11_sensor.forceRead()) {
          Serial.println("DHT11传感器恢复，切换回DHT11模式");
          current_sensor_mode = SENSOR_MODE_DHT11;
          temperature = dht11_sensor.getTemperature();
          humidity = dht11_sensor.getHumidity();
        }
      }
    }

    last_sensor_read = current_time;
  }
}

float read_temperature() {
  if (current_sensor_mode == SENSOR_MODE_DHT11 && dht11_available) {
    return dht11_sensor.getTemperature();
  } else {
    // ADC模拟温度传感器读取
    int temp_raw = adc1_get_raw(TEMP_ADC_CHANNEL);
    float temp_voltage = (temp_raw / 4095.0) * 3.3;
    float temp = 20.0 + (temp_voltage * 20.0) + random(-50, 50) / 100.0;
    return constrain(temp, -10.0, 50.0);
  }
}

float read_humidity() {
  if (current_sensor_mode == SENSOR_MODE_DHT11 && dht11_available) {
    return dht11_sensor.getHumidity();
  } else {
    // ADC模拟湿度传感器读取
    int humid_raw = adc1_get_raw(HUMID_ADC_CHANNEL);
    float humid_voltage = (humid_raw / 4095.0) * 3.3;
    float humid = 40.0 + (humid_voltage * 30.0) + random(-100, 100) / 100.0;
    return constrain(humid, 0.0, 100.0);
  }
}

void set_sensor_mode(SensorMode mode) {
  if (mode == SENSOR_MODE_DHT11 && dht11_available) {
    current_sensor_mode = SENSOR_MODE_DHT11;
    Serial.println("切换到DHT11传感器模式");
  } else if (mode == SENSOR_MODE_ADC) {
    current_sensor_mode = SENSOR_MODE_ADC;
    Serial.println("切换到ADC模拟传感器模式");
  } else {
    Serial.println("无法切换到指定传感器模式");
  }
}

SensorMode get_sensor_mode() {
  return current_sensor_mode;
}

bool is_dht11_available() {
  return dht11_available;
}

String get_sensor_status() {
  String status = "传感器状态信息:\\n";
  status += "当前模式: " + String(current_sensor_mode == SENSOR_MODE_DHT11 ? "DHT11" : "ADC") + "\\n";
  status += "DHT11可用: " + String(dht11_available ? "是" : "否") + "\\n";

  if (dht11_available) {
    status += "DHT11状态: " + dht11_sensor.getStatusString() + "\\n";
    status += "DHT11错误次数: " + String(dht11_sensor.getConsecutiveErrors()) + "\\n";
    status += "DHT11数据新鲜度: " + String(dht11_sensor.isDataFresh() ? "新鲜" : "过期") + "\\n";
  }

  status += "当前温度: " + String(temperature, 1) + "°C\\n";
  status += "当前湿度: " + String(humidity, 1) + "%\\n";
  status += "最后更新: " + String(last_sensor_read) + "ms";

  return status;
}