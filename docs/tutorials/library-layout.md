<!-- SPDX-License-Identifier: MIT -->
# 库结构：`src/<组件>/include/<前缀>/` 到底怎么排

> 这一页回答三个问题：**头文件为什么带前缀**、**IDF 与 Arduino 的前缀为什么有一处不一样**、
> **想改库代码该改哪里**。看完你就不用猜 include 路径了。

## 1. 一份源码，两种发布形态

```
        C 核心（平台无关，MIT）
                 │
      ┌──────────┴───────────┐
      ▼                      ▼
ESP-IDF 组件库           Arduino 库
xiao_robot_kit_idf       xiao_robot_kit_arduino
（八组件 + tests）       （同一核心 + src/arduino 胶水）
```

两边的 `src/` 布局是**同一个形状**：

```
src/<组件>/
├── include/<前缀>/*.h     ← 公开头文件（include 根就是 include/）
└── src/*.c                ← 实现
```

CMake 把 `src/<组件>/include` 加进 include 路径，所以 `<前缀>/xxx.h` 是**真实路径段**，
不是别名。这就是为什么写 `#include "imu/lsm6ds3.h"` 而不是裸名 `lsm6ds3.h`。

> 例外：同一个 `include/<前缀>/` 目录**内部**的头文件互相引用仍写相对名
> （`lsm6ds3.h` 里 `#include "imu_cfg.h"`，两者同目录）。这是目录内互引，
> 不影响外部使用者的写法——**你的代码引用库时一律带前缀**。

> **为什么不用扁平 include**：同一颗核心要被 IDF 库、Arduino 库、组件仓、例程多处消费。
> 一旦某一处把 `imu/lsm6ds3.h` 改写成 `lsm6ds3.h`，那份副本就自成一套路径观，
> 后面每次改动都要在多处各翻译一遍——历史上有过这个阶段，多份副本各自演化成了多种布局。
> 现在只有一条规则：**include 路径就是仓内路径，谁都不许翻译**。

## 2. 八个组件与前缀（IDF 库）

| 组件（链接目标） | 头文件前缀 | 例 |
| --- | --- | --- |
| `xiao_imu` | `imu/` | `#include "imu/lsm6ds3.h"`、`"imu/imu_cfg.h"` |
| `xiao_attitude` | `att/` | `#include "att/mahony.h"`、`"att/quat.h"` |
| `xiao_motor` | `mtr/` | `#include "mtr/motor.h"`、`"mtr/pid.h"`、`"mtr/scurve.h"` |
| `xiao_pstore` | `pstore/` | `#include "pstore/pstore.h"` |
| `xiao_battery` | `battery/` | `#include "battery/battery.h"` |
| `xiao_calibration` | `cal/` | `#include "cal/imu_calib.h"`、`"cal/temp_comp.h"` |
| `xiao_imu_heater` | `imu_heater/` | `#include "imu_heater/imu_heater.h"` |
| `xiao_proto` | `proto/` | `#include "proto/frame.h"` |

## 3. Arduino 库的唯一差异：三个前缀写全词

Arduino 库只有一个 include 根（`src/`），没有「组件目录 + include 目录」两层，
所以三个非全词前缀在发布时被展开成全词：

| 组件 | IDF 库 | Arduino 库 |
| --- | --- | --- |
| IMU | `imu/lsm6ds3.h` | `imu/lsm6ds3.h`（相同） |
| 姿态 | `att/mahony.h` | **`attitude/mahony.h`** |
| 电机 | `mtr/motor.h` | **`motor/motor.h`** |
| 标定 | `cal/imu_calib.h` | **`calibration/imu_calib.h`** |
| 持久化 / 电池 / 加热 | `pstore/` `battery/` `imu_heater/` | 相同 |
| 协议帧 | `proto/frame.h` | **不随 Arduino 库发布**（Arduino 侧直接 `Serial` 打印） |

这是**唯一**允许的路径改写：`att/`→`attitude/`、`mtr/`→`motor/`、`cal/`→`calibration/`。
除此之外两边源码逐字相同——所以你从 IDF 例程抄代码到 sketch 时，只需要改这三个前缀。

## 4. 单元测试住在 `src/` 之外

```
xiao_robot_kit_idf/
├── src/<组件>/{include,src}     ← 库本体
└── tests/<组件>/test_*.c        ← 单元测试（每个文件自带 main()）
```

测试**不能**放进 `src/`：Arduino 会递归编译 `src/` 下所有 `.c`，测试的 `main()` 会和
sketch 的 `setup()/loop()` 打架。IDF 侧由根 `CMakeLists.txt` 各自注册成独立可执行文件。

```bash
cd xiao_robot_kit_idf
cmake -S . -B build && cmake --build build
ctest --test-dir build            # 11 套全部通过
```

## 5. 例程怎么分层

```
examples/
├── _shared/          平台胶水 + 仿真数据源（所有例程共用，改这里影响全部例程）
└── periph/           P-00 ~ P-12：每个外设一个工程（13 个）
```

每个 `periph/` 工程都从库根 `CMakeLists.txt` 取 `xiao_*` 目标，不复制组件源码，
也不引用另一个例程的构建产物。唯一共享的是 `examples/_shared/`。

## 6. 想改库代码，改哪里

| 你想改 | 改这个文件（源仓） | 之后 |
| --- | --- | --- |
| 驱动逻辑 / 新增 API | 组件 `src/*.c` + `include/<前缀>/*.h` | 两个发布形态都会跟着变 |
| 预设参数（采样率、量程、PID 增益） | 组件 `src/*_cfg_presets.c` | 无需改任何调用点 |
| Arduino 侧接线胶水 | Arduino 库 `src/arduino/`（**只此一处手写**） | 不影响 IDF |
| 例程行为 | `examples/<组>/<工程>/main/` | 各工程独立 |

公开仓里的组件源码与例程 `main/*.{c,h}` 是**发布产物**（由单向同步工具生成，
注入 SPDX 头并脱敏），不在这里手改——手改会在下一次同步时被覆盖，也会造成两形态漂移。
改代码请提到源仓；发现文档与代码不一致，直接开 issue。

## 7. 30 秒自查

```bash
# 头文件到底在哪
find src -name "lsm6ds3.h"          # → src/imu/include/imu/lsm6ds3.h

# 你的 include 写法对不对（IDF）
grep -rn '#include "lsm6ds3.h"' examples/    # 有输出 = 写错了

# Arduino 侧三前缀有没有写错
grep -rn '#include "att/\|#include "mtr/\|#include "cal/' examples/   # 有输出 = 该改全词
```