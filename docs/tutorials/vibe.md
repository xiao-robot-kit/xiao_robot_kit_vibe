<!-- SPDX-License-Identifier: MIT -->
# Vibe 工作区教学（xiao_robot_kit_vibe）

> 目标：学会用 `xiao_robot_kit_vibe` 仓库——它是 **vibecoding 工作区**，
> 不是文档。你负责拍板，AI 负责把活干完。
> 方法论文档本体在 [xiao_robot_kit_vibe](https://github.com/xiao-robot-kit/xiao_robot_kit_vibe)。

## 0. 什么时候用这个仓

| 你想 | 用这个 |
| --- | --- |
| 手写 C 代码（IDF / Arduino 各形态） | 手工档库（idf / arduino） |
| **让 AI 替你写**：新实验、新页面、新协议 | ⭐ vibe 工作区 |
| 查示例怎么用 | 本 `docs/` |

vibe 仓是「**AI 多代理工作流的方法论**」：一队子代理（审查员/实现工程师/
测试工程师/前端…）按你可拍板的节奏推进。它本身不含业务代码——
业务代码在两个手工档库。

## 0.5 工作区自举：只 clone vibe 一个仓（新能力）

选 vibe coding 的用户不需要手动 clone 各核心仓：

```bash
git clone https://github.com/xiao-robot-kit/xiao_robot_kit_vibe.git
cd xiao_robot_kit_vibe
python scripts/bootstrap.py --all
```

`bootstrap.py`（纯 Python 标准库）会：① 逐项体检你电脑的依赖（git/python/
cmake/ESP-IDF/arduino-cli…，缺什么就给按平台的安装命令）；② 按
`repos.json` 把组织里其余仓克隆进 `./repos/` 并可随时 `--update` 快进。

对 AI 代理只需说一句「**按 AGENTS.md 干活**」——vibe 仓的
[AGENTS.md](https://github.com/xiao-robot-kit/xiao_robot_kit_vibe/blob/main/AGENTS.md)
里写死了红线、仓库分工、派活前必做（先 bootstrap 体检、先读本 `docs/`
阅读地图）与收口守则。新项目产物落 `projects/`（不入库）。

## 1. 五份配方（从这开始读）

| 配方 | 一句话 | 什么时候抄 |
| --- | --- | --- |
| [workflow-review](https://github.com/xiao-robot-kit/xiao_robot_kit_vibe/blob/main/recipes/workflow-review.md) | 域并行只读审查，每条发现独立复核 | 拿到旧代码想先摸清家底 |
| [workflow-build](https://github.com/xiao-robot-kit/xiao_robot_kit_vibe/blob/main/recipes/workflow-build.md) | 任务卡驱动 + 确定性验证门（不信口头汇报） | 让 AI 实现一个功能 |
| [heartbeat-autopilot](https://github.com/xiao-robot-kit/xiao_robot_kit_vibe/blob/main/recipes/heartbeat-autopilot.md) | 定时勘察：有活不打断，空闲自动开下一波 | 大工程过夜自走 |
| [posix-c](https://github.com/xiao-robot-kit/xiao_robot_kit_vibe/blob/main/recipes/posix-c.md) | snake_case / 0=-1 / 指针校验 / 单位注释检查表 | 任何 C 代码接收入口 |
| [lessons](https://github.com/xiao-robot-kit/xiao_robot_kit_vibe/blob/main/recipes/lessons.md) | 现象→根因→修复→预防，同型错误二次=违规 | 踩坑后沉淀 |

## 2. 最小工作流（10 分钟上手）

**场景**：让 AI 把 `imu_raw` 改成 500ms 平均输出一次。

1. **读一下现状**（让 AI 先读手工档库 README + 目标 sketch，再动笔）：
   ```
   请先读 xiao_robot_kit_arduino 的 README 和 examples/imu_raw/imu_raw.ino，
   然后告诉我改动方案，先别改代码。
   ```
2. **验收定义写清楚**（确定性验证门——配方核心纪律）：
   ```
   改完请给出：① 改动 diff；② 语法检查 sh testing/arduino_stub/check_syntax.sh 输出；
   ③ 平均窗口实现的单元测试；④ 输出 CSV 格式不变。
   ```
3. **AI 交回后你验证**：跑 `check_syntax.sh` → 看 diff → 过。

**关键纪律（从配方里抄的）**：

- 不采信口头汇报——要求「能复现的命令 + 实际输出」
- 一个任务一张卡：文件域 / 验收 / 验证命令写死
- 遇到要改两个库（IDF+Arduino 同源）→ 让 AI 先改核心再双形态同步

## 3. 大小库自由切换（vibe 的核心用武之地）

手工档两个库是同一颗 C 核心。让 AI 干活时，先把目标形态说清楚：

| 目标形态 | 让 AI 用的库 |
| --- | --- |
| ESP-IDF 工程 | xiao_robot_kit_idf（CMake 形态） |
| Arduino IDE/CLI | xiao_robot_kit_arduino（library.properties 形态） |
| 核心算法改动（两形态同要） | 先改核心，再同步到另一个形态（两边的 `src/` 是同一份源码的两种发布形状；不要只改一边） |

切换零成本：API 一致，只有构建形态不同。**让 AI 写之前，先让它读一遍目标
库的 README 与 [库结构说明](library-layout.md)**——头文件前缀（`imu/` `att/`
`mtr/` vs Arduino 的 `attitude/` `motor/` `calibration/`）是它最容易写错的地方。

## 4. 和文档的分工

- **vibe 工作区（本仓）** = 派活的方法论 + 五配方（「怎么让 AI 干」）+ 文档载体
- **`docs/`** = 硬件/库/示例的用法（「这块板子和代码怎么用」）

给 AI 派涉及硬件的活时，把 docs 的
[硬件介绍](../hardware/board.md) 链接一并给它，避免它乱猜引脚。

## 5. 诚实边界（vibe 仓自我声明）

vibe 仓无 CI、无业务代码——唯一的可执行物是 `scripts/bootstrap.py`（发布前
在本机实测 doctor / clone / update / 幂等重跑全部通过）。数字战报中的
「✅ 复跑」发生在私有源项目的真实命令行（发布当日）。抄配方时照抄结构，
数字自己跑自己的。