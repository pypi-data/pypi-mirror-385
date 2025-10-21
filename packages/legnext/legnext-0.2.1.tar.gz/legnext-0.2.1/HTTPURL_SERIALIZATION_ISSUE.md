# HttpUrl 序列化问题详解

## 问题概述

当使用 `blend()` 和 `describe()` 等方法传入字符串 URL 时，SDK 会报错无法序列化 `HttpUrl` 对象。

## 根本原因

### 1. Pydantic 的类型转换

在 `types/requests.py` 中，多个请求模型使用了 `HttpUrl` 类型：

```python
class BlendRequest(BaseModel):
    img_urls: list[HttpUrl] = Field(...)  # HttpUrl 对象的列表
    callback: Optional[HttpUrl] = Field(None)

class DescribeRequest(BaseModel):
    img_url: HttpUrl = Field(...)  # HttpUrl 对象
    callback: Optional[HttpUrl] = Field(None)
```

**Pydantic 的行为：**
- 当你传入字符串 `"https://example.com/image.png"` 时
- Pydantic 自动验证并将其转换为 `HttpUrl` 对象
- `HttpUrl` 是一个特殊的 Pydantic 类型，不是普通字符串

### 2. JSON 序列化失败

在 `resources/midjourney.py` 的原始代码中：

```python
def blend(self, img_urls: list[Union[HttpUrl, str]], ...):
    request = BlendRequest(img_urls=img_urls, ...)
    # ❌ 问题出在这里
    data = self._http.request(
        "POST",
        "/v1/blend",
        json=request.model_dump(by_alias=True)  # 缺少 mode='json'
    )
```

**问题流程：**
1. 用户调用：`client.midjourney.blend(["https://example.com/1.png", "https://example.com/2.png"], ...)`
2. Pydantic 将字符串转换为 `HttpUrl` 对象
3. `request.model_dump(by_alias=True)` 返回：
   ```python
   {
       "imgUrls": [HttpUrl("https://example.com/1.png"), HttpUrl("https://example.com/2.png")],
       "aspect_ratio": "1:1"
   }
   ```
4. `httpx` 尝试将这个字典序列化为 JSON
5. **失败！** Python 的标准 JSON 编码器不知道如何序列化 `HttpUrl` 对象

### 3. 为什么其他接口没有立即暴露这个问题？

让我们对比不同类型的字段：

```python
# ✅ 纯字符串字段 - 没问题
class DiffusionRequest(BaseModel):
    text: str  # 字符串直接序列化
    callback: Optional[HttpUrl]  # 可选，很多时候为 None

# ⚠️ 必填 HttpUrl 字段 - 问题明显
class DescribeRequest(BaseModel):
    img_url: HttpUrl  # 必填！每次调用都会触发问题

# ⚠️ HttpUrl 列表 - 问题更明显
class BlendRequest(BaseModel):
    img_urls: list[HttpUrl]  # 列表中的每个元素都是 HttpUrl
```

## 受影响的接口

### 高风险接口（必填 HttpUrl 字段）

这些接口**每次调用都会出错**，因为它们有必填的 URL 参数：

1. **`blend(img_urls)`** - `img_urls: list[HttpUrl]` 必填
   ```python
   # ❌ 修复前会失败
   client.midjourney.blend(
       img_urls=["https://a.com/1.png", "https://b.com/2.png"],
       aspect_ratio="1:1"
   )
   ```

2. **`describe(img_url)`** - `img_url: HttpUrl` 必填
   ```python
   # ❌ 修复前会失败
   client.midjourney.describe(img_url="https://example.com/image.png")
   ```

3. **`retexture(img_url, remix_prompt)`** - `img_url: HttpUrl` 必填
   ```python
   # ❌ 修复前会失败
   client.midjourney.retexture(
       img_url="https://example.com/image.png",
       remix_prompt="marble texture"
   )
   ```

4. **`remove_background(img_url)`** - `img_url: HttpUrl` 必填
   ```python
   # ❌ 修复前会失败
   client.midjourney.remove_background(img_url="https://example.com/image.png")
   ```

