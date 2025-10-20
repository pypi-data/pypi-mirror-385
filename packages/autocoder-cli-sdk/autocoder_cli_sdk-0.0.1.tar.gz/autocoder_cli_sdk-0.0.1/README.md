# AutoCoder CLI SDK for Python

一个便于在Python代码中调用`auto-coder.run`功能的SDK，无需直接使用subprocess或fork进程。

## 特性

- 🚀 **易于使用**: 提供简洁直观的API接口
- 🔄 **同步/异步**: 同时支持同步和异步调用方式
- 📡 **流式处理**: 支持实时流式输出和事件处理
- 💬 **会话管理**: 内置会话上下文管理，支持多轮对话
- ⚡ **并发支持**: 异步客户端支持并发查询
- 🛠 **完整配置**: 支持所有auto-coder.run命令行选项
- 📦 **零依赖**: 可选择性使用内部SDK或subprocess调用
- 🐍 **类型提示**: 完整的类型提示支持

## 安装

### 使用 uv (推荐)

```bash
cd cli-sdks/python
uv sync  # 安装依赖并创建虚拟环境
```

### 使用 pip

```bash
cd cli-sdks/python
pip install -e .
```

## 快速开始

### 基础用法（文本格式 - Generator接口）

```python
from autocoder_cli_sdk import AutoCoderClient, QueryOptions

# 创建客户端
client = AutoCoderClient()

# 执行查询，返回generator
options = QueryOptions(output_format="text")

for line in client.query("创建一个Python函数来计算斐波那契数列", options):
    print(line)  # 逐行输出生成的代码
```

### JSON格式输出（Pydantic模型）

```python
from autocoder_cli_sdk import AutoCoderClient, QueryOptions, QueryResponseModel

client = AutoCoderClient()
options = QueryOptions(output_format="json")

for response in client.query("创建一个Python类", options):
    if isinstance(response, QueryResponseModel):
        print(f"事件总数: {response.summary.total_events}")
        print(f"最终结果: {response.final_result}")
```

### 异步用法

```python
import asyncio
from autocoder_cli_sdk import AsyncAutoCoderClient, QueryOptions

async def main():
    async with AsyncAutoCoderClient() as client:
        options = QueryOptions(output_format="text")
        
        async for line in client.query("创建一个Python类来管理任务队列", options):
            print(line)  # 异步逐行输出

asyncio.run(main())
```

### 中止操作

```python
import asyncio
from autocoder_cli_sdk import AsyncAutoCoderClient

async def main():
    async with AsyncAutoCoderClient() as client:
        # 启动查询
        query_task = asyncio.create_task(
            client.query("复杂的查询任务").__anext__()
        )
        
        # 5秒后中止
        await asyncio.sleep(5)
        if client.is_running:
            success = await client.abort()  # 优雅中止
            # 或者 await client.abort_force()  # 强制中止
            
asyncio.run(main())
```

### 流式处理

```python
import asyncio
from autocoder_cli_sdk import AsyncAutoCoderClient

async def main():
    async with AsyncAutoCoderClient() as client:
        async for event in client.stream_query("创建一个Web API"):
            if event.event_type == "content":
                print(event.content, end="", flush=True)

asyncio.run(main())
```

### 会话管理

```python
from autocoder_cli_sdk import AutoCoderClient

client = AutoCoderClient()

# 使用会话上下文进行多轮对话
with client.session() as session:
    # 第一轮
    result1 = session.query("创建一个User类")
    
    # 第二轮（基于第一轮的上下文）
    result2 = session.query("为User类添加验证方法")
    
    # 第三轮
    result3 = session.query("添加单元测试")
```

## API 文档

### 客户端类

#### `AutoCoderClient` (同步客户端)

主要的同步客户端，提供所有基础功能。

