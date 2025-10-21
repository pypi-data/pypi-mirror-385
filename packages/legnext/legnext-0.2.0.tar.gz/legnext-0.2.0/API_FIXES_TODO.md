# API Parameters Fix TODO

本文档列出所有需要修复的API接口，以匹配实际的Legnext API规范。

## 进度追踪

- ✅ 已完成
- 🟡 进行中
- ⏳ 待完成

## 状态总览

| 接口 | Request Model | Sync Method | Async Method | README | Examples |
|------|--------------|-------------|--------------|---------|----------|
| diffusion | ✅ | ✅ | ✅ | ✅ | ✅ |
| variation | ✅ | ✅ | ✅ | ✅ | ✅ |
| upscale | ✅ | ✅ | ✅ | ✅ | ✅ |
| reroll | ✅ | ✅ | ✅ | ✅ | ✅ |
| blend | ✅ | ✅ | ⏳ | ⏳ | ⏳ |
| describe | ✅ | ✅ | ⏳ | ⏳ | ⏳ |
| shorten | ✅ | ✅ | ✅ | ✅ | ✅ |
| pan | ✅ | ✅ | ⏳ | ⏳ | ⏳ |
| outpaint | ✅ | ✅ | ⏳ | ⏳ | ⏳ |
| inpaint | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| remix | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| edit | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| upload_paint | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| retexture | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| remove_background | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| enhance | ✅ | ✅ | ✅ | ✅ | ✅ |
| video_diffusion | ✅ | ✅ | ✅ | ✅ | ✅ |
| extend_video | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| video_upscale | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |

---

## 1. Inpaint (⏳)

### Request Model (✅ 已完成)
```python
class InpaintRequest(BaseModel):
    job_id: str = Field(..., alias="jobId")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3)
    mask: Any  # Mask object
    remix_prompt: Optional[str] = Field(None, alias="remixPrompt")
    callback: Optional[HttpUrl] = None
```

### Sync Method 需要修改
**当前签名**:
```python
def inpaint(self, job_id: str, image_no: int, mask: bytes, prompt: str, callback=None)
```

**应改为**:
```python
def inpaint(
    self,
    job_id: str,
    image_no: int,
    mask: dict,  # Mask object: {areas?: Polygon[], url?: str}
    remix_prompt: Optional[str] = None,
    callback: Union[HttpUrl, str, None] = None
) -> TaskResponse:
```

### Async Method 需要同样修改

### README 需要更新示例

---

## 2. Remix (⏳)

### Request Model (✅ 已完成)
```python
class RemixRequest(BaseModel):
    job_id: str = Field(..., alias="jobId")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3)
    remix_prompt: str = Field(..., alias="remixPrompt")  # 必填
    mode: Optional[int] = Field(None, ge=0, le=1)  # 0 or 1
    callback: Optional[HttpUrl] = None
```

### Sync Method 需要修改
**当前签名**:
```python
def remix(self, job_id: str, image_no: int, prompt: str, intensity: Optional[float] = None, callback=None)
```

**应改为**:
```python
def remix(
    self,
    job_id: str,
    image_no: int,
    remix_prompt: str,
    mode: Optional[int] = None,  # 0 or 1, not float
    callback: Union[HttpUrl, str, None] = None
) -> TaskResponse:
```

### Async Method 需要同样修改

### README 需要更新
- 参数名: `prompt` → `remix_prompt`
- 参数类型: `intensity` (float 0-1) → `mode` (int 0 or 1)

---

## 3. Edit (⏳) - 复杂结构

### Request Model (✅ 已完成)
```python
class EditRequest(BaseModel):
    job_id: str = Field(..., alias="jobId")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3)
    canvas: Any  # Canvas object: {width: int, height: int}
    img_pos: Any = Field(..., alias="imgPos")  # CanvasImg: {width, height, x, y}
    remix_prompt: str = Field(..., alias="remixPrompt")
    mask: Optional[Any] = None  # Mask object
    callback: Optional[HttpUrl] = None
```

### Sync Method 需要完全重写
**当前签名**:
```python
def edit(self, job_id: str, image_no: int, prompt: str, callback=None)
```

**应改为**:
```python
def edit(
    self,
    job_id: str,
    image_no: int,
    canvas: dict,  # {width: int, height: int}
    img_pos: dict,  # {width: int, height: int, x: int, y: int}
    remix_prompt: str,
    mask: Optional[dict] = None,  # {areas?: Polygon[], url?: str}
    callback: Union[HttpUrl, str, None] = None
) -> TaskResponse:
```

