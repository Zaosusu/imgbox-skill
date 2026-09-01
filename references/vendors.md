# 各大生图厂商接入速查

核心思路：`openai` provider 是通用入口。只要厂商提供 OpenAI 兼容的
`/images/generations`（可选 `/images/edits`），**填 base-url + model 就能接，不用写新代码**。

```bash
python scripts/cli.py configure --provider openai \
  --base-url "<厂商 base-url>" --update-key

python scripts/cli.py generate "提示词" --provider openai --model "<模型名>"
```

> 一次只配置一个 base-url。要同时用多家，可复制多份配置或临时用环境变量
> `IMAGEGEN_BASE_URL` / `OPENAI_API_KEY` 覆盖。

## 速查表

| 厂商 | base-url | 代表模型 | Key 环境变量 | 来源可信度 |
|---|---|---|---|---|
| OpenAI 官方 | `https://api.openai.com/v1` | `gpt-image-1`、`dall-e-3` | `OPENAI_API_KEY` | 官方 |
| 阿里云百炼（通义万相 / Qwen-Image） | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-image-max`、`wan2.7-image-pro`、`z-image-turbo` | `DASHSCOPE_API_KEY` | 官方文档确认 |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-image`、`cogview-4-250304`、`cogview-4` | `ZHIPUAI_API_KEY` | 多来源交叉验证 |
| 硅基流动 SiliconFlow | `https://api.siliconflow.cn/v1` | `black-forest-labs/FLUX.1-dev`、`stabilityai/stable-diffusion-3-5-medium` | — | 二手来源，**待验证** |
| 火山方舟 Seedream | 走内置 `seedream` provider，无需 base-url | `doubao-seedream-5-0-pro-260628` | `ARK_API_KEY` | 已实跑验证 |
| StepFun | 走内置 `stepfun` provider，无需 base-url | `step-image-edit-2` | `STEPFUN_API_KEY` | 内置 |

## 各家配置示例

### 阿里云百炼（通义万相 / Qwen-Image）

官方提供 OpenAI 兼容入口，这是最省事的路径：

```bash
python scripts/cli.py configure --provider openai \
  --base-url "https://dashscope.aliyuncs.com/compatible-mode/v1" --update-key

python scripts/cli.py generate "水墨风江南水乡" \
  --provider openai --model "qwen-image-max" --size "1024x1024"
```

模型选型（阿里云官方口径）：
- `wan2.7-image-pro`：功能最全，支持组图、最高 4096×4096，文字渲染强
- `qwen-image-max` / `qwen-image-2.0-pro`：擅长文本渲染，适合图表、海报、PPT
- `z-image-turbo`：速度与性价比，擅长高逼真人像与产品图

注意：百炼的原生 REST 接口（`/api/v1/services/aigc/text2image/image-synthesis`）
与 OpenAI 兼容接口是两套，本 skill 走后者。部分万相模型是异步调用，
若超时请用 SKILL.md 里的递增重试策略。

### 智谱 GLM

```bash
python scripts/cli.py configure --provider openai \
  --base-url "https://open.bigmodel.cn/api/paas/v4" --update-key

python scripts/cli.py generate "一只戴墨镜的橘猫" \
  --provider openai --model "glm-image" --size "1280x1280"
```

`glm-image` 默认尺寸 1280×1280，支持 1568×1056 / 1056×1568 等；
`cogview-4` 系列默认 1024×1024。

### 硅基流动（待验证）

```bash
python scripts/cli.py configure --provider openai \
  --base-url "https://api.siliconflow.cn/v1" --update-key

python scripts/cli.py generate "日落沙滩上的橘猫" \
  --provider openai --model "black-forest-labs/FLUX.1-dev"
```

> base-url 来自二手资料，尚未实跑验证。首次使用建议先加 `--dry-run` 确认参数，
> 再真实调用。

## 未收录 / 待补充

- **腾讯混元生图**：未查到公开稳定的 OpenAI 兼容 base-url，暂不收录，避免编造。
- **Midjourney**：无官方 API，需走第三方 relay（风险自担）。
- **百度文心一格、商汤**：需进一步查证其 OpenAI 兼容入口。

新增厂商前，先确认三件事：base-url 是否 OpenAI 兼容、模型名、鉴权头。
未查证的不要写进这张表。
