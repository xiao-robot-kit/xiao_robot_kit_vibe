<!-- SPDX-License-Identifier: MIT -->
# imu_quickstart 逐片拆解（IDF 第一个示例）

> `xiao_robot_kit_idf/examples/idf/imu_quickstart/`
> 这是 IDF 形态的最小完整链路：**IMU → 驱动换算 → 串口流**，
> 也是「把库挂进自己工程」的参照物（CMake 模式照抄）。

## 工程骨架

```
imu_quickstart/
├── CMakeLists.txt        # 工程级：EXTRA_COMPONENT_DIRS 挂库（或 add_subdirectory）
├── sdkconfig.defaults    # IDF 配置基线
└── main/
    ├── CMakeLists.txt    # REQUIRES xiao_imu（要啥列啥）
    ├── bus_i2c_idf.c/.h  # 你的胶水：填 imu_i2c_bus_t（IDF I2C 驱动 → 函数指针表）
    └── main.c            # probe → configure → stream
```

## 三件关键事

**① 库怎么挂进工程（CMake 样板）**

库作为 ESP-IDF 组件（`idf_component.yml` + `CMakeLists.txt`），两种挂法：
- `EXTRA_COMPONENT_DIRS` 指向本仓（推荐：不动 IDF 全局）
- 或 `add_subdirectory` 后 `target_link_libraries(app PRIVATE xiao_imu)`

`main/CMakeLists.txt`：
```cmake
idf_component_register(
    SRCS "main.c" "bus_i2c_idf.c"
    INCLUDE_DIRS "."
    REQUIRES xiao_imu)
```

**② 胶水只做一件事（I2C 操作表）**

核心驱动需要 `imu_i2c_bus_t`（函数指针表），IDF 侧由
`bus_i2c_idf.c` 填充：

| 表字段 | IDF 实现 |
| --- | --- |
| `.i2c_port` | `I2C_NUM_0` |
| `.sda_io_num` | `GPIO5`（D4） |
| `.scl_io_num` | `GPIO6`（D5） |
| `.scl_speed_hz` | `cfg->i2c_speed_hz`（预设源） |

**③ 主循环（20 行）**

```c
const imu_cfg_t *cfg = imu_cfg_find("imu.raw.104");
if (!cfg || bus_i2c_init(cfg->i2c_speed_hz) != 0) { puts("FATAL bus init"); return; }

lsm6ds3_t imu;  lsm6ds3_init(&imu, &bus_i2c);
while (lsm6ds3_probe(&imu) != 0) {          /* 每秒重试，打印明确错误 */
    puts("IMU not found @0x6A, retrying in 1s ...");
    vTaskDelay(pdMS_TO_TICKS(1000));
}
lsm6ds3_configure(&imu, cfg);

for (;;) {
    imu_sample_t s;                          /* g / dps */
    if (lsm6ds3_read(&imu, &s) == 0)
        printf("ax=%+.3f ay=%+.3f az=%+.3f g | gx=%+.1f gy=%+.1f gz=%+.1f dps\n", ...);
    vTaskDelay(pdMS_TO_TICKS(cfg->sample_period_ms));
}
```

## 跑通判定

| 现象 | 输入 |
| --- | --- |
| `streaming: 104 Hz, +-4 g, +-2000 dps` | 触发的配置打印（预设值） |
| `ax=+0.976 ay=+0.001 az=+0.981 g` | 水平静置：az≈±1g |
| `gx=+0.2 gy=-0.4 gz=+0.1 dps` | 静止三轴陀螺≈0 |

## 拿它当模板做自己的工程

1. `cp -r imu_quickstart my_app`
2. 改 `main.c`：加你的业务（比如接 `xiao_attitude` → `REQUIRES xiao_imu xiao_attitude`）
3. 跑 `idf.py set-target esp32s3 && idf.py build flash monitor`

## 无板子也能编译验证

```bash
# 在库根（不是示例内）跑核心单测
cd xiao_robot_kit_idf && cmake -S . -B build && cmake --build build
ctest --test-dir build         # 11 套全部通过（实测 2.45 s）
```