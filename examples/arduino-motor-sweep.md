<!-- SPDX-License-Identifier: MIT -->
# motor_sweep 逐片拆解（Arduino 电机三形态）

> `xiao_robot_kit_arduino/examples/motor_sweep/motor_sweep.ino`
> 一个 sketch 展示 `xiao_motor` 的三种消费方式：**开环 PWM、SG90 舵机、
> 直流 H 桥**。三槽顺序扫掠，各跑自己的腿（S 曲线 + 停顿）。

## 三种槽（从 `k_slots[]` 抄）

| 槽 | 预设 | 通道 | 引脚 | 运动 |
| --- | --- | --- | --- | --- |
| 0 开环 PWM | `pwm.motor.20k` + `motor.pwm.generic` | 0/1 | D0/D1 (GPIO1/2) | duty 0~1，S 形扫掠 |
| 1 舵机 | `pwm.servo.50` + `motor.servo.sg90` | 0/2 | D0/D1 | 135°↔45° 缓慢往复 |
| 2 直流 H 桥 | `pwm.motor.20k` + `motor.dc.generic` | 1/7/8 | D1/D8/D9 (GPIO2/7/8) | +50% ↔ −50% 正反转 |

**槽去重**：同名定时器预设只建一个实例，多槽共享定时器通道面
（`timer_get()` 按预设名去重）——这是 `xiao_motor` 的装机样板。

## 装配样板（三步,每个电机都一样）

```c
/* 1. 建 PWM 定时器（预设） */
pwm_timer_t *t = pwm_timer_create_preset(slot->timer_preset);
/* 2. 预设底版 → 填接线（timer/channel/pin） */
const motor_cfg_t *base = motor_cfg_find(slot->motor_preset);
motor_cfg_t cfg = *base;
cfg.timer = t;  cfg.channel = slot->channel;  /* + pin 绑定 */
/* 3. create 电机实例 */
motor_create(&cfg, ...);
```

要点：**平台表先注册**（`arduino_pwm_hal_install()` 在 setup 最前，
先于任何定时器创建）；非协议适配后每次 bind 前都要保证 HAL 已装。

## 跑通判定

| 槽 | 你应该看到（5~10 秒切换） |
| --- | --- |
| 0 | 电机转速「慢→快→慢」S 形扫掠（不是跳变） |
| 1 | 舵机臂 135°↔45° 缓慢水平摆（载波 50Hz） |
| 2 | 直流电机 +50% ↔ −50% 正反转交替 |

## 接线（默认接法，见 ino 头部注释）

- 开环/舵机槽：PWM 信号接 D0/D1
- H 桥槽：IN1=D8 (GPIO7)、IN2=D9 (GPIO8)，供电另接
- 换板只改 `pin_a/pin_b`（及槽表的 channel/pin）

## 教学点：为什么叫「零硬编码」

三个槽的**行为参数全在预设表**：载波频率（`pwm.motor.20k`=20kHz、
`pwm.servo.50`=50Hz）、PID 增益、S 曲线 jerk 限制——没有一处
`#define MOTOR_FREQ 20000`。要改成 30kHz：加一个预设条目，不动代码。

## 常见坑

- 舵机不动 → ESP32 Arduino core 需 ≥3.x（per-pin `analogWriteFrequency`）
- H 桥只朝一个方向 → 检查两路 IN 的逻辑是否互补
- 编码器闭环槽（`MOTOR_ENC_CLOSED`）→ 本示例没有，需要自己的
  正交解码 HAL（`motor_hal_t`），薄胶水不含它（故意不覆盖）