5. **`upload_paint(img_url, ...)`** - `img_url: HttpUrl` 必填

### 中等风险接口（可选 HttpUrl 字段）

所有接口都有可选的 `callback` 参数，当用户提供 callback URL 时会出错：

```python
# ❌ 使用 callback 时会失败（修复前）
client.midjourney.diffusion(
    text="a sunset",
    callback="https://webhook.example.com/notify"  # 这会被转换为 HttpUrl
)
```

**受影响的所有接口（19个）：**
- diffusion, variation, upscale, reroll
- blend, describe, shorten
- pan, outpaint
- inpaint, remix, edit, upload_paint
- retexture, remove_background, enhance
- video_diffusion, extend_video, video_upscale

## 解决方案

### 使用 `mode='json'`

Pydantic v2 提供了 `mode='json'` 参数来正确序列化特殊类型：

```python
# ✅ 修复后
def blend(self, img_urls: list[Union[HttpUrl, str]], ...):
    request = BlendRequest(img_urls=img_urls, ...)
    data = self._http.request(
        "POST",
        "/v1/blend",
        json=request.model_dump(by_alias=True, mode='json')  # 添加 mode='json'
    )
```

**`mode='json'` 的作用：**
- 告诉 Pydantic 以 JSON 兼容的方式序列化
- `HttpUrl` 对象 → 字符串
- `datetime` 对象 → ISO 格式字符串
- `Enum` → 枚举值
- 其他特殊类型 → 可序列化的基本类型

### 修复范围

已更新**所有 37 个方法调用**：

```python
# 所有这些模式都已修复：
model_dump(by_alias=True)                    → model_dump(by_alias=True, mode='json')
model_dump(exclude_none=True)                → model_dump(exclude_none=True, mode='json')
model_dump(by_alias=True, exclude_none=True) → model_dump(by_alias=True, exclude_none=True, mode='json')
```

## 测试验证

修复后，以下代码现在可以正常工作：

```python
from legnext import Client

client = Client(api_key="your-api-key")

# ✅ blend 接口
response = client.midjourney.blend(
    img_urls=["https://a.com/1.png", "https://b.com/2.png"],
    aspect_ratio="1:1",
    callback="https://webhook.example.com"  # callback 也工作了
)

# ✅ describe 接口
response = client.midjourney.describe(
    img_url="https://example.com/image.png"
)

# ✅ 所有接口的 callback 参数
response = client.midjourney.diffusion(
    text="a sunset",
    callback="https://webhook.example.com"
)
```

## 技术细节

### 序列化对比

**修复前：**
```python
>>> request = BlendRequest(img_urls=["https://a.com/1.png"])
>>> request.model_dump(by_alias=True)
{'imgUrls': [HttpUrl('https://a.com/1.png')], 'aspect_ratio': '1:1', 'callback': None}
# ❌ HttpUrl 对象无法被 JSON 序列化

>>> import json
>>> json.dumps(request.model_dump(by_alias=True))
TypeError: Object of type HttpUrl is not JSON serializable
```

**修复后：**
```python
>>> request.model_dump(by_alias=True, mode='json')
{'imgUrls': ['https://a.com/1.png'], 'aspect_ratio': '1:1', 'callback': None}
# ✅ HttpUrl 已转换为字符串

>>> import json
>>> json.dumps(request.model_dump(by_alias=True, mode='json'))
'{"imgUrls": ["https://a.com/1.png"], "aspect_ratio": "1:1", "callback": null}'
# ✅ 成功序列化
```

## 总结

1. **问题根源：** Pydantic 的 `HttpUrl` 类型不能被标准 JSON 编码器序列化
2. **为什么 blend/describe 最明显：** 它们有必填的 URL 参数，每次调用都触发问题
3. **其他接口：** 所有接口都受影响（通过 callback 参数），但更容易被忽视
4. **解决方案：** 在所有 `model_dump()` 调用中添加 `mode='json'`
5. **影响范围：** 修复了 SDK 中所有 19 个操作的 37 个方法（sync + async）
