<!-- SPDX-License-Identifier: MIT -->
# attitude_print 逐片拆解（Arduino 姿态融合）

> `xiao_robot_kit_arduino/examples/attitude_print/attitude_print.ino`
> 第一个「算法」示例：LSM6DS3 → **Mahony 互补滤波** → roll/pitch/yaw 度数 CSV。

## 链路

```
LSM6DS3TR-C (g/dps) → mahony_update() → mahony_get_angles() → 度数 CSV
```

## 关键设计（这是教学重点）

**① 增益也走预设表（应用层）**

```c
static const att_preset_t k_att_presets[] = {
    { "att.print.teaching", 2.0f, 0.2f },   /* kp=2.0, ki=0.2 */
};
```

- `kp` 比例增益：越大收敛越快，太大会放大加速度噪声
- `ki` 积分增益：补偿陀螺零偏漂移（0 = 关闭）
- 改滤波手感 = 加预设条目，不是改代码。

**② dt 单源自 IMU 预设（单源无第二事实）**

```c
mahony_init(&s_mf, att->kp, att->ki, (float)s_period_ms / 1000.0f);
```

滤波节拍恒等于采样节拍（`imu.attitude.208` 的 sample_period_ms），
没有第二份 dt——少一个「两处漂移」的坑。

**③ 万向锁教学注记（代码注释里明说）**

ZYX 欧拉角在 pitch ±90° 处万向锁（yaw/roll 融合丢一个自由度）。
3D 应用请改 `mahony_get_quat()`（四元数无奇异）。

## 跑通判定

| 动作 | 期望 |
| --- | --- |
| 水平静置 | roll/pitch/yaw 稳定近 0° |
| 绕 Y 轴缓慢俯仰 | pitch 跟随摆动，**roll/yaw 基本不动**（单轴不串轴） |
| 快速晃动 | 三轴跟手，无发散（ki 正在补零偏） |

这就是姿态融合的验收标准：**单轴运动不串轴**。

## 想玩别的

| 想改 | 改哪里 |
| --- | --- |
| 更敢晃（kp 更高） | 预设表加档 `{ "att.print.agile", 4.0f, 0.1f }` |
| 关积分 | `ki = 0` |
| 3D 渲染用 | 改调 `mahony_get_quat()`（w,x,y,z, |q|≡1） |
| 无板验证 | 同一核心在 IDF 形态可 `cmake` + 单测覆盖 quat/mahony |