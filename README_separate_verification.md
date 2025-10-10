# 分别验证每个Adversarial Label功能使用说明

## 概述

现在 `run_single.py` 支持为每个adversarial label分别进行branch and bound验证。这个功能允许您：

- 为每个adversarial label创建独立的验证树
- 获得每个label的详细验证结果
- 更好地理解哪些specific labels是problematic的

## 使用方法

### 基本语法

```bash
python run_single.py <image_index> <eps> [verifier] [option] [approx] [timeout] [separate_labels]
```

### 参数说明

- `image_index`: 图像索引
- `eps`: epsilon值（扰动大小）
- `verifier`: 验证器类型 ("GR", "SA", "BnB")
- `option`: 模型选项 ("mnist01", "mnist03", "cifarbase", etc.)
- `approx`: 近似参数 (0 或其他值)
- `timeout`: 超时时间（秒）
- `separate_labels`: **新参数** - 1表示使用分别验证，0表示常规验证（默认）

### 示例用法

#### 1. 常规验证（原有功能）
```bash
python run_single.py 0 0.1 BnB mnist01 0 1000 0
```

#### 2. 分别验证每个adversarial label
```bash
python run_single.py 0 0.1 BnB mnist01 0 1000 1
```

## 输出格式

### 常规验证输出
```
Verification Result: VERIFIED
Time Taken: 12.34 seconds
Nodes Visited: 156
Lower Bound: 0.045
```

### 分别验证输出
```
=== Separate Verification Results for Image 0 ===
Epsilon: 0.1
--------------------------------------------------------------------------------
Adv Label  Status       Tree Size  Nodes    Lower Bound  Time    
--------------------------------------------------------------------------------
1          VERIFIED     15         23       0.120       
2          UNKNOWN      127        200      -0.030      
3          VERIFIED     8          12       0.450       
4          ADVERSARIAL  3          5        -0.150      
5          VERIFIED     31         47       0.080       
6          UNKNOWN      89         150      -0.010      
7          VERIFIED     12         18       0.330       
8          VERIFIED     6          9        0.670       
9          UNKNOWN      156        250      -0.020      
--------------------------------------------------------------------------------
Summary: 5 verified, 1 adversarial, 3 unknown
Total nodes visited: 520
Result: NOT ROBUST (found adversarial examples for 1 labels)
```

## 功能特点

### 1. 独立验证树
- 每个adversarial label都有自己的branch and bound树
- 每个验证过程完全独立
- 可以并行化处理不同的labels

### 2. 详细结果分析
- **Adv Label**: 对抗标签编号
- **Status**: 验证状态 (VERIFIED/ADVERSARIAL/UNKNOWN)
- **Tree Size**: BnB树的大小
- **Nodes**: 访问的节点数量
- **Lower Bound**: 计算得到的下界

### 3. 综合评估
- 统计各种状态的数量
- 总节点访问数
- 整体鲁棒性评估

## 适用场景

### 使用分别验证的情况：
- 需要详细了解每个adversarial label的鲁棒性
- 想要识别特定的problematic labels
- 研究不同labels的验证复杂度
- 需要并行化验证过程

### 使用常规验证的情况：
- 只需要整体的鲁棒性结果
- 计算资源有限
- 快速验证需求

## 技术实现

### 核心改进
1. **LPTransformer.compute_lb()**: 支持返回所有labels的详细bounds
2. **BnBBase.verify_all_labels_separately()**: 为每个label创建独立的验证过程
3. **run_single.py**: 新增separate_labels参数和相应的结果处理

### 向后兼容
- 所有原有功能保持不变
- 默认行为与之前完全相同
- 只有当明确指定separate_labels=1时才使用新功能

## 注意事项

1. **仅支持BnB验证器**: 分别验证功能目前仅在verifier="BnB"时可用
2. **计算开销**: 分别验证会增加总的计算时间，因为需要为每个label单独运行BnB
3. **内存使用**: 每个label都会创建独立的transformer和模型，可能增加内存使用
4. **并行化**: 当前实现是串行的，但架构支持未来的并行化改进

## 示例脚本

```bash
#!/bin/bash
# 测试不同epsilon值的分别验证
for eps in 0.05 0.1 0.15 0.2; do
    echo "Testing epsilon: $eps"
    python run_single.py 0 $eps BnB mnist01 0 300 1
    echo "------------------------"
done
```

这个功能为neural network verification提供了更细粒度的分析能力，帮助研究者更好地理解模型的鲁棒性特征。