```python
class AutoCoderClient:
    def __init__(self, config: Optional[SDKConfig] = None)
    def query(self, prompt: str, options: Optional[QueryOptions] = None) -> QueryResult
    def stream_query(self, prompt: str, options: Optional[QueryOptions] = None) -> Iterator[StreamEvent]
    def configure(self, config_dict: Dict[str, str]) -> ConfigResult
    def session(self, session_id: Optional[str] = None) -> ContextManager
    def get_version(self) -> str
```

#### `AsyncAutoCoderClient` (异步客户端)

异步版本的客户端，支持并发和流式处理。

```python
class AsyncAutoCoderClient:
    async def query(self, prompt: str, options: Optional[QueryOptions] = None) -> QueryResult
    async def stream_query(self, prompt: str, options: Optional[QueryOptions] = None) -> AsyncIterator[StreamEvent]
    async def batch_query(self, prompts: List[str], max_concurrency: int = 3) -> List[QueryResult]
    async def configure(self, config_dict: Dict[str, str]) -> ConfigResult
    async def session(self, session_id: Optional[str] = None) -> AsyncContextManager
```

### 配置类

#### `SDKConfig` (SDK全局配置)

```python
@dataclass
class SDKConfig:
    default_model: Optional[str] = None
    default_max_turns: int = 10000
    default_permission_mode: str = "manual"
    default_output_format: str = "text"
    verbose: bool = False
    default_cwd: Optional[str] = None
    system_prompt_path: Optional[str] = None
    include_rules: bool = False
    default_allowed_tools: Optional[List[str]] = None
```

#### `QueryOptions` (查询选项)

```python
@dataclass
class QueryOptions:
    model: Optional[str] = None
    max_turns: Optional[int] = None
    system_prompt: Optional[str] = None
    output_format: str = "text"
    verbose: bool = False
    cwd: Optional[str] = None
    session_id: Optional[str] = None
    continue_session: bool = False
    allowed_tools: Optional[List[str]] = None
    permission_mode: str = "manual"
    include_rules: bool = False
    pr: bool = False
    is_sub_agent: bool = False
    
    # 异步代理运行器选项
    async_mode: bool = False
    split_mode: str = "h1"
    delimiter: str = "==="
    min_level: int = 1
    max_level: int = 3
    workdir: Optional[str] = None
    from_branch: str = ""
    bg_mode: bool = False
    task_prefix: str = ""
    worktree_name: Optional[str] = None
```

### 响应类

#### `QueryResult` (查询结果)

```python
@dataclass
class QueryResult:
    success: bool
    content: str
    error: Optional[str] = None
    session_id: Optional[str] = None
    events: List[StreamEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    
    @property
    def is_success(self) -> bool
    @property
    def has_error(self) -> bool
```

#### `StreamEvent` (流式事件)

```python
@dataclass
class StreamEvent:
    event_type: str  # start, content, tool_call, completion, error, end
    data: Dict[str, Any]
    timestamp: Optional[datetime] = None
    
    @property
    def is_content(self) -> bool
    @property
    def content(self) -> str
```

## 高级用法

### 自定义配置

```python
from autocoder_cli_sdk import AutoCoderClient, SDKConfig, QueryOptions

# 全局配置
config = SDKConfig(
    default_model="gpt-4",
    default_max_turns=20,
    verbose=True,
    default_permission_mode="acceptEdits"
)

client = AutoCoderClient(config)

# 查询特定选项
options = QueryOptions(
    max_turns=15,
    system_prompt="你是一个Python专家",
    output_format="json",
    include_rules=True
)

result = client.query("创建一个数据结构", options)
```

### 并发查询

```python
import asyncio
from autocoder_cli_sdk import AsyncAutoCoderClient

async def main():
    async with AsyncAutoCoderClient() as client:
        prompts = [
            "创建一个用户管理模块",
            "创建一个日志模块", 
            "创建一个配置管理模块"
        ]
        
        # 并发执行，最大并发数为2
        results = await client.batch_query(prompts, max_concurrency=2)
        
        for i, result in enumerate(results):
            print(f"查询 {i+1}: {'成功' if result.is_success else '失败'}")
```

