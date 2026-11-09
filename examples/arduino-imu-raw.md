<!-- SPDX-License-Identifier: MIT -->
# imu_raw 逐片拆解（Arduino 第一个示例）

> 一步步看 `xiao_robot_kit_arduino/examples/imu_raw/imu_raw.ino`。
> 这是整个套件最小的完整链路：**IMU → 驱动换算 → CSV 波形**。
> 全程没有量程/速率魔法数字——一切来自预设表。

## 骨架（setup / loop 两段，无平台睡坑）

```
setup():
  Serial 115200 + 等 CDC 枚举
  imu_cfg_find("imu.raw.104")   ← 参数源：预设表（零写死）
  arduino_wire_i2c_init(...)    ← Wire → 驱动函数指针表（薄胶水）
  lsm6ds3_init / probe / configure
  Serial 打印 OK stream + CSV 标签行
loop():
  millis 域节拍对齐（无累积漂移）
  lsm6ds3_read → CSV 六轴输出
```

## 三段关键代码

**① 参数从哪来（预设表，不是 define）**

```c
const imu_cfg_t *cfg = imu_cfg_find("imu.raw.104");
s_period_ms = cfg->sample_period_ms;   /* 采样节拍 104ms 来自表 */
```

改采样率 = 换预设名（`imu.raw.208` 等），改代码=反模式。

**② I2C 胶水（一行接线）**

```c
arduino_wire_i2c_init(&s_bus, cfg->i2c_speed_hz, /*SDA*/5, /*SCL*/6);
```

换板只改这两个数字。C 核心永远看不到 Arduino 头。

**③ 链路探测（不静默失败）**

```c
for (;;) {
    int r = lsm6ds3_probe(&s_imu);
    if (r == 0) break;
    Serial.println(r == -2 ? "ERR who_am_i mismatch" : "ERR i2c no ack, retry 1s");
    delay(1000);
}
```

- `-2` = WHO_AM_I 对不上（芯片不是 0x6A / 接线错）
- 其他负值 = I2C 无应答（查供电、SDA/SCL）

## 跑通之后你可以改什么

| 想改 | 改哪里 |
| --- | --- |
| 采样更快 | 预设表换 `imu.raw.*` 高档位（看 `imu_cfg_presets.c`） |
| 换 I2C 引脚 | `PIN_I2C_SDA/SCL` 两个常量 |
| 输出加温度 | 看 `imu_sample_temp_t`（驱动另有一通道） |
| 串口改 921600 | `UART_BAUD`（Plotter 也改） |

## 验收复查

- 静置 `az≈+1g`，动板子三轴陀螺跟手 → 链路 OK
- 串口绘图器六条曲线滚动 → 输出 OK