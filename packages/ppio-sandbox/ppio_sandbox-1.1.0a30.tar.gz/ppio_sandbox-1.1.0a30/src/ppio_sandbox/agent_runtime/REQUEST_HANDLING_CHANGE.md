# 请求处理方式变更说明

## 变更概述

从本版本开始，Agent Runtime 不再强制验证和转换请求数据为 `InvocationRequest` 模型。服务器现在直接将原始请求数据传递给用户的 entrypoint 函数，**不会丢失任何用户字段**。

## 变更原因

### 之前的问题

```python
# 旧的实现
request_data = await request.json()
invoke_request = InvocationRequest(**request_data)  # ❌ 强制转换，丢失未定义的字段
```

**问题：**
- 用户传入的任意自定义字段会被丢弃
- 限制了用户的灵活性
- InvocationRequest 模型需要预先定义所有可能的字段

### 新的实现

```python
# 新的实现
request_data = await request.json()  # ✅ 保留原始数据
# 直接传递给用户函数，不进行模型转换
```

**优点：**
- ✅ 保留所有用户字段，不丢失数据
- ✅ 最大的灵活性，用户可以传入任意结构
- ✅ Runtime 作为透明管道，不限制数据格式

## 新的使用方式

### 服务器端（Runtime）

```python
from ppio_sandbox.agent_runtime import AgentRuntimeApp, RequestContext

app = AgentRuntimeApp()

@app.entrypoint
def my_agent(request: dict, context: RequestContext):
    """
    request: 原始请求字典，包含所有用户传入的字段
    context: 系统上下文（sandbox_id, request_id, headers）
    """
    # 访问任意字段，不受限制
    query = request.get("query")
    max_tokens = request.get("max_tokens")
    temperature = request.get("temperature")
    custom_param = request.get("custom_param")  # 任意自定义字段
    
    # 系统字段从 context 获取
    sandbox_id = context.sandbox_id  # 如果请求包含则有值
    request_id = context.request_id  # 系统生成的唯一 ID
    
    return {"result": "success"}
```

### 客户端调用

```python
# 可以发送任意结构的 JSON
response = requests.post("http://localhost:8080/invocations", json={
    "query": "你好",
    "max_tokens": 100,
    "temperature": 0.7,
    "custom_field": "任意值",
    "nested": {
        "data": "嵌套数据也完全保留"
    },
    # 可选的系统字段
    "sandbox_id": "my-sandbox"
})
```

## RequestContext 说明

`RequestContext` 只包含系统字段：

```python
class RequestContext:
    sandbox_id: Optional[str]   # 从请求中提取（如果存在）
    request_id: str             # 系统生成的唯一 ID
    headers: Dict[str, str]     # HTTP 请求头
```

### 系统字段的处理

1. **`sandbox_id`**: 
   - 如果请求中包含 `sandbox_id` 字段，会被提取到 context 中
   - 用户也可以直接从 `request.get("sandbox_id")` 获取
   - 主要用于向后兼容

2. **`request_id`**:
   - 系统自动生成（UUID）
   - 用于日志追踪和响应 metadata
   - 用户无需（也无法）传入

3. **`headers`**:
   - HTTP 请求头信息
   - 包含 content-type, authorization 等

## InvocationRequest 模型的新角色

`InvocationRequest` 模型**不再用于强制验证**，现在的作用是：

1. **文档参考**：告诉用户常见的字段有哪些
2. **客户端可选验证**：客户端可以选择使用它来验证
3. **向后兼容**：保留以避免破坏现有代码

```python
class InvocationRequest(BaseModel):
    """仅供参考，不强制使用"""
    prompt: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    sandbox_id: Optional[str] = None
    timeout: Optional[int] = None  # 注：Runtime server 不使用此字段
    stream: bool = False  # 已弃用
    metadata: Optional[Dict[str, Any]] = None
```

## 实际场景示例

### LLM Agent

```python
@app.entrypoint
async def llm_agent(request: dict, context: RequestContext):
    # 完全自定义的请求结构
    messages = request.get("messages", [])
    model = request.get("model", "gpt-4")
    max_tokens = request.get("max_tokens", 1000)
    temperature = request.get("temperature", 0.7)
    tools = request.get("tools", [])
    
    # 流式响应
    for token in llm_generate(messages, model, max_tokens, temperature):
        yield token
```

