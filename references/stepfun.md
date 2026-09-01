# StepFun Step Plan API 参考

## 接口
- Base URL: `https://api.stepfun.com/step_plan/v1`
- 认证: `Authorization: Bearer <STEPFUN_API_KEY>`

## 文生图
`POST /images/generations`

关键字段：
- `model`: `step-image-edit-2`（推荐）/ `step-2x-large` / `step-1x-medium`
- `prompt`: 最大 512 字符
- `size`: `1024x1024` / `768x1360` / `896x1184` / `1360x768` / `1184x896`（step-image-edit-2）
- `n`: 当前仅支持 1
- `response_format`: `url` / `b64_json`

Extra body：
- `steps`: 1-50，step-image-edit-2 默认 8，其他默认 50
- `cfg_scale`: 1.0-10.0，step-image-edit-2 默认 1.0，step-2x-large 默认 6.0，step-1x-medium 默认 7.5
- `seed`: 0-2147483647（step-image-edit-2）
- `negative_prompt`: 最大 512 字符（仅 step-image-edit-2）
- `text_mode`: boolean（仅 step-image-edit-2）
- `style_reference`: `{ "source_url": "...", "weight": 1.0 }`（仅 step-1x-medium）

## 图编辑
`POST /images/edits`

- `model`: 当前仅 `step-image-edit-2`
- `image`: 二进制图片文件
- `prompt`: 编辑指令
- `response_format`: 默认 `b64_json`

## 限流
图像生成产品线独立限流（额度/张数），与 ASR / LLM 不同。
