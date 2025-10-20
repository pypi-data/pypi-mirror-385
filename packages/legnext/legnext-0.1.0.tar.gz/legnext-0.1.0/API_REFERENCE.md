# Legnext SDK API 参考

## 设计原则

**直接映射 API Endpoints**

所有方法名和参数直接对应 Legnext API 规范，避免额外的抽象层和概念映射。

- ✅ 方法名 = API endpoint 名称
- ✅ 参数名和类型 = API 规范定义
- ✅ 统一的命名空间 `client.midjourney.*`

## 客户端初始化

```python
from legnext import Client

client = Client(
    api_key="your-api-key",
    base_url=None,  # 可选：自定义 API 地址
    timeout=60.0,   # 请求超时（秒）
    max_retries=3   # 最大重试次数
)
```

## API Endpoints

### 图片生成 (Image Generation)

#### POST /diffusion - 文本生成图片

```python
response = client.midjourney.diffusion(
    text="a beautiful sunset",  # 文本提示词 (1-8192字符)
    callback=None               # 可选：webhook 回调 URL
) -> TaskResponse
```

#### POST /variation - 创建图片变体

```python
variation = client.midjourney.variation(
    job_id="...",      # 原始任务 ID
    image_no=0,        # 图片编号 (0-3)
    type=0,            # 变体类型: 0=微妙, 1=强烈
    remix_prompt=None, # 可选：remix 提示词
    callback=None
) -> TaskResponse
```

#### POST /upscale - 放大图片

```python
upscale = client.midjourney.upscale(
    job_id="...",
    image_no=0,
    type=1,      # 放大类型: 0=微妙, 1=创意
    callback=None
) -> TaskResponse
```

#### POST /reroll - 重新生成

```python
reroll = client.midjourney.reroll(
    job_id="...",   # 要重新生成的任务 ID
    callback=None
) -> TaskResponse
```

#### POST /blend - 混合图片

```python
blend = client.midjourney.blend(
    image_urls=[     # 2-5 个图片 URL
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg"
    ],
    callback=None
) -> TaskResponse
```

#### POST /describe - 图片描述

```python
describe = client.midjourney.describe(
    image_url="https://example.com/image.jpg",
    callback=None
) -> TaskResponse
```

#### POST /shorten - 简化提示词

```python
shorten = client.midjourney.shorten(
    prompt="a very long and detailed prompt...",
    callback=None
) -> TaskResponse
```

#### POST /pan - 定向扩展

```python
pan = client.midjourney.pan(
    job_id="...",
    image_no=0,
    direction="left",  # 方向: left, right, up, down
    callback=None
) -> TaskResponse
```

#### POST /outpaint - 全向扩展

```python
outpaint = client.midjourney.outpaint(
    job_id="...",
    image_no=0,
    callback=None
) -> TaskResponse
```

#### POST /inpaint - 区域修改

```python
with open("mask.png", "rb") as f:
    inpaint = client.midjourney.inpaint(
        job_id="...",
        image_no=0,
        mask=f,  # PNG 格式的遮罩图片
        prompt="add mountains",
        callback=None
    ) -> TaskResponse
```

#### POST /remix - 重新混合

```python
remix = client.midjourney.remix(
    job_id="...",
    image_no=0,
    prompt="same scene but in anime style",
    intensity=0.7,  # 可选：混合强度 (0-1)
    callback=None
) -> TaskResponse
```

#### POST /edit - 编辑区域

```python
edit = client.midjourney.edit(
    job_id="...",
    image_no=0,
    prompt="add a garden",
    callback=None
) -> TaskResponse
```

#### POST /upload-paint - 高级编辑

```python
with open("image.jpg", "rb") as f:
    upload_paint = client.midjourney.upload_paint(
        image=f,
        prompt="editing instructions",
        x=None,  # 可选：X 坐标
        y=None,  # 可选：Y 坐标
        callback=None
    ) -> TaskResponse
```

#### POST /retexture - 纹理变换

```python
retexture = client.midjourney.retexture(
    job_id="...",
    image_no=0,
    prompt="marble texture",
    callback=None
) -> TaskResponse
```

#### POST /remove-background - 移除背景

```python
remove_bg = client.midjourney.remove_background(
    job_id="...",
    image_no=0,
    callback=None
) -> TaskResponse
```

#### POST /enhance - 增强质量

```python
enhance = client.midjourney.enhance(
    job_id="...",  # 需要使用 --v7 --draft 生成的图片
    image_no=0,
    callback=None
) -> TaskResponse
```

### 视频生成 (Video Generation)

#### POST /video-diffusion - 生成视频

```python
# 从文本生成
video = client.midjourney.video_diffusion(
    prompt="a serene landscape",
    image_url=None,
    duration=None,
    callback=None
) -> TaskResponse

# 从图片生成
video = client.midjourney.video_diffusion(
    prompt=None,
    image_url="https://example.com/image.jpg",
    duration=5,  # 秒
    callback=None
) -> TaskResponse
```

#### POST /extend-video - 延长视频

```python
extend = client.midjourney.extend_video(
    job_id="...",  # 原始视频任务 ID
    callback=None
) -> TaskResponse
```

