# 舆情简报服务单元测试

本目录包含了舆情简报服务的单元测试，使用pytest框架编写。这些测试旨在验证系统在各种输入条件下的行为是否符合预期。

## 测试文件结构

- **test_briefing.py**: 主要测试文件，包含了针对generate_briefing函数的全面测试用例
- **test_core_functionality.py**: 补充测试文件，专注于核心功能的基本测试
- **conftest.py**: pytest配置文件，提供测试环境设置和共享fixtures

## 测试覆盖范围

测试用例覆盖了以下场景：

### 正常情况
- 成功生成舆情简报
- 使用本地mock数据进行测试
- 不同max_articles值的处理

### 异常情况
- 新闻API调用失败
- 未找到相关文章
- 摘要生成失败
- 无效的输入参数

### 边界情况
- max_articles的边界值处理
- 文章内容为空的处理
- 请求参数验证

## 运行测试

### 安装依赖

在运行测试前，请确保已安装所有必要的依赖：

```bash
pip install -r ../requirements.txt
```

### 运行所有测试

在unitest目录下执行以下命令运行所有测试：

```bash
cd /data/wangyihong/testProblem/unitest
pytest
```

### 运行特定测试

运行单个测试文件：

```bash
pytest test_briefing.py -v
```

运行特定测试用例：

```bash
pytest test_briefing.py::TestBriefingGeneration::test_successful_briefing_generation -v
```

### 运行慢速测试

某些测试被标记为"slow"，这些测试可能涉及更复杂的场景或模拟耗时操作。要运行这些测试，请使用以下命令：

```bash
pytest --run-slow
```

## 测试原理

测试主要使用Python的unittest.mock库来模拟外部依赖，如：

- 模拟新闻API的响应
- 模拟摘要生成模型的行为
- 模拟文件读取操作

这样可以在不依赖真实外部服务的情况下测试系统的核心逻辑。

## 添加新测试

要添加新的测试用例，请遵循以下步骤：

1. 在现有的测试文件中添加新的测试方法，或创建新的测试文件
2. 使用pytest的标记机制标记测试类型（如`@pytest.mark.slow`）
3. 使用conftest.py中定义的fixtures简化测试编写
4. 确保测试覆盖正常、异常和边界情况

## 测试报告

运行测试后，可以生成测试报告：

```bash
pytest --cov=../testmain --cov-report=html
```

这将生成HTML格式的测试覆盖率报告，保存在htmlcov目录中。