# Seedream（火山方舟）API 参考

## 接口
- `POST https://ark.cn-beijing.volces.com/api/v3/images/generations`
- 认证: `Authorization: Bearer <ARK_API_KEY>`

## 请求体
- `model`: 接入点 ID（如 `ep-20260901141453-x7wsb`，对应 `doubao-seedream-5-0-pro-260628`）
- `prompt`: 提示词
- `response_format`: `url`
- `size`: 如 `2K` / `1K`
- `stream`: `false`
- `watermark`: `true` / `false`

## 返回
- `data[0].url`: TOS 签名 URL，24h 过期
- `usage.total_tokens`: 出图约 16000+

## 环境变量
- `ARK_API_KEY`: 火山方舟 Key
- `SEEDREAM_ENDPOINT`: 接入点 ID
- `SEEDREAM_OUT_DIR`: 输出目录