### 数据结构说明
```python
# Canvas
{
    "width": 1024,    # Canvas width in pixels
    "height": 1024    # Canvas height in pixels
}

# CanvasImg
{
    "width": 512,     # Image width in pixels
    "height": 512,    # Image height in pixels
    "x": 256,         # Horizontal offset from canvas top-left
    "y": 256          # Vertical offset from canvas top-left
}

# Mask
{
    "areas": [        # Optional: Polygonal areas
        {
            "width": 512,
            "height": 512,
            "points": [x1, y1, x2, y2, x3, y3, x4, y4]  # Clockwise from top-left
        }
    ],
    "url": "https://..."  # Optional: Black and white mask image URL
}
```

### Async Method 需要同样修改

### README 需要详细示例
```python
response = client.midjourney.edit(
    job_id="original-job-id",
    image_no=0,
    canvas={"width": 1024, "height": 1024},
    img_pos={"width": 512, "height": 512, "x": 256, "y": 256},
    remix_prompt="change the sky to sunset",
    mask={
        "areas": [{
            "width": 512,
            "height": 512,
            "points": [0, 0, 512, 0, 512, 256, 0, 256]  # Top half
        }]
    }
)
```

---

## 4. Upload Paint (⏳) - 复杂结构

### Request Model (✅ 已完成)
```python
class UploadPaintRequest(BaseModel):
    img_url: HttpUrl = Field(..., alias="imgUrl", max_length=1024)
    canvas: Any  # Canvas object
    img_pos: Any = Field(..., alias="imgPos")  # CanvasImg object
    remix_prompt: str = Field(..., alias="remixPrompt")
    mask: Any  # Mask object (required)
    callback: Optional[HttpUrl] = None
```

### Sync Method 需要完全重写
**当前签名**:
```python
def upload_paint(self, image: bytes, prompt: str, x: Optional[float] = None, y: Optional[float] = None, callback=None)
```

**应改为**:
```python
def upload_paint(
    self,
    img_url: Union[HttpUrl, str],
    canvas: dict,  # {width: int, height: int}
    img_pos: dict,  # {width: int, height: int, x: int, y: int}
    remix_prompt: str,
    mask: dict,  # {areas?: Polygon[], url?: str} - Required!
    callback: Union[HttpUrl, str, None] = None
) -> TaskResponse:
```

### 关键变化
- ❌ 删除 `image: bytes` 参数
- ❌ 删除 `x`, `y` 参数
- ✅ 添加 `img_url: str` - 图片URL
- ✅ 添加 `canvas: dict` - 画布尺寸
- ✅ 添加 `img_pos: dict` - 图片位置和尺寸
- ✅ `mask` 现在是必填参数

### Async Method 需要同样修改

### README 需要详细示例
```python
response = client.midjourney.upload_paint(
    img_url="https://example.com/image.jpg",
    canvas={"width": 1024, "height": 1024},
    img_pos={"width": 800, "height": 800, "x": 112, "y": 112},
    remix_prompt="add magical sparkles",
    mask={
        "url": "https://example.com/mask.png"  # Black and white mask
    }
)
```

---

## 5. Retexture (⏳)

### Request Model (✅ 已完成)
```python
class RetextureRequest(BaseModel):
    img_url: HttpUrl = Field(..., alias="imgUrl", max_length=1024)
    remix_prompt: str = Field(..., alias="remixPrompt")
    callback: Optional[HttpUrl] = None
```

### Sync Method 需要修改
**当前签名**:
```python
def retexture(self, job_id: str, image_no: int, prompt: str, callback=None)
```

**应改为**:
```python
def retexture(
    self,
    img_url: Union[HttpUrl, str],
    remix_prompt: str,
    callback: Union[HttpUrl, str, None] = None
) -> TaskResponse:
```

### 关键变化
- ❌ 删除 `job_id`, `image_no` 参数
- ✅ 改为 `img_url` - 直接使用图片URL
- ✅ `prompt` → `remix_prompt`

### Async Method 需要同样修改

### README 需要更新示例
```python
response = client.midjourney.retexture(
    img_url="https://example.com/image.jpg",
    remix_prompt="metallic and shiny surfaces"
)
```

---

## 6. Remove Background (⏳)

### Request Model (✅ 已完成)
```python
class RemoveBackgroundRequest(BaseModel):
    img_url: HttpUrl = Field(..., alias="imgUrl", max_length=1024)
    callback: Optional[HttpUrl] = None
```

### Sync Method 需要修改
**当前签名**:
```python
def remove_background(self, job_id: str, image_no: int, callback=None)
```

**应改为**:
```python
def remove_background(
    self,
    img_url: Union[HttpUrl, str],
    callback: Union[HttpUrl, str, None] = None
) -> TaskResponse:
```

### 关键变化
- ❌ 删除 `job_id`, `image_no` 参数
- ✅ 改为 `img_url` - 直接使用图片URL

### Async Method 需要同样修改

### README 需要更新示例
```python
response = client.midjourney.remove_background(
    img_url="https://example.com/image.jpg"
)
```

---

## 7. Extend Video (⏳)

