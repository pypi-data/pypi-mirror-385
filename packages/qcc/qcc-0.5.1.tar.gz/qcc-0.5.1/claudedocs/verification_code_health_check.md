# 验证码健康检查机制

## 📋 问题背景

### 原始问题
某些 API 服务器（如 88code.org）在 API Key 被禁用时，返回的是：
- **HTTP 200** 状态码（而不是标准的 401/403）
- **错误信息在 JSON body 中**：`{"error": {"type": "Bad Request", "message": "..."}}`

这导致 QCC 的健康检查将其误判为成功，因为：
1. HTTP 状态码是 200
2. 没有抛出异常
3. 原有逻辑直接认为 200 = 成功

### 挑战
不同的 API 服务器错误格式各异：
- 标准 Anthropic：返回 HTTP 401/403
- 某些代理：返回 HTTP 200 + `{"error": {...}}`
- 其他服务：可能返回其他格式

需要一个**通用的验证机制**，不依赖特定的错误格式或 HTTP 状态码。

## 🎯 解决方案：验证码机制

### 核心思路
**用户建议**：让 AI 在响应中回复一个随机验证码，通过检查响应是否包含该验证码来判断是否真正成功。

### 机制设计

#### 1. 生成随机验证码
每次健康检查时生成 6 位随机字母数字组合：
```python
verification_code = ''.join(
    random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6)
)
# 例如: "A1B2C3", "XYZ789", "TEST99"
```

#### 2. 发送验证请求
将验证码嵌入测试消息：
```python
test_message = f"收到消息请仅回复这个验证码：{verification_code}"
```

#### 3. 验证响应
检查 AI 的响应是否包含验证码（不区分大小写）：
```python
def _validate_response(verification_code: str, response: str) -> bool:
    if not response or not verification_code:
        return False
    return verification_code.upper() in response.upper()
```

### 验证逻辑流程

```
┌─────────────────────────────────────────────────────────┐
│ 1. 生成验证码: "ABC123"                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 发送请求:                                             │
│    "收到消息请仅回复这个验证码：ABC123"                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 接收响应                                              │
│                                                          │
│    正常情况: "ABC123" 或 "好的，验证码是：ABC123"        │
│    错误情况: "" 或 "API key is disabled" 或其他          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. 验证                                                  │
│                                                          │
│    检查响应中是否包含 "ABC123" (不区分大小写)            │
│    • 包含 → response_valid = True                        │
│    • 不包含 → response_valid = False                     │
└─────────────────────────────────────────────────────────┘
```

## 📊 实测效果

### 测试场景 1：被禁用的 API Key

**配置**：
```python
base_url = "https://www.88code.org/api"
api_key = "88_3b5c724a7ce3e94496409e5294fa4414eac5266c03ba74ce6361aa2d15d6101d"
```

**结果**：
```
HTTP 状态码: 200
响应内容: ''  (空字符串)
验证码: 5MKY9D
响应中包含验证码: False
response_valid: False  ✅

结论: 被正确识别为无效！
```

### 测试场景 2：正常的 API Key

**配置**：
```python
base_url = "https://jp.duckcoding.com"
api_key = "sk-7yVW8CrBSuYvV3sKdzHFS42sGS1TXTbiWWTjtHwv26QHl12j"
```

**结果**：
```
HTTP 状态码: 200
响应内容: 'EHPLSP'
验证码: EHPLSP
响应中包含验证码: True
response_valid: True  ✅

结论: 验证成功！
```

## 🔧 实现细节

### 修改的文件

#### 1. [fastcc/proxy/conversational_checker.py](../fastcc/proxy/conversational_checker.py)

**变更内容**：

**a) 移除固定测试消息列表**
```python
# 删除前
self.test_messages = [
    "收到消息请回复 1",
    "你好，请回复确认",
    # ... 更多消息
]

# 删除后
# 不再需要，每次动态生成
```

**b) 动态生成验证码**
```python
# 在 check_endpoint() 中
verification_code = ''.join(
    random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6)
)
check.test_message = f"收到消息请仅回复这个验证码：{verification_code}"
check.verification_code = verification_code
```

**c) 简化验证逻辑**
```python
# 修改前：复杂的规则匹配
def _validate_response(self, test_message: str, response: str) -> bool:
    if "回复 1" in test_message:
        return '1' in response or 'one' in response
    if "1+1" in test_message:
        return '2' in response
    # ... 更多规则

# 修改后：简单的验证码检查
def _validate_response(self, verification_code: str, response: str) -> bool:
    if not response or not verification_code:
        return False
    return verification_code.upper() in response.upper()
```

**d) 兼容多种响应格式**
```python
# 支持不同的 JSON 响应格式
if 'content' in data and data['content']:
    content = data['content'][0].get('text', '')
elif 'message' in data:
    content = data['message']
elif 'text' in data:
    content = data['text']
```

#### 2. [fastcc/proxy/health_check_models.py](../fastcc/proxy/health_check_models.py)

**新增字段**：
```python
class ConversationalHealthCheck:
    def __init__(self, endpoint_id: str):
        # ... 其他字段
        self.verification_code: Optional[str] = None  # 新增
```

