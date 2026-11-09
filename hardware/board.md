<!-- SPDX-License-Identifier: MIT -->
# 硬件介绍：XIAO Robot Board V1.0（XIAO ESP32-S3）

> 一句话：一块「双电机闭环 + 四舵机 + 灯效 + IMU」的小机器人主板，
> **20 个 GPIO 全部用满**，扩展只能走 I2C / UART。
>
> 本页是**速查表**；完整能力（每个 IO 能做什么 / 每个接口能接什么 / 电源怎么走 /
> 有哪些坑 / 未验证项）见 [硬件能力报告](hardware-capability.md)，逐例程验收标准见
> [例程规格](periph-spec.md)。两者不一致时以 hardware-capability.md 为准。

## 核心板：XIAO ESP32-S3

- 主控：XIAO ESP32-S3（Plus 版）
- 烧录/调试/供电：USB-C（USB 2.0，USB CDC 串口日志）
- 复位键：K6（EN）

## 板载 / 扩展板器件

| 器件 | 型号 | 接口 | 对应组件 |
| --- | --- | --- | --- |
| 六轴 IMU | LSM6DS3TR-C | I2C（与 Grove 口共总线），**INT1 未接 MCU**，只能轮询 | `xiao_imu` |
| 双路 H 桥 ×2 | GC9112（U14=M1、U16=M2） | IN1/IN2 差分 PWM | `xiao_motor` |
| 舵机 PWM ×4 | — | 50Hz LEDC，独立 4 路 | `xiao_motor` |
| IMU 加热 | Q1 NMOS + 加热电阻 | D12 PWM 控制 | `xiao_imu_heater` |
| RGB 缓冲 | SN74LVC1G17 | 3.3V → 5V 电平，串 22R | — |
| 电池 | 1S 锂电座 + 充电管理 | D16 ADC 分压采样 100K:30K | `xiao_battery` |
| 用户按键 | K7 | D11 直连 | — |
| 参数存储 | 板载 flash | 裸分区 `store` | `xiao_pstore` |

## 引脚分配表（全 20 脚占用，无空余）

| XIAO 脚 | 分配 | 串联/保护 | 去向 |
| --- | --- | --- | --- |
| D0 | SERVO3 PWM | R61(0R)+ESD | J13.1 |
| D1 | M1_PWM1 | R29(22R) | U14(GC9112).IN1 |
| D2 | M1_PWM2 | R30(22R) | U14.IN2 |
| D3 | M1_ENC_A 输入 | R48(22R)+ESD | J8.3 |
| D4 | **I2C1_SDA** | R25(22R)+ESD | J11.2 + J12.2 + U18.14 |
| D5 | **I2C1_SCL** | R26(22R)+ESD | J11.1 + J12.1 + U18.13 |
| D6 | UART0_TX | R27(**0R** 跳线)+ESD | J10.1 |
| D7 | UART0_RX | R28(**0R** 跳线)+ESD | J10.2 |
| D8 | SERVO4 PWM | R96(0R)+ESD | J14.1 |
| D9 | SERVO2 PWM | R41(0R)+ESD | J5.1 |
| D10 | M2_ENC_B 输入 | R53(22R)+ESD | J9.4 |
| D11 | 用户按键 K7 | 面板按键 | 侧面按钮 |
| D12 | IMU 加热 PWM | R76(100R) | Q1 NMOS 栅极 → 加热电阻 |
| D13 | RGB 数据 | R79(22R) → U4 缓冲 → R52(22R) | J7.1 |
| D14 | M1_ENC_B 输入 | R49(22R)+ESD | J8.4 |
| D15 | SERVO1 PWM | R35(0R)+ESD | J1.1 |
| D16 | 电池 ADC | R109(100K)+R74(30K) 分压 | VBAT_IN |
| D17 | M2_ENC_A 输入 | R51(22R)+ESD | J9.3 |
| D18 | M2_PWM2 | R32(22R) | U16.IN2 |
| D19 | M2_PWM1 | R31(22R) | U16.IN1 |

**电池换算**：`Vbat = Vadc × 130/30`。满电 4.2V → 0.97V；3.0V → 0.69V（12dB 量程内）。

**电机口共享**：J4/J6（GH 1.25mm 2P 直流口）与 J8/J9（ZH 1.5mm 6P 编码器口）
**共享同一对输出**——同一时刻只能接其中一种电机。

**备用引脚**：模块底面 pad24(MTDI)、pad25(MTDO) 引至测试点 **TP20/TP21**，
是全板唯一可飞线的备用 GPIO（注意 strapping 属性，见 [P-12](../examples/periph-index.md#p-12)）。

## 接口位置

| 接口 | 板位 | 引脚 |
| --- | --- | --- |
| 电机 M1 | J4（直流）/ J8（编码器） | 1=M1_OUT+, 2=ENC VCC, 3=ENC_A(D3), 4=ENC_B(D14), 5=GND, 6=M1_OUT− |
| 电机 M2 | J6（直流）/ J9（编码器） | 3=ENC_A(D17), 4=ENC_B(D10)，其余同 J8 |
| 舵机 S1~S4 | J1 / J5 / J13 / J14 | 1=PWM(D15/D9/D0/D8), 2.0mm 4P |
| RGB 灯带 | J7 | 1=数据(D13), 5V 供电 |
| I2C Grove ×2 | J11 / J12 | 1=SCL(D5), 2=SDA(D4), 3=3V3, 4=GND |
| UART Grove | J10 | 1=TX(D6), 2=RX(D7), 3=3V3, 4=GND |
| 电池 | J3 | JST-PH 2.0 |

## I2C 总线约定

板载 IMU 与两个 Grove 口（J11/J12）**在同一条 I2C 总线上**：

- SDA = D4 = GPIO5，SCL = D5 = GPIO6
- 速率来自预设表的 `i2c_speed_hz`（如 `imu.raw.104`）
- 外接传感器时注意地址不要和 IMU（0x6A）冲突
- 想先看总线上都有谁，跑 [P-08 I2C 扫描](../examples/periph-index.md#p-08)

## 遇到问题先看这里

| 现象 | 先查 |
| --- | --- |
| 插上 USB 串口没出现 | 换线 / 按住 BOOT 再插（进下载模式） |
| IMU 读到 0 | 确认总线号是 0、D4/D5 没接反、跑 P-08 看总线有没有 0x6A |
| 电机不动 | 先试开环 PWM，再查 H 桥两路时序；确认没同时接 J4 和 J8 |
| 舵机抖动 / 复位 | 多舵机堵转电流过大，`Motor_5V` 轨带不动，减少同时动作的舵机数 |
| 灯带不亮 | D13 已缓冲到 5V，别绕过缓冲；灯带供电走 J7 的 5V |
| 加热例程不升温 | P-10 默认合成温度场景，需把 `P_SIM_HEAT` 改 0（真硬件档 HAL 待补） |
| 想接别的传感器 | 20 脚全满——只能走 I2C(J11/J12) 或 UART(J10)，或 TP20/TP21 飞线 |