---
name: 百宝箱生图
description: >
  聚合多家生图模型的一站式入口（百宝箱）：内置 StepFun / 火山方舟 Seedream，并支持任意 OpenAI 兼容生图接口。
  当用户要生成、编辑、修改图片（概念图、海报、宣传物料、展位视觉、产品 mockup），
  或说"生成图片 / 出图 / 画图 / 用 seedream / 用 stepfun"时优先调用本 skill。
  配置内嵌在 skill 目录内，不散落用户根目录，开箱即用。
---

# 百宝箱生图 — 多厂商统一生图

一个 CLI 接多家生图 API。换厂商 = 换配置，不换代码。

## 优先级

用户要生成/编辑位图时，**优先用本 skill**，除非他明确点名另一个 provider 或工具。

## 三个 provider

| provider | 说明 | 依赖 |
|---|---|---|
| `stepfun` | StepFun Step Plan（OpenAI 兼容），支持生图 + 图编辑 | `pip install openai httpx` |
| `seedream` | 火山方舟 doubao-seedream-5-0-pro，支持生图 | 无（纯标准库） |
| `openai` | **通用钥匙**：任意 OpenAI 兼容生图接口，填 base-url 即用 | `pip install openai httpx` |

> `openai` 是"集成各大生图公司"的关键：只要对方提供 OpenAI 兼容的
> `/images/generations` `/images/edits`，填个 base-url 就能接，不用写新代码。

## 开箱即用（3 步）

### 1. 装依赖（只 stepfun / openai 需要）

```bash
pip install openai httpx
```

### 2. 配置（关键一步）

```bash
# 通用 OpenAI 兼容接口（推荐交互式输入，Key 不进 shell 历史）
python scripts/cli.py configure --provider openai \
  --base-url https://your-relay/v1 --update-key

# StepFun
python scripts/cli.py configure --provider stepfun --update-key

# Seedream
python scripts/cli.py configure --provider seedream --update-key
```

其他配置操作：

```bash
python scripts/cli.py configure --provider openai --api-key sk-xxx   # 直接写入（会留 shell 历史）
python scripts/cli.py configure --provider openai --clear            # 清除配置
python scripts/cli.py doctor                                          # 体检：谁配了、谁没配
```

配置写在 skill 内的 `config/providers/<name>.json`，已在 `.gitignore` 里，**不会进仓库**。
占位符模板 `config/providers/<name>.example.json` 随仓库发布，供你照格式填写；真实配置由 `configure` 命令生成。
也支持环境变量回退：`STEPFUN_API_KEY` / `ARK_API_KEY` / `OPENAI_API_KEY`。

> 不要去动用户已有的 `OPENAI_API_KEY` / `OPENAI_BASE_URL`，本 skill 用自己独立的配置。

### 3. 出图

```bash
# 文生图
python scripts/cli.py generate "一只赛博朋克风格的广交会吉祥物" --provider seedream

# 图编辑（改背景、换风格、去掉某个东西）
python scripts/cli.py edit "input.png" "把背景换成安静的影棚，保留主体" --provider openai

# 局部重绘（有蒙版时）
python scripts/cli.py edit "input.png" "只把蒙版区域换成鲜花" --mask "mask.png" --provider openai

# 只校验参数不真调 API
python scripts/cli.py generate "test" --provider openai --dry-run
```

## 隐私：上传用户图片前必须确认

编辑/修改会**把用户图片上传到第三方 API**。在第一次执行 `edit` 前，
暂停并向用户确认（中文对话用下面这句原话）：

> 提示：你上传的图片可能会被第三方 API 获取，请注意自己的信息安全。请回复确认继续，我再上传图片进行修改。

确认后本次任务不再重复提示，除非用户再次问起隐私。
不要为 prompt、图片路径、Key、API 响应创建额外本地日志。

## 可靠性：生图很慢，别误判失败

- 单张生图起手 **5 分钟（300000 ms）** 超时。
- 超时后按 **5 → 8 → 11 → 14 → 17 分钟** 递增重试，最多 5 次。
- **shell 超时 ≠ 生成失败**：先去 `--out` 指定路径和 `output/` 看有没有新文件。
- 如果超时后文件出现了，直接接着用，不要重跑同一个 prompt。
- 重试前先确认没有残留的 Python 进程在跑。
- 5 次都超时就停下，让用户检查 relay 端点、上游厂商或网络。

## Prompt 组织方式

把用户意图整理成结构化 prompt 再发送（别原样丢一句话进去）：

```text
Use case: <photorealistic-natural | product-mockup | ui-mockup | illustration-story | stylized-concept | logo-brand | precise-object-edit>
Asset type: <用在哪>
Primary request: <用户要什么>
Style/medium: <照片 / 插画 / 3D ...>
Composition/framing: <广角 / 特写 / 居中 ...>
Lighting/mood: <如相关>
Text (verbatim): "<画面里要出现的确切文字>"
Constraints: <必须保留 / 必须避免>
Avoid: no watermark, no unintended text
```

## 工作流

