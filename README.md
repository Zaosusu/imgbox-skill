# 百宝箱生图 (imgbox-skill)

一个 CLI 接多家生图 API + 本地 AI 抠图，开箱即用。换厂商 = 换配置，不换代码。

## 功能一览

| 能力 | 说明 |
|------|------|
| **文生图** | StepFun / Seedream / 任意 OpenAI 兼容接口 |
| **图编辑** | 改背景、换风格、局部重绘 |
| **AI 抠图** | U²-Net 本地运行，生图后可选自动抠图，输出透明 PNG |
| **默认无水印** | Seedream 默认关闭「AI生成」水印 |

## 快速开始

```bash
pip install -r requirements.txt

# 配置（以 Seedream 为例）
python scripts/cli.py configure --provider seedream --update-key

# 文生图
python scripts/cli.py generate "一只赛博朋克风格的广交会吉祥物" --provider seedream

# 生图 + 自动抠图（一条命令出透明 PNG）
python scripts/cli.py generate "一只广交会吉祥物" --provider seedream --removebg

# 单独抠图
python scripts/cli.py removebg photo.png --out photo_nobg.png
```

## Provider

| provider | 说明 | 依赖 |
|----------|------|------|
| `stepfun` | StepFun Step Plan（OpenAI 兼容），生图 + 图编辑 | `pip install openai httpx` |
| `seedream` | 火山方舟 doubao-seedream-5-0-pro，零依赖 | 无 |
| `openai` | 任意 OpenAI 兼容生图接口，填 base-url 即用 | `pip install openai httpx` |
| `removebg` | U²-Net 本地抠图，输出透明 PNG | `pip install rembg onnxruntime pillow` |

## 生图后可选抠图

生图完成后，三档可选：

1. **显式 flag**：`generate ... --removebg` → 自动对结果抠图，输出 `<原名>_nobg.png`
2. **终端询问**：TTY 里跑 generate 会问「是否去除背景？[y/N]」
3. **非交互提示**：打印抠图命令供手动执行

抠图本地运行，不消耗 API、不上传图片、无额外费用。

## 水印控制

Seedream 默认**无水印**输出。如需平台水印：

```bash
python scripts/cli.py generate "..." --provider seedream --watermark
```

## 常用命令

```bash
python scripts/cli.py list                          # 列出可用 provider
python scripts/cli.py doctor                        # 体检：谁配了、谁没配
python scripts/cli.py generate "<prompt>" --provider <名> [--size] [--out] [--removebg]
python scripts/cli.py edit <图片> "<指令>" --provider <名> [--mask]
python scripts/cli.py removebg <图片> [--out] [--model u2netp]
```

详细文档见 [SKILL.md](SKILL.md)。

## License

MIT
