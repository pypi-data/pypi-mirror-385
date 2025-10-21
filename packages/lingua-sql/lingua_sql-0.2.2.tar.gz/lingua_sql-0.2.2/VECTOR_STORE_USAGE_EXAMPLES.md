# LinguaSQL 向量数据库使用示例

本文档展示如何使用 LinguaSQL 支持的各种向量数据库。

## 支持的向量数据库

### 1. ChromaDB
- **类型**: `chromadb`
- **特点**: 开源的向量数据库，支持持久化和内存模式
- **优势**: 易于使用，支持多种嵌入模型，内置去重功能
- **适用场景**: 中小规模应用，快速原型开发

### 2. FAISS
- **类型**: `faiss`
- **特点**: Facebook 开源的高性能相似性搜索库
- **优势**: 高性能，支持多种索引类型，内存效率高
- **适用场景**: 大规模应用，高性能要求

## 使用方法

### 方法1: 环境变量配置

```bash
# 设置向量数据库类型
export LINGUA_SQL_VECTOR_STORE="faiss"  # 或 "chromadb"

# 设置存储路径
export LINGUA_SQL_VECTOR_STORE_PATH="./vector_data"

# 设置嵌入模型（仅FAISS支持）
export LINGUA_SQL_EMBEDDING_MODEL="paraphrase-multilingual-MiniLM-L12-v2"
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
from lingua_sql.config import LinguaSQLConfig, APIConfig, VectorStoreConfig, DatabaseConfig

# 使用 FAISS 向量数据库
config = LinguaSQLConfig(
    api=APIConfig(
        api_key="your_api_key",
        model="qwen-turbo"
    ),
    vector_store=VectorStoreConfig(
        type="faiss",
        path="./faiss_data",
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
        n_results_sql=10,
        n_results_ddl=5,
        n_results_documentation=5
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

### 方法3: 使用 ChromaDB

```python
from lingua_sql import LinguaSQL
from lingua_sql.config import LinguaSQLConfig, APIConfig, VectorStoreConfig

# 使用 ChromaDB 向量数据库
config = LinguaSQLConfig(
    api=APIConfig(
        api_key="your_api_key",
        model="deepseek-chat"
    ),
    vector_store=VectorStoreConfig(
        type="chromadb",
        path="./chroma_data",
        client="persistent",  # persistent 或 in-memory
        n_results_sql=10
    )
)

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

# 添加DDL
nl.train(ddl="CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), age INT)")

# 添加文档
nl.train(documentation="用户表包含用户的基本信息，包括ID、姓名和年龄")

# 生成SQL
sql = nl.generate_sql("查询年龄大于25的用户")
print(sql)

# 执行查询
result = nl.ask("查询年龄大于25的用户")
print(result)
```

### 向量数据库特定功能

#### ChromaDB 特定功能

```python
# 获取相似问题
similar_questions = nl.get_similar_questions("查询用户信息", n_results=5)
for q in similar_questions:
    print(f"相似度: {q.get('score', 0):.3f}, 问题: {q.get('document', '')}")

# 清理重复数据
cleaned = nl.clean_duplicates()
print(f"清理了 {cleaned} 个重复数据")

# 获取所有DDL
all_ddl = nl.get_ddl()
print(f"共有 {len(all_ddl)} 个DDL")
```

#### FAISS 特定功能

```python
# 获取统计信息（仅FAISS支持）
if hasattr(nl.vector_store, 'get_stats'):
    stats = nl.vector_store.get_stats()
    print(f"向量数据库统计: {stats}")

# 自定义嵌入模型
from sentence_transformers import SentenceTransformer

# 使用中文嵌入模型
config = LinguaSQLConfig(
    vector_store=VectorStoreConfig(
        type="faiss",
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2"
    )
)
nl = LinguaSQL(config=config)
```

### 性能对比示例

```python
import time
from lingua_sql import LinguaSQL
from lingua_sql.config import LinguaSQLConfig, VectorStoreConfig

def benchmark_vector_store(vector_store_type, test_data):
    """性能测试函数"""
    config = LinguaSQLConfig(
        vector_store=VectorStoreConfig(
            type=vector_store_type,
            path=f"./test_{vector_store_type}"
        )
    )
    
    nl = LinguaSQL(config=config)
    
    # 测试添加数据
    start_time = time.time()
    for question, sql in test_data:
        nl.train(question=question, sql=sql)
    add_time = time.time() - start_time
    
    # 测试查询
    start_time = time.time()
    for question, _ in test_data[:10]:  # 只测试前10个
        nl.get_similar_question_sql(question)
    query_time = time.time() - start_time
    
    return {
        'vector_store': vector_store_type,
        'add_time': add_time,
        'query_time': query_time,
        'total_data': len(test_data)
    }

