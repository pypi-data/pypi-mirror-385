"""
基础 Agent Runtime 使用示例

这个示例展示了如何使用重新实现的 PPIO Agent Runtime 模块。

注意：request 参数接收原始的请求字典，可以包含任意自定义字段，不会丢失数据。
"""

from ppio_sandbox.agent_runtime import AgentRuntimeApp, RequestContext

# 创建应用实例
app = AgentRuntimeApp(debug=True)


@app.entrypoint
def my_agent(request: dict, context: RequestContext) -> dict:
    """基础 Agent 实现
    
    request 是原始的请求字典，包含所有用户传入的字段。
    你可以访问任意自定义字段，不受限制。
    """
    # 访问标准字段
    query = request.get("query", "")
    
    # 访问任意自定义字段（不会丢失）
    max_tokens = request.get("max_tokens", 100)
    temperature = request.get("temperature", 0.7)
    custom_field = request.get("custom_field", "default")
    
    # 从 context 获取系统字段
    sandbox_id = context.sandbox_id  # 如果请求中包含则有值
    request_id = context.request_id  # 系统自动生成
    
    # Agent 处理逻辑
    result = f"处理查询: {query} (max_tokens={max_tokens}, temp={temperature})"
    
    return {
        "response": result,
        "sandbox_id": sandbox_id,
        "metadata": {
            "request_id": request_id,
            "custom_field": custom_field
        }
    }


@app.ping
def health_check() -> dict:
    """自定义健康检查"""
    return {"status": "healthy", "service": "basic-agent"}


if __name__ == "__main__":
    app.run(port=8080)