调用时：
```json
{
  "messages": [{"role": "user", "content": "你好"}],
  "model": "gpt-4",
  "max_tokens": 1000,
  "temperature": 0.7,
  "tools": [{"type": "function", "function": {...}}]
}
```

### 数据处理 Agent

```python
@app.entrypoint
def data_processor(request: dict, context: RequestContext):
    # 完全自定义的结构
    input_data = request.get("data")
    operations = request.get("operations", [])
    output_format = request.get("format", "json")
    options = request.get("options", {})
    
    result = process_data(input_data, operations, options)
    return format_output(result, output_format)
```

调用时：
```json
{
  "data": [...],
  "operations": ["filter", "transform", "aggregate"],
  "format": "csv",
  "options": {
    "compression": "gzip",
    "encoding": "utf-8"
  }
}
```

## 向后兼容性

### 完全兼容

如果你之前这样写：

```python
@app.entrypoint
def agent(request: dict, context: RequestContext):
    query = request.get("query")
    # ...
```

**不需要任何修改**，代码会继续正常工作。

### 新增能力

现在你可以：

```python
@app.entrypoint
def agent(request: dict, context: RequestContext):
    # 访问任意自定义字段
    custom_field = request.get("custom_field")  # ✅ 不会丢失
    nested_data = request.get("nested", {}).get("data")  # ✅ 嵌套数据完全保留
```

## 技术实现细节

### 服务器端改动

**文件：** `runtime/server.py`

**主要变化：**

1. **`_handle_invocations`**:
   ```python
   # 之前
   invoke_request = InvocationRequest(**request_data)  # ❌
   
   # 现在
   # 直接使用 request_data，不转换  # ✅
   context = RequestContext(
       sandbox_id=request_data.get("sandbox_id"),
       request_id=str(uuid.uuid4()),
       headers=dict(request.headers)
   )
   ```

2. **`_execute_agent_function`**:
   ```python
   # 之前
   async def _execute_agent_function(self, request: InvocationRequest, ...) -> Any:
       args = (request.model_dump(), context)  # ❌
   
   # 现在
   async def _execute_agent_function(self, request_data: Dict[str, Any], ...) -> Any:
       args = (request_data, context)  # ✅ 直接传递原始字典
   ```

### 数据流

```
客户端请求 (任意 JSON)
    ↓
服务器解析 JSON → request_data (dict)
    ↓
提取系统字段 → RequestContext (sandbox_id, request_id, headers)
    ↓
传递给用户函数 → entrypoint(request_data, context)
    ↓
用户访问任意字段 → request.get("any_field")  ✅ 不丢失
```

## 常见问题

### Q: 我需要修改现有代码吗？
A: 不需要。现有代码完全兼容，会继续正常工作。

### Q: InvocationRequest 会被删除吗？
A: 不会。它被保留用于文档和向后兼容，但不再用于强制验证。

### Q: 如何验证请求格式？
A: 你可以在 entrypoint 函数中自行验证：
```python
@app.entrypoint
def agent(request: dict, context: RequestContext):
    # 自定义验证
    if "query" not in request:
        raise ValueError("Missing required field: query")
    
    # 或使用 Pydantic 验证
    from pydantic import BaseModel
    
    class MyRequest(BaseModel):
        query: str
        max_tokens: int = 100
    
    validated = MyRequest(**request)
    return process(validated)
```

### Q: sandbox_id 和 timeout 字段还有用吗？
A: 
- `sandbox_id`: 可选，如果传入会被提取到 context，主要用于向后兼容
- `timeout`: Runtime server 不使用此字段，可能被客户端或平台层使用

### Q: 如何处理嵌套的复杂结构？
A: 完全保留，直接访问：
```python
nested_value = request.get("level1", {}).get("level2", {}).get("value")
```

---

**变更日期：** 2025-10-17  
**影响范围：** Agent Runtime Server (Python SDK)  
**向后兼容：** 是  
**需要用户操作：** 否