# 准备测试数据
test_data = [
    (f"查询用户{i}的信息", f"SELECT * FROM users WHERE id = {i}")
    for i in range(100)
]

# 测试 ChromaDB
chromadb_result = benchmark_vector_store("chromadb", test_data)
print(f"ChromaDB 结果: {chromadb_result}")

# 测试 FAISS
faiss_result = benchmark_vector_store("faiss", test_data)
print(f"FAISS 结果: {faiss_result}")
```

## 配置参数详解

### VectorStoreConfig 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | str | "chromadb" | 向量数据库类型 |
| `path` | str | "." | 数据存储路径 |
| `client` | str | "persistent" | 客户端类型（仅ChromaDB） |
| `embedding_model` | str | None | 嵌入模型名称（仅FAISS） |
| `n_results_sql` | int | 10 | SQL查询返回结果数 |
| `n_results_ddl` | int | 10 | DDL查询返回结果数 |
| `n_results_documentation` | int | 10 | 文档查询返回结果数 |

### 环境变量

| 环境变量 | 说明 | 示例值 |
|----------|------|--------|
| `LINGUA_SQL_VECTOR_STORE` | 向量数据库类型 | "faiss" |
| `LINGUA_SQL_VECTOR_STORE_PATH` | 存储路径 | "./vector_data" |
| `LINGUA_SQL_EMBEDDING_MODEL` | 嵌入模型 | "paraphrase-multilingual-MiniLM-L12-v2" |

## 选择建议

### 根据应用规模选择

- **小规模应用 (< 10万向量)**:
  - 推荐: ChromaDB
  - 原因: 易于使用，功能完整，支持持久化

- **中大规模应用 (> 10万向量)**:
  - 推荐: FAISS
  - 原因: 高性能，内存效率高，支持多种索引类型

### 根据使用场景选择

- **开发测试**:
  - 推荐: ChromaDB
  - 原因: 快速部署，易于调试

- **生产环境**:
  - 推荐: FAISS
  - 原因: 高性能，稳定性好

- **多语言支持**:
  - 推荐: FAISS + 多语言嵌入模型
  - 原因: 支持更多嵌入模型选择

## 迁移指南

### 从 ChromaDB 迁移到 FAISS

```python
# 1. 导出 ChromaDB 数据
chromadb_nl = LinguaSQL(config=ChromaDBConfig())
training_data = chromadb_nl.get_training_data()

# 2. 创建 FAISS 实例
faiss_nl = LinguaSQL(config=FAISSConfig())

# 3. 导入数据
for _, row in training_data.iterrows():
    if row['training_data_type'] == 'sql':
        faiss_nl.train(question=row['question'], sql=row['content'])
    elif row['training_data_type'] == 'ddl.txt':
        faiss_nl.train(ddl=row['content'])
    elif row['training_data_type'] == 'documentation':
        faiss_nl.train(documentation=row['content'])

print("迁移完成")
```

## 故障排除

### 常见问题

1. **FAISS 安装问题**
   ```
   ImportError: No module named 'faiss'
   ```
   解决：`pip install faiss-cpu` 或 `pip install faiss-gpu`

2. **嵌入模型下载问题**
   ```
   OSError: [Errno 2] No such file or directory
   ```
   解决：检查网络连接，或手动下载模型

3. **内存不足**
   ```
   MemoryError: Unable to allocate array
   ```
   解决：减少 `n_results_*` 参数，或使用更小的嵌入模型

4. **存储路径权限问题**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   解决：检查存储路径的读写权限

### 调试模式

```python
config = LinguaSQLConfig(
    vector_store=VectorStoreConfig(
        type="faiss",
        path="./debug_vector_data"
    ),
    debug=True  # 启用调试模式
)

nl = LinguaSQL(config=config)
```

启用调试模式后，系统会输出详细的配置信息和错误信息，便于排查问题。

## 最佳实践

1. **数据备份**: 定期备份向量数据库文件
2. **性能监控**: 监控查询响应时间和内存使用
3. **模型选择**: 根据语言和领域选择合适的嵌入模型
4. **索引优化**: 对于大规模数据，考虑使用 FAISS 的量化索引
5. **定期清理**: 定期清理重复和无用的数据
