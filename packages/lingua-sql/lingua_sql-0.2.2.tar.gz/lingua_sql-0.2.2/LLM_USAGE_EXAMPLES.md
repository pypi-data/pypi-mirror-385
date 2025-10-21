# LinguaSQL 大模型使用示例

本文档展示如何使用 LinguaSQL 支持的各种国内大模型。

## 支持的大模型

### 1. DeepSeek (深度求索)
- **模型**: `deepseek-chat`, `deepseek-coder`
- **API密钥**: `DEEPSEEK_API_KEY`
- **特点**: 代码生成能力强，适合SQL生成

### 2. 通义千问 (Qwen)
- **模型**: `qwen-turbo`, `qwen-plus`, `qwen-max`, `qwen-long`
- **API密钥**: `QWEN_API_KEY`
- **特点**: 阿里云出品，中文理解能力强

### 3. 文心一言 (ERNIE)
- **模型**: `ernie-bot`, `ernie-bot-turbo`, `ernie-bot-4`
- **API密钥**: `ERNIE_API_KEY`
- **特点**: 百度出品，知识图谱丰富

### 4. 智谱AI (GLM)
- **模型**: `glm-4`, `glm-4-flash`, `glm-3-turbo`
- **API密钥**: `GLM_API_KEY`
- **特点**: 清华大学出品，逻辑推理能力强

### 5. 月之暗面 (Moonshot)
- **模型**: `moonshot-v1-8k`, `moonshot-v1-32k`, `moonshot-v1-128k`
- **API密钥**: `MOONSHOT_API_KEY`
- **特点**: 长文本处理能力强

### 6. 零一万物 (Yi)
- **模型**: `yi-34b-chat`, `yi-6b-chat`
- **API密钥**: `YI_API_KEY`
- **特点**: 李开复团队出品，多语言支持

## 使用方法

### 方法1: 环境变量配置

```bash
# 设置API密钥
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export QWEN_API_KEY="your_qwen_api_key"
export ERNIE_API_KEY="your_ernie_api_key"
export GLM_API_KEY="your_glm_api_key"
export MOONSHOT_API_KEY="your_moonshot_api_key"
export YI_API_KEY="your_yi_api_key"

# 设置模型（可选，会根据API密钥自动选择）
export LINGUA_SQL_MODEL="qwen-turbo"
```

```python
from lingua_sql import LinguaSQL
from lingua_sql.config import LinguaSQLConfig

# 自动从环境变量读取配置
nl = LinguaSQL()
```

### 方法2: 代码配置

```python
from lingua_sql import LinguaSQL
from lingua_sql.config import LinguaSQLConfig, APIConfig, DatabaseConfig

# 使用通义千问
config = LinguaSQLConfig(
    api=APIConfig(
        api_key="your_qwen_api_key",
        model="qwen-turbo"
    ),
    database=DatabaseConfig(
        type="mysql",
        host="localhost",
        port=3306,
        user="root",
        password="password",
        database="test_db"
    )
)

nl = LinguaSQL(config=config)
```

### 方法3: 字典配置（兼容旧版本）

```python
from lingua_sql import LinguaSQL

# 使用智谱AI
config = {
    "api_key": "your_glm_api_key",
    "model": "glm-4",
    "database": {
        "type": "mysql",
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "password",
        "database": "test_db"
    }
}

nl = LinguaSQL(config=config)
```

## 使用示例

### 基本使用

```python
# 初始化
nl = LinguaSQL()

# 训练数据
nl.train(
    question="查询所有用户的姓名和年龄",
    sql="SELECT name, age FROM users"
)

# 生成SQL
sql = nl.generate_sql("查询年龄大于25的用户")
print(sql)

# 执行查询
result = nl.ask("查询年龄大于25的用户")
print(result)
```

### 智能训练

```python
# 启用智能训练
config = LinguaSQLConfig(
    api=APIConfig(
        api_key="your_api_key",
        model="qwen-turbo"
    ),
    intelligent_training=IntelligentTrainingConfig(
        enabled=True,
        max_questions_per_table=10,
        auto_execute_training=True
    )
)

nl = LinguaSQL(config=config)

# 自动训练
nl.intelligent_auto_train()
```

### 字段和表名提取

```python
# 提取字段名
fields = nl.extract_field_names(
    question="查询用户的姓名和邮箱",
    available_fields=["user_name", "email", "phone", "address"]
)
print(fields)  # ['user_name', 'email']

# 提取表名
tables = nl.extract_table_names(
    question="查询用户表和订单表的关联数据",
    available_tables=["users", "orders", "products"]
)
print(tables)  # ['users', 'orders']

# 分析问题意图
intent = nl.analyze_question_intent("统计每个部门的平均工资")
print(intent)
```

## 模型选择建议

### 根据任务类型选择

- **SQL生成**: DeepSeek, Qwen, GLM
- **中文理解**: Qwen, ERNIE
- **长文本处理**: Moonshot
- **代码生成**: DeepSeek, Yi
- **知识问答**: ERNIE, GLM

### 根据性能需求选择

- **速度优先**: `qwen-turbo`, `glm-4-flash`, `moonshot-v1-8k`
- **质量优先**: `qwen-max`, `glm-4`, `moonshot-v1-128k`
- **平衡选择**: `qwen-plus`, `glm-3-turbo`, `yi-34b-chat`

## 注意事项

1. **API密钥安全**: 不要在代码中硬编码API密钥，使用环境变量
2. **模型兼容性**: 不同模型的API格式可能略有差异，系统会自动处理
3. **错误处理**: 如果某个模型不可用，系统会自动回退到默认模型
4. **成本控制**: 不同模型的计费方式不同，请查看各厂商的定价策略

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ValueError: config must contain a [model] api_key
   ```
   解决：检查环境变量或配置中的API密钥是否正确

2. **模型不支持**
   ```
   ⚠️  未知模型 xxx，使用默认的 DeepSeek
   ```
   解决：使用支持模型列表中的模型名称

3. **网络连接问题**
   ```
   ❌ 创建大模型客户端失败: Connection error
   ```
   解决：检查网络连接和API端点是否可访问

### 调试模式

```python
config = LinguaSQLConfig(
    api=APIConfig(
        api_key="your_api_key",
        model="qwen-turbo"
    ),
    debug=True  # 启用调试模式
)

nl = LinguaSQL(config=config)
```

启用调试模式后，系统会输出详细的配置信息和错误信息，便于排查问题。
