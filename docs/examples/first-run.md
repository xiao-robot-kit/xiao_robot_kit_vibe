<!-- SPDX-License-Identifier: MIT -->
# 第一次跑通：30 分钟从零到有波形

> 目标：不管你是 IDF 还是 Arduino 用户，先选一条路跑出一个真实波形。
> 跑通了，库环境 = OK，后面所有示例都是同一套玩法。

## 选哪条路

| 你的工具链 | 走这条 | 产物 |
| --- | --- | --- |
| ESP-IDF CLI | **P-00（第一步）** → [P-01 IMU 采样](../tutorials/idf.md) | 启动自检 → IMU 数据流 |
| Arduino IDE | [imu_raw](../tutorials/arduino.md) | Serial Plotter 六轴波形 |

如果你刚拿到板子、还不确定工具链是否装对，**先跑 P-00**：

```bash
cd xiao_robot_kit_idf/examples/periph/P-00_hello_bringup
idf.py set-target esp32s3
idf.py build flash monitor
```

看到 `OK boot P-00_hello_bringup` + 版本号 + 复位原因 = 工具链、串口、板子
三件事都对。它不接任何外设，所以排除了接线变量。

然后再跑 IMU（P-01 / Arduino 的 imu_raw）做的是同一件事：
**读 LSM6DS3TR-C 六轴 IMU → 物理量（g / dps）→ 输出**。

## 跑通判定（一定要看到这些才叫跑通）

1. 串口 115200,8N1 有输出（Arduino Plotter / IDF monitor 都行）
2. 板子**水平静置**：`az ≈ ±1g`（换个面放就变号），`ax/ay ≈ 0`
3. 三轴陀螺仪 `gx/gy/gz ≈ 0`（静止零转速的理论值）
4. 手拿起板子快速转 → 角速度曲线跟手动（陀螺仪在干活）

## 接线清单（无杜邦线——IMU 在扩展板上已接好）

- 板载 IMU 走 D4/D5，**不需要接线**
- USB-C 一根，插上既是供电也是串口（USB-Serial-JTAG）
- 舵机/电机才接线（见 [外设例程索引](periph-index.md) 里的 P-05 / P-07）

## 如果没波形（自检顺序）

| 现象 | 大概率原因 | 修法 |
| --- | --- | --- |
| 串口根本没出现 | 线/驱动 | 换线、重插、看设备管理器 |
| 串口有乱码 | 波特率错了 | 统一 115200,8N1 |
| `ERR who_am_i mismatch` | IMU 没被探测到 | 查供电/接线（板载常见：Bus 号或 SDA/SCL 反） |
| `ERR i2c no ack` | I2C 没应答 | 同上；确认引脚是 5/6 |
| 波形全是 0 | 配置没生效或采样失败 | 看 `fatal()` 打印；重新上电 |

## 下一步

- **想逐个玩板上的外设**：看 [外设例程索引](periph-index.md)（P-00~P-12，按
  「我想干什么」分组：动起来 / 灯光 / 传感器 / 电源 / 闭环 / 存参数）
- 想看姿态（roll/pitch/yaw）：去 [attitude_print](arduino-attitude-print.md)
- 想动电机：去 [motor_sweep](arduino-motor-sweep.md)（Arduino）或 P-05~P-07（IDF）