### Request Model (✅ 已完成)
```python
class ExtendVideoRequest(BaseModel):
    job_id: str = Field(..., alias="jobId")
    video_no: int = Field(..., alias="videoNo", ge=0, le=3)  # 新增！
    prompt: Optional[str] = Field(None, min_length=1, max_length=8192)  # 新增！
    callback: Optional[HttpUrl] = None
```

### Sync Method 需要修改
**当前签名**:
```python
def extend_video(self, job_id: str, callback=None)
```

**应改为**:
```python
def extend_video(
    self,
    job_id: str,
    video_no: int,
    prompt: Optional[str] = None,
    callback: Union[HttpUrl, str, None] = None
) -> TaskResponse:
```

### 关键变化
- ✅ 添加 `video_no` (int, required, 0-3) - 视频编号
- ✅ 添加 `prompt` (str, optional) - 引导提示词

### Async Method 需要同样修改

### README 需要更新示例
```python
response = client.midjourney.extend_video(
    job_id="original-video-job-id",
    video_no=0,                    # 视频编号 (0-3)
    prompt="continue with more clouds"  # Optional
)
```

---

## 8. Video Upscale (⏳)

### Request Model (✅ 已完成)
```python
class VideoUpscaleRequest(BaseModel):
    job_id: str = Field(..., alias="jobId")
    video_no: int = Field(..., alias="videoNo", ge=0, le=3)  # 新增！
    callback: Optional[HttpUrl] = None
```

### Sync Method 需要修改
**当前签名**:
```python
def video_upscale(self, job_id: str, callback=none)
```

**应改为**:
```python
def video_upscale(
    self,
    job_id: str,
    video_no: int,
    callback: Union[HttpUrl, str, None] = None
) -> TaskResponse:
```

### 关键变化
- ✅ 添加 `video_no` (int, required, 0-3) - 视频编号

### Async Method 需要同样修改

### README 需要更新示例
```python
response = client.midjourney.video_upscale(
    job_id="original-video-job-id",
    video_no=0                     # 视频编号 (0-3)
)
```

---

## 需要创建的类型定义

建议在 `src/legnext/types/shared.py` 或新建 `src/legnext/types/canvas.py`:

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class Canvas(BaseModel):
    """Canvas dimensions."""
    width: int = Field(..., description="Canvas width in pixels")
    height: int = Field(..., description="Canvas height in pixels")

class CanvasImg(BaseModel):
    """Image position and size on canvas."""
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    x: int = Field(..., description="Horizontal offset from canvas top-left")
    y: int = Field(..., description="Vertical offset from canvas top-left")

class Polygon(BaseModel):
    """Polygon area definition."""
    width: int = Field(..., ge=500, le=4096, description="Image width in pixels")
    height: int = Field(..., ge=500, le=4096, description="Image height in pixels")
    points: List[int] = Field(..., description="XYXY coordinates, clockwise from top-left")

class Mask(BaseModel):
    """Mask definition for editing operations."""
    areas: Optional[List[Polygon]] = Field(None, description="Polygonal areas")
    url: Optional[str] = Field(None, description="Black and white mask image URL")
```

---

## 测试检查清单

修复完成后，需要验证：

### 1. Request Models
- [ ] 所有字段名使用alias匹配API (camelCase)
- [ ] 所有必填/可选参数正确
- [ ] 字段验证规则正确 (ge, le, min_length, max_length)

### 2. Resource Methods (Sync)
- [ ] 方法签名匹配Request Model
- [ ] 使用 `by_alias=True` 序列化
- [ ] 文档字符串准确

### 3. Resource Methods (Async)
- [ ] 与sync版本保持一致
- [ ] 使用await调用

### 4. README.md
- [ ] 所有19个方法有示例
- [ ] 参数说明准确
- [ ] 复杂结构有详细示例

### 5. Examples
- [ ] 示例代码可运行
- [ ] 使用正确的参数名和类型

### 6. Tests
- [ ] 更新test fixtures
- [ ] 测试新参数验证
- [ ] 测试复杂嵌套结构

---

## 优先级建议

**高优先级** (常用接口):
1. ✅ diffusion, variation, upscale, reroll
2. 🟡 blend, describe, pan, outpaint
3. ⏳ remix, enhance

**中优先级** (专业功能):
4. ⏳ inpaint, retexture, remove_background
5. ⏳ video_diffusion, extend_video, video_upscale

**低优先级** (复杂/少用):
6. ⏳ edit, upload_paint, shorten

---

## 下一步行动

1. **继续修复同步方法** (inpaint → video_upscale)
2. **修复所有异步方法** (保持与同步一致)
3. **更新README** (所有方法示例)
4. **更新examples/** (特别是复杂接口)
5. **运行测试** 验证所有修改
6. **更新CHANGELOG** 记录breaking changes
7. **发布v0.1.7** (包含所有API修复)
