<!-- SPDX-License-Identifier: MIT -->
# XIAO Robot Kit Docs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

XIAO Robot Kit 的**使用方法文档**：这块板子是什么、三个库怎么用、每个示例
拿去怎么跑、跑起来看什么、换参数怎么改。**教学导向**——不是文件清单,
是「拿到手 30 分钟内跑通第一个示例」的路。

## 阅读地图（按你的角色选路）

| 你是谁 | 走这条路 | 预计时间 |
| --- | --- | --- |
| 第一次拿到套件 | [硬件介绍](hardware/board.md) → [跑通第一个示例](examples/first-run.md) | 15 min |
| 想逐个玩板上的外设 | [**外设例程索引**](examples/periph-index.md)（13 个例程） | — |
| 想让数据变准、环变稳 | [**深度实验索引**](examples/experiments-index.md)（14 个工程：标定 / 姿态 / 闭环 / 持久化） | — |
| 想看懂库的目录与头文件前缀 | [**库结构说明**](tutorials/library-layout.md) | 10 min |
| ESP-IDF 开发者 | [IDF 库教学](tutorials/idf.md) → [imu_quickstart 拆解](examples/idf-imu-quickstart.md) | 30 min |
| Arduino 用户 | [Arduino 库教学](tutorials/arduino.md) → [imu_raw 拆解](examples/arduino-imu-raw.md) | 30 min |
| 没有实物板 | [QEMU 仿真](https://github.com/xiao-robot-kit/xiao_robot_kit_qemu) → [串口协议](https://github.com/xiao-robot-kit/xiao_robot_kit_qemu/blob/main/docs/protocol-spec.md) | 20 min |
| 想用 AI 代写 | [Vibe 工作区教学](tutorials/vibe.md) → [大小库切换](https://github.com/xiao-robot-kit/xiao_robot_kit_vibe) | 10 min |
| 想可视化调试 | [上位机指南](https://github.com/xiao-robot-kit/xiao_robot_kit_host) | 10 min |

## 六仓总览

```
xiao-robot-kit（组织）
├── xiao_robot_kit_idf     手工档 IDF 库——八组件 C 核心 + 13 个外设例程 + 14 个深度实验
├── xiao_robot_kit_arduino 手工档 Arduino 库——同一颗 C 核心 + 三 sketch
├── xiao_robot_kit_vibe    vibecoding 自举工作区——只 clone 它一个，脚本自动拉齐其余仓 + 依赖体检；五配方
├── xiao_robot_kit_docs    ★ 本仓：硬件介绍 + 教程 + 示例用法
├── xiao_robot_kit_qemu    QEMU 虚拟板——无实物烧录调试
└── xiao_robot_kit_host    上位机——已支持示例的可视化交互调试
```

两个手工档库是**同一颗 C 核心**（MIT），API 一致，只有构建形态不同。切换成本为零。

## 目录

```
docs/
├── README.md               ★ 本文件（教学地图）
├── hardware/
│   ├── board.md            硬件介绍：XIAO ESP32-S3 + 全 20 脚引脚表 + 器件清单
│   ├── hardware-capability.md  ★ 硬件能力报告：每个 IO 能做什么/接口/电源/坑位（权威源）
│   └── periph-spec.md      外设例程规格：P-00~P-12 已发布 + P-13 深睡（规划）清单与逐项验收标准
├── tutorials/
│   ├── idf.md              ESP-IDF 手工档库教学（挂依赖 → 最小工程 → 跑示例）
│   ├── arduino.md          Arduino 手工档库教学（装库 → 选板 → 跑 sketch）
│   ├── library-layout.md   ★ 库结构：include 前缀怎么排、IDF 与 Arduino 的唯一差异、改库改哪里
│   └── vibe.md             vibecoding 工作区教学（让 AI 读配方 → 派活 → 验收）
└── examples/
    ├── periph-index.md     ★ 13 个外设例程索引（P-00~P-12，按「想干什么」分组）
    ├── experiments-index.md ★ 14 个深度实验索引（IMU 链路 / 电机控制 / 参数持久化）
    ├── first-run.md        第一次跑通：P-00 起步 / imu_quickstart
    ├── idf-imu-quickstart.md   imu_quickstart 逐片拆解（IDF）
    ├── arduino-imu-raw.md      imu_raw 逐片拆解（Arduino）
    ├── arduino-motor-sweep.md  motor_sweep 逐片拆解（Arduino 电机三形态）
    └── arduino-attitude-print.md  attitude_print 逐片拆解（姿态融合看什么）
```

## 板上能玩什么（13 个外设例程一览）

完整用法见 **[外设例程索引](examples/periph-index.md)**，这里只给一张地图：

| 板载资源 | 例程 |
| --- | --- |
| 工具链自检 | P-00 |
| 六轴 IMU（I2C） | P-01 |
| 用户按键 K7 | P-02 |
| WS2812 灯带 | P-03 |
| 电池电压 / 电量 | P-04 |
| 双路直流电机 | P-05 |
| 编码器测速闭环 | P-06 |
| 四路舵机 | P-07 |
| I2C 总线扩展 | P-08 |
| Grove 串口 | P-09 |
| IMU 恒温加热 | P-10 |
| 参数持久化 | P-11 |
| 备用引脚（飞线） | P-12 |

## 通用知识（所有教程共用）

- **引脚分配**：20 个 GPIO **全部占用**——IMU I2C = D4/D5；双电机 = D1/D2 + D19/D18；
  编码器 = D3/D14 + D17/D10；四舵机 = D15/D9/D0/D8；灯带 = D13；加热 = D12；
  按键 = D11；电池 ADC = D16；Grove 串口 = D6/D7；I2C 扩展 = J11/J12。
  唯一可飞线备用 = TP20/TP21。完整表见 [硬件介绍](hardware/board.md)。
- **串口帧协议** :IMU/姿态/电机遥测都走同一帧打包（SOF 0xA5 | LEN | TYPE |
  SEQ | PAYLOAD | CRC8）。上位机与 QEMU 都认这套帧。完整规范见
  [protocol-spec.md](https://github.com/xiao-robot-kit/xiao_robot_kit_qemu/blob/main/docs/protocol-spec.md)。
- **零硬编码参数**：库的一切可调项都来自命名预设表（`imu.raw.104`、
  `motor.servo.sg90`…）。改行为 = 换预设，不是改代码里的魔法数字。
- **头文件带组件前缀**：链接 `xiao_imu` 后写 `#include "imu/lsm6ds3.h"`（不是裸名
  `lsm6ds3.h`）。库布局 `src/<组件>/include/<前缀>/*.h` + `src/<组件>/src/*.c`，
  前缀（`imu/` `att/` `mtr/` `pstore/` `battery/` `cal/` `imu_heater/` `proto/`）
  就是真实路径段。
- **两种发布形态只有一处不同**：Arduino 库只有一个 include 根，所以三个简写前缀
  写全词——`att/`→`attitude/`、`mtr/`→`motor/`、`cal/`→`calibration/`；其余（`imu/`
  `pstore/` `battery/` `imu_heater/`）两边相同，`proto/` 不随 Arduino 库发布。
  细节与改库指南见 [库结构说明](tutorials/library-layout.md)。

## 内容守则（本仓自我约束）

- 每个教程都以「**能跑通的最小闭环**」收尾——跑完有可见现象、可验证。
- 不罗列文件清单；文件树只作为帮你定位的索引。
- 数字写实测值，截图占位不会冒充已测。

## License

[MIT](LICENSE) © XIAO Robot Kit Contributors