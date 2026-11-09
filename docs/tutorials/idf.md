<!-- SPDX-License-Identifier: MIT -->
# ESP-IDF 手工档库教学（xiao_robot_kit_idf）

> 目标：在 30 分钟内，用 `xiao_robot_kit_idf` 库跑通第一个 IMU 流式示例。
> 同一颗 C 核心的 Arduino 形态见 [Arduino 教学](arduino.md)。

## 0. 你在用什么

`xiao_robot_kit_idf` 是一个 **ESP-IDF 组件库**（esp32s3），八个独立组件：

| 组件 | 头文件（`#include` 路径） | 干的事 | 对应例程 |
| --- | --- | --- | --- |
| `xiao_imu` | `imu/lsm6ds3.h`、`imu/imu_cfg.h` | LSM6DS3TR-C 驱动：探测 → 按预设配置 → 物理量采样 | P-01 |
| `xiao_attitude` | `att/mahony.h`、`att/quat.h` | 四元数 + Mahony 互补滤波 → roll/pitch/yaw | — |
| `xiao_motor` | `mtr/motor.h`、`mtr/pwm_timer.h`、`mtr/pid.h`、`mtr/scurve.h` | 电机实例（PWM 定时器 / PID / S 梯度轨迹） | P-05/06/07 |
| `xiao_pstore` | `pstore/pstore.h` | 参数持久化（项注册表 + 帧序列化 + CRC32） | P-11 |
| `xiao_battery` | `battery/battery.h` | 电池 ADC 换算 + OCV 曲线 → 剩余电量 | P-04 |
| `xiao_calibration` | `cal/imu_calib.h`、`cal/temp_comp.h` | IMU 零偏标定 + 温漂补偿（temperature compensation） | P-10 |
| `xiao_imu_heater` | `imu_heater/imu_heater.h` | 恒温控制状态机（滞回 + 超温保护 + 看门狗） | P-10 |
| `xiao_proto` | `proto/frame.h` | 串口帧编解码（SOF 0xA5 / LEN / TYPE / SEQ / PAYLOAD / CRC8） | 各例程遥测帧 |

零硬编码参数：所有可调项来自预设表（`imu.raw.104` 等），见各组件 `*_presets`。

**组件之间可以组合**：`xiao_calibration` 依赖 `xiao_imu`（类型头），
`xiao_imu_heater` 与 `xiao_calibration` 常一起用（恒温 + 温补）。
链式依赖由库的 CMake `target_link_libraries(... PUBLIC ...)` 自动传播，
你只需链接最上层那个。

## 1. 建立工程（两条路选一）

### 例程目录长什么样

`examples/` 下一共 **13 个独立工程**（P-00 ~ P-12 外设例程）：

```
examples/
├── _shared/                   平台胶水 + 仿真数据源（所有例程共用，不用改）
└── periph/                    13 个外设例程，覆盖板上每一个器件
    ├── P-00_hello_bringup/    上电自检
    ├── P-01_imu_lsm6ds3/      板载 IMU
    ├── P-02_button_k7/        D11 按键
    └── ...                    完整清单见「外设例程索引」
```

> `examples/_shared/` 在**根上**（不是 `periph/_shared/`）：13 个外设例程共用同一份
> 端口层，如 `imu_hal_i2c.c`、`pstore` 的 flash 后端、电机仿真 HAL。

**先看 [外设例程索引](../examples/periph-index.md)**——13 个例程按「你想干什么」
分组，每个都写明跑起来看到什么、改哪里。

**路 A：直接抄已验证工程（推荐第一次用）**

```bash
git clone https://github.com/xiao-robot-kit/xiao_robot_kit_idf
cd xiao_robot_kit_idf/examples/periph/P-01_imu_lsm6ds3
idf.py set-target esp32s3
idf.py build flash monitor      # 串口 115200,8N1
```

打开串口监视器应看到 CSV 流（`az≈±1g, gz≈0`）：

```
az=+0.976g gz=+0.2dps
az=+0.981g gz=-0.4dps
...
```

**路 B：挂进你自己的工程**

在项目 `CMakeLists.txt` 加一行（`EXTRA_COMPONENT_DIRS` 或 `add_subdirectory`）：

