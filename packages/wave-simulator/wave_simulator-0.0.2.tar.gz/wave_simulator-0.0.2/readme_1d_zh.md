# 一维波仿真

## 非均匀介质中的波动方程

在非均匀介质中，波速 $c$ 不再是一个常数，而是位置的函数 $c(\mathbf{x})$。标准的波动方程中的 $c^2$ 项不能直接移到偏导数外面。

以一维波动方程为例，当波速 $c(x)$ 随位置变化时，方程通常写为：

$$\frac{\partial^2 A}{\partial t^2} = \frac{\partial}{\partial x} \left[ c^2(x) \frac{\partial A}{\partial x} \right]$$

有限差分形式

$$\frac{A_{i}^{j+1} - 2A_{i}^{j} + A_{i}^{j-1}}{\Delta t^2} = \frac{1}{\Delta x^2} \left[ \frac{c_{i+1}^2 + c_{i}^2}{2} (A_{i+1}^{j} - A_{i}^{j}) - \frac{c_{i}^2 + c_{i-1}^2}{2} (A_{i}^{j} - A_{i-1}^{j}) \right]$$

> 推导过程[参考](./wave_equation.md)

### 一阶导数近似 (First Derivative Approximation)

**微分方程形式:**
$$\frac{\partial}{\partial t} A(x, t) = u$$

**有限差分形式 (使用 $a_j^i$ 符号):**
$$\frac{a_j^{i+1} - a_j^{i-1}}{2\Delta t} \approx u$$

## 启动问题（Starting problem）

在仿真开始时，我们可以指定第一帧的波形，以及第一帧中各个质点的瞬时速度。但根据波动方程得到的递推公式需要两帧的数据才能启动。
我们用当前质点的速度（由初始值指定）和加速度（波动方程的右侧部分）估算质点在第二帧的位置。

## 边界条件

### 固定边界

最简单的边界条件，默认固定为 0

### 自由端边界 (Neumann Boundary Condition)

物理含义： 边界点的位移梯度（斜率）为零（例如，一根绳子的末端系在一个可以在杆上自由滑动的环上）。这模拟了波在反射时没有相位反转的情况。

我们利用一个**虚拟点** $u_{-1}^n$ 来满足 Neumann 条件：

Neumann 条件差分近似
$$\frac{\partial u}{\partial x} \Big|_{i=0} \approx \frac{u_1^n - u_{-1}^n}{2 \Delta x} = 0 \quad \Rightarrow \quad u_{-1}^n = u_1^n$$

将 $u_{-1}^n = u_1^n$ 代入 $i=0$ 处的内部更新公式：

### 一阶吸收边界条件（First-order ABC）

这个条件基于这样一个事实：在一个无限的 1 维空间中，在波速为 $c$ 的情况下，波只向一个方向传播（例如，在右边界处，波只向右传播）。

对于左边界 ($x=0$)

向左传播的波满足 $\left(\frac{\partial}{\partial t} - c \frac{\partial}{\partial x}\right) A = 0$。

因此，左边界的吸收边界条件为：
$$\frac{\partial A}{\partial t} - c \frac{\partial A}{\partial x} = 0 \quad \text{在 } x=0$$
差分形式

$$\frac{A_0^{n+1} - A_0^n}{\Delta t} - c \frac{A_1^n - A_0^n}{\Delta x} = 0$$

$$A_0^{n+1} = A_0^n + c \frac{\Delta t}{\Delta x} (A_1^n - A_0^n)$$

$$A_0^{n+1} = A_0^n + C (A_1^n - A_0^n)$$

$$A_0^{n+1} = (1 - C) A_0^n + C A_1^n$$
