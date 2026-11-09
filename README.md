<!-- SPDX-License-Identifier: MIT -->
# XIAO Robot Kit Vibe

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Vibe coding with XIAO Robot Kit!**

一个机器人套件，一个周末，一队 AI 子代理工作流。

一队 AI 把一套 ESP32-S3 小机器人套件（六轴 IMU 姿态、四类电机驱动、串口帧协议、
上位机示波器）从旧项目里审查、移植、验收、实验矩阵一路推到开源——审查员、复核员、
移植工程师、固件工程师、测试工程师、前端工程师，每个角色都是一张任务卡派出去的
子代理，人类只负责验收和拍板。

本仓是这场实验的**方法论蒸馏 + vibecoding 工作区**：5 份可以直接抄走的配方，
加上一个自举脚本——**clone 本仓一个，AI 替你把组织里其余的仓克隆齐、体检你
电脑缺什么、提示你怎么装**。本仓不存业务代码，能跑的代码都在它替你拉下来的
兄弟仓里。

## 30 秒起步（只 clone 这一个仓）

```bash
git clone https://github.com/xiao-robot-kit/xiao_robot_kit_vibe.git
cd xiao_robot_kit_vibe
python scripts/bootstrap.py --all
```

`bootstrap.py`（纯标准库，无第三方依赖）做两件事：

1. **依赖体检**——逐项探测 git / python / cmake / ninja / **ESP-IDF** /
   arduino-cli / esptool / **QEMU** / node，版本不够会给出按平台（Windows
   winget / macOS brew / Linux apt）的安装命令；缺必需项时明确告知，
   不让你到编译失败才发现。
2. **兄弟仓自举**——按 [`repos.json`](repos.json)（组织仓唯一机器清单）
   把 6 个仓克隆进 `./repos/`（浅克隆）；`--update` 快进已有克隆
   （本地有未提交改动会跳过并说明，不覆盖你的工作）；`--json` 给
   机器可读报告，`--strict` 把「必需项缺失」变成退出码 1，可当 CI 门禁。

```text
$ python scripts/bootstrap.py            # 只体检（不动任何东西）
$ python scripts/bootstrap.py --clone    # 补齐缺失的仓
$ python scripts/bootstrap.py --update   # 快进已克隆的仓
$ python scripts/bootstrap.py --json     # AI 消费机器报告
```

AI 用户直接对代理说「按 AGENTS.md 干活」即可——代理会自己跑 bootstrap、
读 docs 仓地图、再开始派活（见 [`AGENTS.md`](AGENTS.md)）。

## 组织架构：七层分治，一仓一职

整个组织按**七层分治**组织（coordination → presentation → interface →
core → shared + testing + docs），依赖单向向下，跨仓只走契约：

```text
                 ┌──────────────────────────────────────────┐
  coordination   │ vibe（本仓：方法论+工作区） · .github     │  派活、配方、组织面
                 └───────────────┬──────────────────────────┘
                                 │ 读文档、发任务卡
                 ┌───────────────▼──────────────────────────┐
  docs           │ xiao_robot_kit_docs                       │  事实源：硬件/例程/教程
                 └───────────────┬──────────────────────────┘
                                 │
   ┌─────────────────────────────┼─────────────────────────────┐
   │                             │                             │
presentation            interface + core + shared        testing
   │                     xiao_robot_kit_idf                     │
xiao_robot_kit_host     （八组件 C 核心 + 28 工程）    xiao_robot_kit_qemu
（可视化上位机）          xiao_robot_kit_arduino           （QEMU 虚拟板）
                         （同一颗核心的 Arduino 形态）
```