### 配置管理

```python
from autocoder_cli_sdk import AutoCoderClient

client = AutoCoderClient()

# 设置配置
result = client.configure({
    "model": "gpt-4",
    "max_turns": "25",
    "permission_mode": "acceptEdits"
})

if result.success:
    print("配置更新成功")
    print("应用的配置:", result.applied_configs)
```

### 异步代理运行器

```python
from autocoder_cli_sdk import AutoCoderClient, QueryOptions

client = AutoCoderClient()

# 使用异步代理运行器模式
options = QueryOptions(
    async_mode=True,
    split_mode="h1",
    workdir="/path/to/work",
    bg_mode=False,
    task_prefix="feature-"
)

result = client.query("""
# 任务1：用户管理模块

创建用户管理相关功能...

# 任务2：权限管理模块  

创建权限管理相关功能...
""", options)
```

## 示例项目

查看 `examples/` 目录中的完整示例：

- `basic_usage.py` - 基础用法演示
- `async_usage.py` - 异步用法演示  
- `session_management.py` - 会话管理演示

运行示例：

```bash
# 使用 uv (推荐)
uv run python examples/basic_usage.py
uv run python examples/async_usage.py
uv run python examples/session_management.py

# 或使用开发脚本
python scripts/dev.py example basic_usage
python scripts/dev.py example async_usage
```

## 错误处理

```python
from autocoder_cli_sdk import AutoCoderClient, AutoCoderError, ValidationError

client = AutoCoderClient()

try:
    result = client.query("创建一个函数")
    if result.is_success:
        print(result.content)
    else:
        print("执行失败:", result.error)
        
except ValidationError as e:
    print("参数验证失败:", e)
except AutoCoderError as e:
    print("SDK错误:", e)  
except Exception as e:
    print("未知错误:", e)
```

## 依赖说明

这个SDK设计为可选依赖：

1. **内部SDK模式**: 如果可以导入`autocoder.sdk`模块，将直接使用内部API，性能更好
2. **Subprocess模式**: 如果无法导入内部模块，将回退到调用`auto-coder.run`命令行工具

两种模式API完全一致，用户无需关心底层实现。

## 类型提示

SDK提供完整的类型提示支持，在支持的IDE中可以获得良好的代码补全和类型检查：

```python
from typing import Optional
from autocoder_cli_sdk import AutoCoderClient, QueryOptions, QueryResult

client: AutoCoderClient = AutoCoderClient()
options: Optional[QueryOptions] = QueryOptions(max_turns=10)
result: QueryResult = client.query("prompt", options)
```

## 开发

### 设置开发环境

```bash
cd cli-sdks/python
uv sync  # 安装所有依赖（包括开发依赖）
```

### 开发任务

```bash
# 运行测试
python scripts/dev.py test
# 或直接使用 uv run pytest tests/ -v

# 代码格式化
python scripts/dev.py format
# 或分别运行 uv run black . 和 uv run isort .

# 代码检查
python scripts/dev.py lint
# 或直接使用 uv run flake8 autocoder_cli_sdk/

# 构建包
python scripts/dev.py build
# 或直接使用 uv build

# 运行示例
python scripts/dev.py example basic_usage
```

### 版本管理

项目使用 uv 进行依赖管理：

- `pyproject.toml` - 项目配置和依赖定义
- `uv.lock` - 锁定的依赖版本
- `.venv/` - 虚拟环境（由 uv 自动创建）

## 版本兼容性

- Python 3.7+
- 兼容所有版本的auto-coder.run命令行工具
- 支持asyncio (Python 3.7+)
- 使用 uv 0.8+ 进行包管理

## 许可证

MIT License - 详见 LICENSE 文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个SDK。开发流程：

1. Fork 项目
2. 创建功能分支
3. 使用 `uv sync` 设置开发环境
4. 运行 `python scripts/dev.py test` 确保测试通过
5. 运行 `python scripts/dev.py format` 格式化代码
6. 提交 Pull Request