#### POST /video-upscale - 视频放大

```python
upscale = client.midjourney.video_upscale(
    job_id="...",
    callback=None
) -> TaskResponse
```

### 任务管理 (Task Management)

#### GET /job/{job_id} - 查询任务状态

```python
task = client.tasks.get(
    job_id="..."
) -> TaskResponse
```

#### 等待任务完成

```python
result = client.tasks.wait_for_completion(
    job_id="...",
    timeout=300.0,      # 超时时间（秒）
    poll_interval=3.0,  # 轮询间隔（秒）
    on_progress=None    # 可选：进度回调函数
) -> TaskResponse
```

### 账户管理 (Account)

#### GET /account/info - 账户信息

```python
info = client.account.get_info() -> AccountInfo
```

#### GET /account/active_tasks - 活跃任务

```python
active = client.account.get_active_tasks() -> ActiveTasksResponse
```

## 响应类型

### TaskResponse

```python
class TaskResponse:
    job_id: str              # 任务 ID
    model: str               # 使用的模型
    task_type: TaskType      # 任务类型
    status: JobStatus        # 状态: pending, processing, completed, failed
    output: ImageOutput      # 输出结果（完成后）
    meta: Meta               # 元数据（时间、用量等）
    error: Error             # 错误信息（失败时）
```

### JobStatus (枚举)

- `pending` - 等待中
- `staged` - 已排队
- `processing` - 处理中
- `completed` - 已完成
- `failed` - 失败

### TaskType (枚举)

- `diffusion` - 文本生成图片
- `variation` - 变体
- `upscale` - 放大
- `reroll` - 重新生成
- `blend` - 混合
- `describe` - 描述
- `shorten` - 简化
- `pan` - 定向扩展
- `outpaint` - 全向扩展
- `inpaint` - 区域修改
- `remix` - 重新混合
- `edit` - 编辑
- `upload-paint` - 高级编辑
- `retexture` - 纹理变换
- `remove-background` - 移除背景
- `enhance` - 增强
- `video-diffusion` - 视频生成
- `extend-video` - 延长视频
- `video-upscale` - 视频放大

## 异步客户端

所有方法都有对应的异步版本：

```python
import asyncio
from legnext import AsyncClient

async def main():
    async with AsyncClient(api_key="your-api-key") as client:
        response = await client.midjourney.diffusion(text="a sunset")
        result = await client.tasks.wait_for_completion(response.job_id)
        print(result.output.image_urls)

asyncio.run(main())
```

## Webhook 处理

```python
from legnext.webhook import WebhookHandler

handler = WebhookHandler(webhook_secret="your-secret")

@handler.on_completed
def handle_completed(task):
    print(f"任务完成: {task.job_id}")
    print(f"结果: {task.output.image_urls}")

@handler.on_failed
def handle_failed(task):
    print(f"任务失败: {task.error.message}")

# 在你的 webhook endpoint 中
handler.handle(
    payload=request.body,
    signature=request.headers["X-Legnext-Signature"]
)
```

## 错误处理

```python
from legnext import Client, LegnextAPIError, RateLimitError

client = Client(api_key="your-key")

try:
    response = client.midjourney.diffusion(text="a sunset")
except RateLimitError as e:
    print(f"请求过于频繁: {e.message}")
except LegnextAPIError as e:
    print(f"API 错误: {e.message} (状态码: {e.status_code})")
```

## 完整示例

```python
from legnext import Client

client = Client(api_key="your-api-key")

# 1. 生成图片
response = client.midjourney.diffusion(
    text="a futuristic cityscape, cyberpunk style"
)

# 2. 等待完成
def show_progress(task):
    print(f"状态: {task.status}")

result = client.tasks.wait_for_completion(
    response.job_id,
    on_progress=show_progress
)

# 3. 获取结果
print(f"生成了 {len(result.output.image_urls)} 张图片:")
for i, url in enumerate(result.output.image_urls):
    print(f"  图片 {i+1}: {url}")

# 4. 创建变体
variation = client.midjourney.variation(
    job_id=result.job_id,
    image_no=0,  # 选择第一张图片
    type=1       # 强烈变体
)
variation_result = client.tasks.wait_for_completion(variation.job_id)
print(f"变体: {variation_result.output.image_url}")

# 5. 放大
upscale = client.midjourney.upscale(
    job_id=result.job_id,
    image_no=1,  # 选择第二张图片
    type=1       # 创意放大
)
upscale_result = client.tasks.wait_for_completion(upscale.job_id)
print(f"放大: {upscale_result.output.image_url}")
```

## 参数对照表

| Python 参数 | API 参数 | OpenAPI 规范 |
|------------|---------|-------------|
| `text` | `text` | DiffusionRequest.text |
| `job_id` | `jobId` | *.jobId |
| `image_no` | `imageNo` | *.imageNo |
| `type` | `type` | *.type |
| `remix_prompt` | `remixPrompt` | VariationRequest.remixPrompt |
| `image_url` | `imageUrl` | *.imageUrl |
| `image_urls` | `imageUrls` | BlendRequest.imageUrls |

所有参数名在 SDK 中使用 snake_case（Python 惯例），但会自动转换为 API 所需的 camelCase 格式。