### 增加 max_tokens

```python
# 从 10 增加到 20，确保有足够空间返回验证码
self.max_tokens = 20
```

## ✅ 测试覆盖

### 单元测试

[tests/test_verification_logic.py](../tests/test_verification_logic.py) - 7 个测试用例：

1. ✅ `test_validate_response_basic` - 基本验证
2. ✅ `test_validate_response_case_insensitive` - 不区分大小写
3. ✅ `test_validate_response_embedded` - 嵌入文本中
4. ✅ `test_validate_response_invalid` - 无效情况
5. ✅ `test_validate_response_edge_cases` - 边界情况
6. ✅ `test_verification_code_format` - 验证码格式
7. ✅ `test_real_world_scenarios` - 真实场景

**测试结果**：
```bash
$ uvx -n pytest tests/test_verification_logic.py -v

============================= test session starts =============================
tests/test_verification_logic.py::test_validate_response_basic PASSED    [ 14%]
tests/test_verification_logic.py::test_validate_response_case_insensitive PASSED [ 28%]
tests/test_verification_logic.py::test_validate_response_embedded PASSED [ 42%]
tests/test_verification_logic.py::test_validate_response_invalid PASSED  [ 57%]
tests/test_verification_logic.py::test_validate_response_edge_cases PASSED [ 71%]
tests/test_verification_logic.py::test_verification_code_format PASSED   [ 85%]
tests/test_verification_logic.py::test_real_world_scenarios PASSED       [100%]

============================== 7 passed in 0.04s ==============================
```

## 🌟 优势

### 1. **通用性强**
- ✅ 不依赖特定的 HTTP 状态码
- ✅ 不依赖特定的错误格式
- ✅ 适用于各种 API 服务器实现
- ✅ 支持各种代理和转发服务

### 2. **可靠性高**
- ✅ 验证真实的 AI 响应能力
- ✅ 避免 HTTP 200 + 错误 body 的陷阱
- ✅ 准确识别被禁用/无效的 API Key
- ✅ 不会被缓存响应干扰（每次验证码不同）

### 3. **实现简单**
- ✅ 逻辑清晰，易于理解和维护
- ✅ 代码量减少（删除复杂的规则匹配）
- ✅ 测试用例简单直观
- ✅ 性能开销低（简单的字符串包含检查）

### 4. **安全性好**
- ✅ 每次使用不同的验证码
- ✅ 避免固定模式被预测或缓存
- ✅ 6 位字母数字 = 36^6 = 2,176,782,336 种可能
- ✅ 碰撞概率极低

## 📈 性能影响

### Token 使用
- **之前**：`max_tokens: 10`
- **现在**：`max_tokens: 20`
- **增加**：10 tokens/请求（用于返回验证码）
- **成本影响**：几乎可忽略（健康检查使用最便宜的 haiku 模型）

### 响应时间
- **无显著影响**：验证码验证是简单的字符串包含检查（O(n)）
- **实测**：< 1ms（可忽略）

## 🎯 适用场景

### 完美适用
✅ 所有 Claude API 兼容服务
✅ 各种代理和负载均衡器
✅ 自定义 API endpoint
✅ 需要验证真实 AI 能力的场景

### 不适用
❌ 非 AI 对话 API（如纯 REST API）
❌ 不支持对话的服务

## 🔄 向后兼容性

✅ **完全向后兼容**
- 不影响现有的 endpoint 配置
- 不改变健康检查的调用方式
- 只是改进了内部验证逻辑
- 对用户透明

## 📝 使用示例

### 健康检查日志示例

**成功的健康检查**：
```log
[health_check] Endpoint 1e3e69eb 健康检查成功 (1824ms, 评分: 80)
  测试消息: 收到消息请仅回复这个验证码：EHPLSP
  响应内容: EHPLSP
  响应有效: True
```

**失败的健康检查**：
```log
[health_check] Endpoint 71de8865 健康检查成功 (686ms, 评分: 20)
  测试消息: 收到消息请仅回复这个验证码：5MKY9D
  响应内容: (空)
  响应有效: False
  → 被识别为无效 endpoint
```

## 🚀 未来增强

### 可能的改进方向

1. **可配置的验证码长度**
   ```python
   verification_code_length: int = 6  # 可配置
   ```

2. **多语言支持**
   ```python
   test_messages = {
       'en': f"Reply with this code: {code}",
       'zh': f"收到消息请仅回复这个验证码：{code}",
       'ja': f"このコードで返信してください：{code}"
   }
   ```

3. **验证码复杂度等级**
   ```python
   # 简单：纯数字
   # 中等：字母数字
   # 复杂：字母数字+特殊字符
   ```

## 📚 相关文档

- [健康检查机制说明](./health_check_explained.md)
- [Endpoint 稳定 ID 修复](./endpoint_stable_id_fix.md)
- [HTTP 504 错误诊断指南](./http_504_error_guide.md)

---

**修复日期**: 2025-10-17
**版本**: v0.4.2-dev
**测试状态**: ✅ 7/7 测试通过
**提出者**: 用户建议
**实现**: Claude + QCC Team
