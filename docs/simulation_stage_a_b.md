# Stage A/B 仿真说明

## Stage A：纯数学局部集合

`configs/local_set/stage_a_baseline.yml` 给出候选接触点、足底法向、切向基、总法向载荷、单点法向载荷上限和候选摩擦参数。`DiscreteContactModel` 按

\[
\mathbf f_j=\lambda_j\mathbf n+\mathbf T\mathbf u_j,
\qquad
\|\mathbf u_j\|_2\leq\mu_j\lambda_j
\]

构造离散接触力，并用

\[
\mathbf w=\sum_j
\begin{bmatrix}[\mathbf r_j]_{\times}\\\mathbf I_3\end{bmatrix}\mathbf f_j
\]

映射到六维扳手 `[tau_x, tau_y, tau_z, f_x, f_y, f_z]`。`LocalWrenchSet` 提供：

- `contains(wrench)`：是否存在满足约束的逐点接触力见证；
- `support(direction)`：给定方向上的最大投影；
- `radial_capacity(working_wrench, direction)`：从工作点沿加载方向到边界的余量；
- `support_reduced(direction)`：解析消去切向力后的线性规划交叉验证。

固定 `normal_load_n` 只是一个条件截面。需要研究法向载荷变化时，应扫描多个配置得到集合族，不能把某一截面当成整机可实现集合。

## Stage B：简化 MuJoCo 数字实验台

`models/bench/single_foot_bench.xml` 是一个带自由基座的刚性足体，足底用四个离散球形接触几何近似，地面只用于生成仿真接触。`mujoco_io.bench` 读取 MuJoCo 的逐接触力，转换到世界坐标并汇总到足体原点；这是真值通道，不是压力阵列算法输入。

Stage B 先验证接触力提取、法向合力和接触扳手。下一步可在相同配置下加入受控外力/外力矩加载，并将每个时刻的法向点载荷送入 Stage A 成员检验。完整 X1、整机动力学和瞬时可行扳手集合放在后续阶段。