| 层 | 仓 | 职责 |
| --- | --- | --- |
| coordination | **vibe（本仓）** + `.github` | 工作流配方、自举工具、组织 profile |
| presentation | [xiao_robot_kit_host](https://github.com/xiao-robot-kit/xiao_robot_kit_host) | 可视化上位机：波形/姿态/电机/参数，sim 与真机两档 |
| interface | idf 仓 `examples/_shared/` + arduino 仓 `src/arduino/` | 平台胶水：I2C/flash/PWM 后端、Arduino 包装 |
| core | [xiao_robot_kit_idf](https://github.com/xiao-robot-kit/xiao_robot_kit_idf) / [xiao_robot_kit_arduino](https://github.com/xiao-robot-kit/xiao_robot_kit_arduino) | 八组件平台无关 C 核心（同一颗，两种发布形态） |
| shared | idf 仓 `src/proto/include/proto/frame.h` + 预设表 | 零依赖契约：帧格式、命名预设（`imu.raw.104`…） |
| testing | 各组件 `tests/` + [xiao_robot_kit_qemu](https://github.com/xiao-robot-kit/xiao_robot_kit_qemu) | 5,052 断言 / 11 套单测；无实物板的 QEMU 运行 |
| docs | [xiao_robot_kit_docs](https://github.com/xiao-robot-kit/xiao_robot_kit_docs) | 硬件介绍 + 例程索引 + 教程 + 踩坑 |

**跨仓契约只有三样**：串口帧格式（`frame.h` 单点定义）、命名预设表、引脚表
（docs 仓权威）。其余一律不跨界——所以换上位机不影响固件，换固件形态不影响
上位机。

## 这套软硬件能玩什么（速览）

**板载硬件（20 个 GPIO 全占用，一个外设一个例程）**：六轴 IMU（LSM6DS3TR-C）·
K7 按键 · WS2812 灯带 · 电池 ADC · 双 GC9112 直流电机 · 双编码器 · 四路舵机 ·
I2C 扩展口（J11/J12）· Grove 串口（J10）· IMU 恒温加热 · flash 参数区 ·
备用飞线 TP20/TP21。

**28 个可独立构建的 ESP-IDF 工程**：13 个外设例程（P-00~P-12，验收锚点齐全）+
5 级 IMU 链路（原始→标定→欧拉→四元数→轨迹）+ 8 个电机控制实验
（开环→编码器→PID 网格→S 曲线→嵌套定时器）+ 1 个断电持久化 + 1 个入门模板。

**软件三形态**：ESP-IDF 组件库 · Arduino 库（同一颗 C 核心，API 一致，切换
零成本）· QEMU 虚拟板（不买板也能跑固件看数据）。

逐器件的引脚、验收锚点、每个工程加了什么能力——**全在
[xiao_robot_kit_docs](https://github.com/xiao-robot-kit/xiao_robot_kit_docs)**
（人和 AI 读完就知道有什么、能用什么、怎么跑）。

## 本仓目录

```text
xiao_robot_kit_vibe/
├── AGENTS.md           ★ AI 运行规范：红线 / 七层映射 / 派活前必做 / 收口守则
├── repos.json          ★ 组织仓唯一机器清单（bootstrap 的输入）
├── scripts/
│   └── bootstrap.py    ★ 依赖体检 + 兄弟仓克隆/更新（纯标准库）
├── recipes/            ★ 5 份配方（多代理工作流方法论）
│   ├── workflow-review.md      域并行审查 + 逐条独立复核
│   ├── workflow-build.md       实现波 + 确定性验证门
│   ├── heartbeat-autopilot.md  无人值守心跳接力
│   ├── posix-c.md              C 接口纪律检查表
│   └── lessons.md              踩坑池（四段法）
├── repos/              （bootstrap 产物，gitignore——克隆的兄弟仓住这里）
└── projects/           （你的 vibe coding 产物区，gitignore）
```

本仓无业务代码、无 CI、无可执行交付物——`bootstrap.py` 是唯一脚本，
它自己也在这仓里被测过（doctor / clone / update / 幂等重跑）。

## 数字战报

| 战报 | 数字 | 口径 |
| --- | --- | --- |
| 工作流波次 | **12+** | 10 份具名波次脚本真迹 + 12 份在档运行日志 ¹ |
| 并行作战域 | **6** | 驱动/平台 · 算法库 · 固件组装 · 串口协议 · 上位机后端 · 上位机页面 ¹ |
| 断言与逐帧检查 | **≈15,000+ 全绿** | 两段万帧级全链逐帧断言就占 15,006 ² |
| QEMU 真仿真全链 | **esp32s3 固件 → 串口 → socket → 上位机** | 双实验联调 exit 0；发布当日复跑 12,999 帧 0 坏帧 ² |
| 四类电机驱动库 | **1,238 断言** | PWM 开环 / 舵机 / 编码器闭环 / 直流 H 桥 ³ |

细账（每个数字都标了口径，防战报注水）：

| 套件 / 链路 | 数字 | 状态 |
| --- | --- | --- |
| 标定组件单测 | 3,402 断言 | ✅ 当前版本复跑 0 fail ² |
| 电机实例单测（四类） | 1,022 断言 | ✅ 复跑 0 fail ² |
| 姿态融合组件单测 | 107 断言 | ✅ 复跑 0 fail ² |
| PWM 定时器单测 | 119 断言 | ✅ 复跑 0 fail ² |
| PID 单测（抗饱和） | 78 断言 | ✅ 复跑 0 fail ² |
| 参数持久化单测 | 153 断言 | ✅ 复跑 0 fail ² |
| IMU 驱动单测 | 29 断言 | ✅ 复跑 0 fail ² |
| 电池/SOC 单测 | 35 断言 | ✅ 复跑 0 fail ² |
| IMU 加热组件单测 | 40 断言 | ✅ 复跑 0 fail ² |
| 串口帧协议单测 | 48 断言 | ✅ 复跑 0 fail ² |
| S 梯度轨迹单测 | 全相位 PASS | ✅ 复跑 ² |
| **库单测合计** | **11 套 / 5,052 断言** | ✅ `ctest` 11/11 通过（实测 2.45 s）² |
| 上位机 socket 桥 | 37 断言 | ✅ 复跑 0 fail ² |
| 协议注入回归 | 100,000 帧 + 1% 比特错误注入，零静默污染 | ✅ 复跑 0 fail ² |
| QEMU 电机全链（DC 专项） | 13,007 帧，零错向帧 | 波次记录 ¹，发布当日复跑 12,999 帧 PASS ² |
| QEMU 四元数全链 | 1,999 帧，零丢帧，\|q\|≡1 | 波次记录 ¹ |
| 轨迹重建 | 320 帧，静止漂移 0.18 mm | ✅ 复跑 0 fail ² |

> 口径说明：
> ¹ = 项目波次记录（私有项目的内部工作台账与波次脚本不随本仓发布，数字抄录自
> 验收记录，指标对得上才上表）；
> ² = 本仓发布当日在私有源项目里真实复跑，exit 0（单测编译→运行、QEMU 链路
> 后台起→限时收→必杀，均为实际命令行输出，非口头汇报）；
> ³ = 与 [xiao_robot_kit_idf](https://github.com/xiao-robot-kit/xiao_robot_kit_idf) / [xiao_robot_kit_arduino](https://github.com/xiao-robot-kit/xiao_robot_kit_arduino) 开源组件库同一颗
> 电机核心的同一数字（motor 1,022 + pid 78 + pwm 119 + scurve 19 = 1,238）。
> ≈15,000 的算法：13,007 + 1,999 = 15,006 帧逐帧断言（两段万帧级全链）；再算上
> 单测断言与上位机套件，全量口径约 1.9 万——「15k+」是保守写法。

## 配方索引

| 配方 | 一句话 | 实战背书 |
| --- | --- | --- |
| [代码审查工作流](recipes/workflow-review.md) | 域并行只读审查，每条发现派独立复核员重读求证 | 两轮审查 59 条发现 59 条复核成立，violation=0 ¹ |
| [实现波](recipes/workflow-build.md) | 任务卡驱动 + 确定性验证门（不采信口头汇报）+ 一轮修复 | 电机实现波四门实跑全绿：119 / 78 / 1022 / S 梯度 ¹ |
| [心跳自动驾驶](recipes/heartbeat-autopilot.md) | 定时勘察：有活不打断，空闲自动开下一波 | 68 次心跳注入跨 14.4 小时挂机，接力 13 个完成波次 ¹ |
| [POSIX C 接口检查表](recipes/posix-c.md) | snake_case / 0=-1 / 指针校验 / 单位注释，逐条打勾 | 全部组件接口的统一形态 |
| [踩坑集](recipes/lessons.md) | 现象→根因→修复→预防；同类坑第二次出现 = 流程违规 | 4 条原始错误全部蒸馏入池，同型零复发 ¹ |

## 工作流全景

从旧项目到开源，五个阶段，每个阶段都是一串多代理工作流波次：

```text
  旧项目代码                     开源发布物
  ──────────  ──────────────────────────────────────────────────────  ──────────
                 ┌────────────┐     ┌────────────┐     ┌────────────┐
                 │  ① 审查波   │ ─▶ │ ② 移植/实现 │ ─▶ │  ③ 验收波   │
                 │ 域并行只读  │     │ 文件域拆分  │     │ 功能矩阵 +  │
                 │ 逐条独立复核│     │ 确定性验证门│     │ 测试套总跑  │
                 └────────────┘     └────────────┘     └────────────┘
                                            │                  │
                                            ▼                  ▼
                                     ┌────────────┐     ┌────────────┐
                                     │ ④ 实验矩阵  │ ─▶ │  ⑤ 开源化   │
                                     │ QEMU 真仿真 │     │ 组件蒸馏 +  │
                                     │ 万帧级联调  │     │ 配方提炼(本仓)│
                                     └────────────┘     └────────────┘
```

| 阶段 | 打法 | 实战产出 |
| --- | --- | --- |
| ① 审查波 | 六域并行只读审查 + 每条发现独立复核 | 59 条发现全部复核成立，violation=0，雷清单注入下一波 |
| ② 移植/实现波 | 文件域拆分并行子代理，波尾脚本实跑编译+单测当门 | 四类电机 1,022 断言、标定 3,402 断言等单测全绿 |
| ③ 验收波 | 双域功能矩阵（✅实测 / ⚠️仅编译 / ❌缺失）+ 全部测试套总跑 | 61 项功能矩阵 + 测试套全绿，缺口清单化转实验矩阵 |
| ④ 实验矩阵 | 单波单实验，QEMU esp32s3 真仿真全链逐帧断言 | 9 个实验接力完成，万帧级链路零坏帧 |
| ⑤ 开源化 | 组件库蒸馏脱敏 + 方法论配方提炼 | idf/arduino 组件库（11 套 / 5,052 断言）+ 本仓五配方 |

（每一格的打法，都在 [recipes/](recipes/) 里有对应配方。）

## 依赖需求（bootstrap 会逐项体检并给安装命令）

| 依赖 | 必需? | 用在哪 | 装法速记 |
| --- | --- | --- | --- |
| git ≥ 2.20 | ✅ | 克隆/更新所有仓 | winget / brew / apt |
| python ≥ 3.9 | ✅ | bootstrap + 上位机 | winget / brew / apt |
| cmake ≥ 3.16 | ✅ | ESP-IDF 构建（IDF 自带一份） | winget / brew / apt |
| **ESP-IDF ≥ 6.0** | ✅（烧固件） | 28 个 IDF 工程构建烧录 | [官方安装](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/)，每个新 shell 先 `export` |
| ninja ≥ 1.10 | 可选 | IDF 默认生成器 | winget / brew / apt |
| arduino-cli ≥ 1.0 | 可选 | Arduino 线路 | winget / brew / install.sh |
| esptool ≥ 4 | 可选 | 手动擦写 flash | `pip install esptool` |
| **QEMU（Espressif 版）** | 可选 | 无实物板跑固件 | [xiao_robot_kit_qemu](https://github.com/xiao-robot-kit/xiao_robot_kit_qemu) 的 `setup-qemu.ps1` 一键装 |
| node ≥ 18 | 可选 | 上位机页面测试 | winget / brew / apt |

## 使用方式

1. **vibe coding**（本仓的主场景）：clone 本仓 → `bootstrap.py --all` →
   对你的 AI 代理说「按 AGENTS.md 干活」→ 代理自己读 docs 仓地图、克隆缺的仓、
   按 [recipes/](recipes/) 里的配方派子代理波次；你验收拍板。产物落
   `projects/`。
2. **单配方套用**：每份配方自包含（模式名 / 适用场景 / 结构骨架 / 实战数据），
   把任务卡模板抄走、改成你的文件域和验证命令，就能派活；
3. **整条流水线组合**：审查波产出雷清单 → 注入实现波任务卡 → 确定性验证门收口 →
   心跳自动驾驶让整条链过夜自走；
4. **要能跑的机器人代码**：去 `repos/xiao_robot_kit_idf`（ESP-IDF 组件形态）
   或 `repos/xiao_robot_kit_arduino`（Arduino 库形态）——同一颗 C 核心
   （11 套 / 5,052 断言），API 一致，自由切换。

> 诚实声明：本仓无可执行交付物——`bootstrap.py` 是唯一脚本；战报表里每个
> 「✅ 复跑」都发生在私有源项目的真实命令行里（发布当日），口径见上文脚注。

## License

[MIT](LICENSE)——配方与叙事随便抄，抄走了就去造你自己的机器人。