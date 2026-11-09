<!-- SPDX-License-Identifier: MIT -->
# Arduino 手工档库教学（xiao_robot_kit_arduino）

> 目标：在 30 分钟内，用 `xiao_robot_kit_arduino` 库跑通第一个 sketch。
> 同一颗 C 核心的 IDF 形态见 [IDF 教学](idf.md)。

## 0. 你在用什么

`xiao_robot_kit_arduino` 是一个**标准 Arduino 库**（有 `library.properties`），
自包含同一颗 C 核心 + 一层薄 Arduino 胶水（`src/arduino/`：Wire I2C + PWM）。

- 装好后在 Arduino IDE 里 **想用时零配置**：`#include "imu/lsm6ds3.h"` 即可。
- 三个现成 sketch 都输出 **CSV**，打开 Serial Plotter 直接看波形。

## 1. 安装

> ⚠️ 目前本库**尚未收录进 Arduino Library Manager**（提交还在排期），所以下面「方式 A」
> 暂不可用——请直接用「方式 B」手动安装。收录后本节会改成两种并列。

**方式 A（待收录后可用）：Arduino IDE → 库管理器**

1. `工具 → 管理库...`，搜索 **"XIAO Robot Kit"** → 安装。
2. `工具 → 开发板 → 开发板管理器`，装 **esp32 by Espressif**（≥3.x，舵机
   兼容需要）。
3. 开发板选 **XIAO ESP32S3**。

**方式 B（现在就能用）：手动克隆**

```bash
git clone https://github.com/xiao-robot-kit/xiao_robot_kit_arduino
# 放到 ~/Documents/Arduino/libraries/xiao_robot_kit_arduino 下
# （Windows 是 文档\Arduino\libraries\；目录名必须与 library.properties 的 name 可区分）
```

装完重启 Arduino IDE：`文件 → 示例 → XIAO Robot Kit Libraries` 下应能看到三个 sketch。
仍是空的 → 目录层级错了（必须是 `libraries/xiao_robot_kit_arduino/library.properties`）。

## 2. 跑第一个 sketch

1. `文件 → 示例 → XIAO Robot Kit → imu_raw`
2. 选板 XIAO ESP32S3 → 选串口 → 上传
3. 打开 **Serial Plotter**（115200），水平静置板子：

   - AZ 一条线≈+1g（重力），AX/AY≈0
   - GX/GY/GZ≈0（静止无转动）
   - 手拿起板子晃一晃 → 三条线实时跟手

这就是「**能跑通的第一个示例**」的最小闭环。

## 2.5 头文件前缀：Arduino 与 IDF 的唯一差别

Arduino 库只有一个 include 根（`src/`），所以三个简写前缀在这里写成全词：

| 组件 | IDF 写法 | Arduino 写法 |
| --- | --- | --- |
| IMU | `imu/lsm6ds3.h` | `imu/lsm6ds3.h`（相同） |
| 姿态 | `att/mahony.h` | **`attitude/mahony.h`** |
| 电机 | `mtr/motor.h` | **`motor/motor.h`** |
| 标定 | `cal/imu_calib.h` | **`calibration/imu_calib.h`** |
| 持久化 / 电池 / 加热 | `pstore/` `battery/` `imu_heater/` | 相同 |
| 协议帧 | `proto/frame.h` | 不随 Arduino 库发布 |

从 IDF 例程抄代码到 sketch，只需改这三个前缀；其余逐字相同。
链式依赖已经由 Arduino 的构建展开处理好，你只需 include 你要用的那个头。
细节见 [库结构说明](library-layout.md)。

## 3. 三个示例分别看什么

| Sketch | 现象（跑通 = 看见这个） | 涉及组件 |
| --- | --- | --- |
| [imu_raw](../examples/arduino-imu-raw.md) | 六轴 CSV，静置 az≈+1g，晃动跟手 | xiao_imu |
| [motor_sweep](../examples/arduino-motor-sweep.md) | 三个电机槽顺序动：开环 PWM → 舵机 → H 桥 | xiao_motor |
| [attitude_print](../examples/arduino-attitude-print.md) | roll/pitch/yaw 度数，单轴倾斜不串扰 | xiao_attitude + xiao_imu |

每个拆解文档里都有「跑通判定」——不知道期望现象就跑是盲调。

## 4. 换成你自己的电机/接线

`motor_sweep.ino` 头部注释就是改装甲板的地方：

```cpp
static const int pin_a = 1;   /* D0  GPIO1 */
static const int pin_b = 2;   /* D1  GPIO2 */
/* D8=7 D9=8 是 H 桥路；D4/D5=I2C，D6/D7=串口，避开 */
```

换预设（零硬编码参数）→ 找 `imu_cfg_presets.c` / `motor_cfg_presets.c` 里
的命名表。

## 5. 常见坑

- 库管理器搜不到 "XIAO Robot Kit" → 正常，尚未收录（见第 1 节）；先用手动安装。
- 示例菜单下一个 sketch 都没有 → `libraries/` 层级不对，见第 1 节末尾。
- `att/mahony.h: No such file` → 把 IDF 写法直接抄过来了，Arduino 里是 `attitude/mahony.h`。
- 舵机不动 → Arduino core 需 ≥3.x（per-pin `analogWriteFrequency`）。
- 烧录失败 → 按住 BOOT 再插线。
- 想无板验证语法 → 本仓库自带 stub 检查（自带假 `Arduino.h`/`Wire.h`）：

```bash
sh testing/arduino_stub/check_syntax.sh   # 6 项 PASS：2 个胶水×2 核 + 3 个 sketch
```

## 6. 深入

- 逐片拆解：[imu_raw 拆解](../examples/arduino-imu-raw.md)（第一个示例）
- 电机强度示范：[motor_sweep 拆解](../examples/arduino-motor-sweep.md)
- 姿态融合：[attitude_print 拆解](../examples/arduino-attitude-print.md)