```cmake
set(EXTRA_COMPONENT_DIRS ${CMAKE_CURRENT_LIST_DIR}/xiao_robot_kit_idf)
```

然后 `main/CMakeLists.txt` 里链接你要用的组件
（库 CMake 约定：`REQUIRES` 无条件全列，不要只写一个；
组件目标用 `target_link_libraries` 链接，链式依赖自动传播）：

```cmake
idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES esp_driver_i2c esp_timer)

set(LIBS_ROOT ${CMAKE_CURRENT_LIST_DIR}/../path/to/xiao_robot_kit_idf)
add_subdirectory(${LIBS_ROOT} ${CMAKE_CURRENT_BINARY_DIR}/xiao_libs)
target_link_libraries(${COMPONENT_LIB} PUBLIC xiao_imu xiao_attitude)
```

头文件**带组件前缀**：链接 `xiao_imu` 后写 `#include "imu/lsm6ds3.h"`，
不是裸名 `#include "lsm6ds3.h"`。库内部布局是

```
src/<组件>/include/<前缀>/*.h      src/<组件>/src/*.c
```

CMake 链接后自动把 `src/<组件>/include` 加进 include 路径，`imu/` `att/` `mtr/`
`pstore/` `battery/` `cal/` `imu_heater/` `proto/` 这些前缀就是真实路径段。

> **Arduino 形态只有一处不同**：Arduino 库只有一个 include 根，所以三个简写前缀写全词
> ——`att/mahony.h` → `attitude/mahony.h`，`mtr/motor.h` → `motor/motor.h`，
> `cal/imu_calib.h` → `calibration/imu_calib.h`；其余前缀两边相同，`proto/` 不随
> Arduino 库发布。完整对照与「改库改哪里」见 [库结构说明](library-layout.md)。

## 2. 最小代码（抄 P-01 主循环）

```c
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "imu/lsm6ds3.h"    /* xiao_imu */
#include "imu/imu_cfg.h"
#include "port_i2c.h"         /* examples/_shared：填 imu_i2c_bus_t 函数指针表 */

void app_main(void)
{
    const imu_cfg_t *cfg = imu_cfg_find("imu.raw.104");  /* 预设，非魔法数字 */
    esp_port_i2c_init(cfg->i2c_speed_hz);

    lsm6ds3_t imu;
    lsm6ds3_init(&imu, &esp_port_i2c_bus);
    while (lsm6ds3_probe(&imu) != 0) vTaskDelay(pdMS_TO_TICKS(1000));
    lsm6ds3_configure(&imu, cfg);

    for (;;) {
        imu_sample_t s;                    /* 单位：g / dps */
        if (lsm6ds3_read(&imu, &s) == 0)
            printf("az=%+.3fg gz=%+.1fdps\n", s.az, s.gz);
        vTaskDelay(pdMS_TO_TICKS(cfg->sample_period_ms));
    }
}
```

## 3. 改行为 = 换预设（不是改代码）

| 想要的效果 | 换哪行 |
| --- | --- |
| 采样率更快/更慢 | `imu_cfg_find("imu.raw.104")` → 另一个预设（`.raw.208` 等，看 `imu_cfg_presets.c`） |
| 换 I2C 引脚 | `esp_port_i2c_init` 里的 SDA/SCL GPIO 常量 |
| 调 PI 增益 | 用 `xiao_motor` 时找 `motor_cfg_presets` 的 PID 预设 |

## 4. 单元测试（改动库本身时跑）

```bash
cd xiao_robot_kit_idf
cmake -S . -B build && cmake --build build
ctest --test-dir build --output-on-failure   # 11 套，5,052 断言（实测 2.45s）
```

分母是 8 个组件 + 3 个子模块套件（pid / pwm_timer / scurve 各自独立二进制）。
单个组件想单独跑：`ctest --test-dir build -R test_pstore -V`。

## 5. 常见坑

- `idf.py build` 首次会拉 IDF 依赖，慢是正常的。
- 烧不进 → 按住 BOOT 键再插 USB。
- 改了组件但没生效 → `idf.py fullclean` 再 build（增量缓存会骗你）。

下一步：逐片拆解外设例程 → [外设例程索引](../examples/periph-index.md)。