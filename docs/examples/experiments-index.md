<!-- SPDX-License-Identifier: MIT -->
# 深度实验索引（14 个工程）

13 个外设例程回答「这颗器件能不能动」；这一页的 14 个工程回答「动起来之后，
数据准不准、环稳不稳、参数丢不丢」。每条链路都是**可构建、可观测、参数零写死**的
独立 IDF 工程，构建后从串口（或 UART0）能看到明确的帧流。

**14 个工程的构成**：IMU 链路 5（`examples/imu`）+ 电机控制 8（`examples/motor`）
+ 参数持久化 1（`examples/store_demo`）。对外共 **28 个可独立构建的工程**
= 13 外设例程 + 14 深度实验 + 1 入门模板（`examples/idf/imu_quickstart`）。
串口帧类型（`0x01` IMU_SAMPLE / `0x02` IMU_CAL / `0x03` EULER / `0x04` QUAT /
`0x05` MOTOR / `0x7D` CMD / `0x7E` ACK / `0x7F` TEXT）定义在帧契约头文件里。

> 源码位置：`xiao_robot_kit_idf/examples/{imu,motor,store_demo}/`
> 每个工程目录下有 `README.md`（意图 / 帧契约 / 数据源宏 / 构建运行）与
> `run.bat`（构建+烧录+监视）、`run_qemu.bat`（只构建 SIM 变体）。
> 想先看外设能不能动，回 [外设例程索引](periph-index.md)。

## 怎么用这一页

1. **按「回答什么问题」挑工程**——同一组里的工程变量只有一处，便于对照。
2. 所有工程共用一条**字节级帧契约**：布局单源是仓内 `src/proto/include/proto/frame.h`，
   上位机解析必须与它一致（不是某个文档的副本）。
3. 想知道板子引脚与电源，查 [硬件介绍](../hardware/board.md) /
   [硬件能力报告](../hardware/hardware-capability.md)。

## IMU 链路（examples/imu）

从裸数据一路走到姿态与轨迹数据源，五个工程逐级叠加能力，**每一步只加一件事**：

| 工程 | 回答什么问题 | 输出 | 涉及组件 |
| --- | --- | --- | --- |
| `exp1_raw` | 传感器原始读数长什么样 | `0x01` IMU 帧（6×float32：ax,ay,az,gx,gy,gz） | `xiao_imu`、`xiao_proto` |
| `exp2_calib` | 零偏怎么去掉、温漂怎么补 | `0x02` 标定帧 + TEXT 进度，参数跨重启保持 | `xiao_imu`、`xiao_calibration`、`xiao_pstore` |
| `exp3_euler` | 姿态用欧拉角表示 | `0x03` 欧拉帧（roll,pitch,yaw 弧度，ZYX） | `xiao_attitude`、`xiao_calibration`、`xiao_imu` |
| `exp4_quat` | 姿态用四元数表示（同一滤波器，唯一变量是表示法） | `0x04` 四元数帧（w,x,y,z） | 同 exp3 |
| `exp5_trajectory` | 位移重建需要什么数据 | `0x04` + `0x01` 双流（姿态 + 原始比力）+ 段标记 | 同 exp3 + 轨迹场景源 |

`examples/imu/common/` 是四个姿态实验共用的**标定命令会话**（`CAL` 行命令 →
重标定 → TEXT 进度 → `0x02` 打包）。TEXT 行格式必须字节一致，所以它只有一份实现，
四份副本必然漂移。

## 电机控制（examples/motor）

同一个 `xiao_motor` 内核（500 Hz 控制环 + 预设表），八个工程各验证一种控制面：