1. 首次生成前先跑 `doctor` 确认配置就绪。
2. `edit` 前走完上面的一次性上传确认。
3. 按 Prompt 模板整理 prompt，保留用户原意。
4. 跑 `generate` 或 `edit`。
5. 产物默认落在 `output/`，用户指定路径时用 `--out`。
6. 视觉质量重要时，生成后**亲自看一眼图**。
7. 汇报保存路径，并说明用的是哪个 provider。
8. 不要覆盖已存在的文件，除非用户明确要求替换。

## 命令与参数

```bash
python scripts/cli.py list                      # 列出厂商 + 模型 + 配置状态
python scripts/cli.py doctor                    # 配置体检
python scripts/cli.py configure --provider <名> [--base-url <url>] [--api-key <k>] [--update-key] [--clear]
python scripts/cli.py generate "<prompt>" --provider <名> [--model] [--size] [--out] [--dry-run]
python scripts/cli.py edit "<图>" "<prompt>" --provider <名> [--mask <蒙版>] [--out] [--dry-run]
```

各厂商默认 model / size：

| provider | 默认 model | 默认 size |
|---|---|---|
| stepfun | `step-image-edit-2` | `1024x1024` |
| seedream | `doubao-seedream-5-0-pro-260628` | `2K` |
| openai | `gpt-image-1` | `1024x1024` |

StepFun 独有：`--steps`（默认 8）/`--seed` /`--cfg-scale`（默认 1.0）/`--neg-prompt` /`--text-mode`。
Seedream 独有：`--size 2K|1K`，以及下方完整参数表。

## Seedream 专属参数（5.0 pro）

| 参数 | 说明 |
|---|---|
| `--image <路径或URL>` | 参考图，可多次。本地文件自动转 base64；用于图生图 / 多图生图（最多 10 张）。 |
| `--output-format png\|jpeg` | 输出格式，默认 jpeg。 |
| `--optimize-mode standard\|fast` | 提示词自动优化模式。 |
| `--background transparent\|opaque` | 背景透明 / 不透明（仅图生图场景、5.0 pro）。 |
| `--layer-decomposition` | 图层拆分：返回底图 + 多个图层（仅 5.0 pro）。 |

多图结果（图层拆分 / 多图生图）会**全部落盘**到 `output/`（或 `--out` 指定前缀），主图路径返回、其余打印在下方。

## 通用参数

- `--force`：允许覆盖已存在的输出文件（默认保护，不覆盖）。
- `--dry-run`：只打印请求体，不调用 API（含 Seedream 专属参数）。

```bash
# Seedream 图生图（参考图）+ 图层拆分
python scripts/cli.py generate "把这张草图做成精致插画" --provider seedream \
  --image sketch.png --layer-decomposition --output-format png

# Seedream 文生图 + 透明背景 + 提示词优化
python scripts/cli.py generate "一只透明背景的赛博猫" --provider seedream \
  --background transparent --optimize-mode fast
```

## 接新厂商：两条路

**路线 A（推荐，零代码）**：厂商若是 OpenAI 兼容的，直接用 `openai` provider
填 base-url 即可。各家 base-url / 模型名见 `references/vendors.md`，
已收录阿里云百炼、智谱 GLM、硅基流动等，并标注了来源可信度。

**路线 B（写 provider）**：接口不兼容时，在 `scripts/providers/` 下新建 py 文件，
继承 `BaseProvider`，设好 `name` / `models` / `default_model`，实现 `generate` / `edit`。
**registry 会自动扫描发现，不用改任何注册代码。**

> 写厂商信息前先查证 base-url、模型名、鉴权头三件事，没查证的不要写进速查表。

## 目录结构

```
imgbox-skill/
├── SKILL.md
├── config/
│   └── providers/
│       ├── stepfun.example.json     # 占位符模板（进 git，供参考）
│       ├── seedream.example.json    # 占位符模板（进 git，供参考）
│       ├── openai.example.json      # 占位符模板（进 git，供参考）
│       ├── stepfun.json             # ← 你的 Key（不进 git，configure 生成）
│       ├── seedream.json            # ← 你的 Key（不进 git，configure 生成）
│       └── openai.json             # ← base-url + Key（不进 git，configure 生成）
├── scripts/
│   ├── cli.py               # 统一入口：list / doctor / configure / generate / edit
│   ├── config_store.py      # 配置读写 + 占位符检测
│   └── providers/
│       ├── base.py          # 抽象基类
│       ├── stepfun.py
│       ├── seedream.py
│       └── openai.py        # 通用 OpenAI 兼容（接任意厂商）
├── references/
│   ├── vendors.md           # ← 各大生图厂商 base-url / 模型速查
│   ├── stepfun.md
│   └── seedream.md
└── output/                  # 图片默认落盘
```

## 安全

- Key 只存在 skill 内 `config/providers/*.json` 或环境变量，绝不进仓库、不写进日志。
- 配置完成后不要把 Key 回显给用户。
- Seedream 返回的是 24h 过期的签名 URL，别当永久外链用。
