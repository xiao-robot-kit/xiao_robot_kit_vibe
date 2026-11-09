<!-- SPDX-License-Identifier: MIT -->
# AGENTS.md — vibe 工作区运行规范

> 给在本仓里干活的 AI 代理（与人类协作者）的**运行时规范**。
> 你刚被 clone 进这个仓、或被派活到这里：先读完本文件再动手。

## 0. 本仓是什么（一句话）

**vibecoding 工作区 + 方法论配方仓**：用户只 clone 本仓，其余组织仓由
`scripts/bootstrap.py` 自动克隆/更新；本仓**不存任何业务代码**——能跑的
代码在 `repos/` 下的兄弟仓里（见 §2）。

## 1. 红线（违反任何一条 = 立即停手）

1. **本仓不长业务代码**。固件/上位机/库的改动一律去 `repos/<对应仓>/`
   里做（那是独立 git 仓，有自己的提交规范）；本仓只收：配方（`recipes/`）、
   工作区工具（`scripts/`、`repos.json`）、文档（`README.md`、本文件）。
2. **`repos/` 不入本仓版本库**（已在 `.gitignore`）。它是克隆产物——
   需要重建就重跑 bootstrap，**禁止**把兄弟仓内容复制进本仓提交。
3. **`repos.json` 是组织仓的唯一机器清单**。新仓/改名/改默认分支只改
   这个文件；**禁止**在任何文档或脚本里手写第二份仓清单。
4. **引导只走 `scripts/bootstrap.py`**。不要手写 `git clone` 命令教用户——
   让用户（或你代跑）`python scripts/bootstrap.py --all`。
5. **不声称「已克隆/已装/已更新」**，以 bootstrap 实际输出为准（汇报贴
   退出码与输出摘要）；`--strict` 可当门禁用。
6. `projects/` 是 AI/用户的实验产物区（已 gitignore）——vibe coding 生成的
   新项目放那里，**别提交进本仓**。

## 2. 仓库分工（架构事实源）

| 仓 | 职责 |
| --- | --- |
| **本仓** + `.github` | 工作区：自举工具、多代理配方、文档、组织 profile |
| `repos/xiao_robot_kit_idf` | ESP-IDF 固件库 + 28 例程（平台胶水在 `examples/_shared/`） |
| `repos/xiao_robot_kit_arduino` | 同一颗 C 核心的 Arduino 库形态（包装在 `src/arduino/`） |

跨仓只共享三样（各只在一处定义）：串口帧格式
（idf 仓 `frame.h`）、命名预设表（各仓 `*_cfg_presets.c`）、引脚表
（本仓 `docs/hardware/`）。动到这三样时，同 commit 同步引用方。

## 3. 派活前必做（AI 例行）

1. `python scripts/bootstrap.py`——体检 + 仓状态；缺必需项就按输出里的
   安装提示告知用户（缺 ESP-IDF 等不能自动装，须用户本人装）。
2. 读任务相关仓的 README + **文档阅读地图**（`docs/README.md`）
   ——「板子上有什么、例程能玩什么」以 `docs/` 为事实源，不凭记忆编。
3. 写代码的任务：先确认目标仓已克隆；没有就 `--clone`。
4. 数字（组件数/断言数/例程数）一律**现场数**（`ctest`、`ls`、bootstrap 输出），
   不从本仓战报表抄——战报表只记录历史口径。

## 4. 收口守则

- 改了兄弟仓 → 在**那个仓**里提交推送（遵守它的提交身份与规范），别在 vibe 提交。
- 本仓新配方 → `recipes/*.md` 自包含（模式名/适用场景/结构骨架/数据口径）+ SPDX MIT 头。
- 汇报格式：做了什么 / 证据（命令 + 输出摘要）/ 没验证什么（如实标注）。
- 工具坏/依赖缺：只报「根因 + 安装/恢复方案清单」，由用户拍板，不擅自换环境。

## 5. 五份配方是干什么的

`recipes/workflow-review.md`（域并行审查+独立复核）、`workflow-build.md`
（实现波+确定性验证门）、`heartbeat-autopilot.md`（无人值守接力）、
`posix-c.md`（C 接口纪律检查表）、`lessons.md`（踩坑池）。
派多代理活之前，把对应配方读一遍——它们是实战蒸馏，不是设想。