| 工程 | 验证什么 | 场景 |
| --- | --- | --- |
| `exp_motor_qemu` | 四类电机（开环/舵机/编码器闭环/DC）共存 + 运行期场景切换 | 上电即跑四槽演示，UART0 收 `SCEN <n>` 切五种场景（`0x06` 帧） |
| `exp_motor_pwm` | 开环占空 → 转速的单调性与死区 | 0/25/50/75/100 % 五档阶梯，每档 2 s |
| `exp_motor_dc` | H 桥方向位与带符号占空 | +50 % ↔ −50 % 各 2 s |
| `exp_motor_servo` | 舵机角度线性度与回程迟滞 | 0/45/90/135/180° 升后降，每点 2 s |
| `exp_motor_enc` | 速度环阶跃响应 | 30 → 90 rpm 交替，每段 4 s |
| `exp_motor_nested` | 嵌套定时器的通道隔离 | A/B 共享 20 kHz 定时器（A 动 B 静）+ C 独立 50 Hz 舵机 |
| `exp_motor_pidscan` | PID 参数网格的量化对比 | `kp × ki` 3×3 = 9 组，各跑一次阶跃，轮末 TEXT 输出收敛时间/超调/稳态误差与最优组 |
| `exp_motor_scurve` | 七相位 S 曲线的形状与到点精度 | 双槽各跑一条点位轨迹，逐相位判形 |

## 参数持久化（examples/store_demo）

| 工程 | 回答什么问题 | 要点 |
| --- | --- | --- |
| `store_demo` | 参数能不能跨掉电活下来 | flash **裸分区**后端（`partitions.csv` 自定义 `store` 分区，不经 NVS 中间层）；`boot_count` 开机 +1 落盘；运行期经 `0x7D` CMD / `0x7E` ACK 下发 `GET`/`STATUS`/`SET` 三条命令 |

## 构建与变体

所有工程都是独立 IDF 工程，进目录构建即可：

```bash
cd examples/motor/exp_motor_dc
idf.py build                    # 真板档
idf.py -DEXP_SIM=0 build        # 切真实硬件源（仅 imu 系与部分 periph 提供）
run.bat COM5                    # Windows：构建 + 烧录 + 串口监视
run_qemu.bat                    # Windows：只构建 SIM 变体（-DEXP_SIM=1 -DEXP_QEMU_UART=1）
```

两个变体宏的正交关系：

| 宏 | 1 | 0 |
| --- | --- | --- |
| `EXP_SIM` | 合成数据源（无传感器/电机也能跑通全链） | 真实硬件源；**硬件 HAL 未随本仓发布的工程（电机系、存储系）在编译期显式拒绝 0**，而不是悄悄编出一个「假硬件」固件 |
| `EXP_QEMU_UART` | 帧出口 = UART0（可接 QEMU / 串口自动联调） | 帧出口 = USB-Serial-JTAG（真板档） |

`periph/` 系列用的是更早的 `P_SIM_*` 命名表达同一件事，见各工程 README。

## 验证边界（如实说明）

| 项 | 状态 |
| --- | --- |
| 工程配置 | **28/28 `idf.py reconfigure` 通过**（14 深度实验 + 13 外设例程 + imu_quickstart，ESP-IDF v6.1 / esp32s3） |
| 深度实验全量构建 | **已实证 2 例新构建**：`imu/exp1_raw`（`exp1_raw.bin` 199,136 B）、`store_demo`（`store_demo.bin` 195,200 B），均 `Project build complete`；其余 12 例同模板但未在本次发布窗口逐个 build（改库/改模板后请自行重跑） |
| 外设例程全量构建 | **已实证 4 例**：P-00（167,696 B）、P-01、P-05（190,224 B）、P-11（`p11_pstore_params.bin`）；其余 9 例为 configure 层通过 |
| 合成数据源链路 | 可在无硬件条件下编出并烧进 QEMU 运行 |
| 真板电气行为 | **逐项实测未在发布前完成**——各工程 README 的「现象」是设计意图与判读契约，需按上表命令自行复核 |
| 电机 / 存储系真实 HAL | 未发布（`EXP_SIM=0` 编译期拒绝），因此这些工程的真实硬件档不构成本仓的可用路径 |

> 构建数字均为本次复核实测输出（Windows + ESP-IDF v6.1）。全量构建需注意：同一仓
> 的 `idf.py build` 与 `idf.py reconfigure` **不要并发**（共享 `build/` 下的 sdkconfig.h、
> CMakeCache、.ninja_log），否则会得到看起来像源码错误的假失败。