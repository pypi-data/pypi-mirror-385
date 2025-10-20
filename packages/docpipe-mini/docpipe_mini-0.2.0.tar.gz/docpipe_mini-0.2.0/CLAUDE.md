```markdown
# CLAUDE.md – Protocol-oriented mixin design 版

This file provides guidance to Claude Code (claude.ai/code) when working with **docpipe** – a *protocol-oriented*, **zero-dependency**, **typed** document-to-jsonl serializer.

Goal: 5 MB install, 300 ms/MB, zero model, zero OCR, **just give AI clean text with coordinates**.

---

## 1. 设计哲学（Protocol-oriented mixin design）

- **能力 → Protocol**  
  任何行为（加载、格式化、日志、内存保护）先声明为 `typing.Protocol`，**不关心继承，只关心结构**。

- **复用 → Mixin**  
  给每个 Protocol 提供一份 **零依赖、可多继承** 的 `Mixin` 类，**默认实现**即可用，**随时被替换**。

- **组合 > 继承**  
  新功能？先写 `ProcessorProto[In, Out]` 实现，再 `entry-point` 注册；**绝不 deep-subclass**。

---

## 2. 核心协议一览（src/docpipe/_protocols.py）

| Protocol | 能力摘要 | 默认 Mixin | 备注 |
|----------|----------|------------|------|
| `LoaderProto[StreamT]` | 文件 → `StreamT` | `LoaderMixin` | 内存守护由 `MemoryGuardProto` 自动注入 |
| `ProcessorProto[In, Out]` | 流式转换 | `ProcessorMixin` | 自带 `__enter__/__exit__` 生命周期 |
| `FormatterProto[StreamT]` | `StreamT` → `bytes` | `JsonlFormatterMixin` | 统一落盘为 JSONL |
| `MemoryGuardProto` | RSS 超限杀进程 | `MemoryGuardMixin` | 子进程 + `psutil.RSS` |
| `LogMixinProto` | 结构化日志 | `LogMixin` | stderr 输出，`-O` 静默 |
| `SerializerProto` | 序列化配置 | `SerializerMixin` | header/RAG/内存限幅 |

> 所有 Protocol 均 `@runtime_checkable`，**运行时鸭子类型** + **mypy strict** 双通过。

---

## 3. 数据流（ typed streams ）

```
file_path
   ▼
LoaderProto[PageStream]  ─► ProcessorProto[PageStream, BlockStream]  ─► FormatterProto  ─►  bytes (JSONL)
   ▲                                                                    ▲
   │                    memory guard via subprocess                     │
   └────────────────────────── MemoryGuardProto ────────────────────────┘
```

- 每阶段 **只** 通过 `Protocol` 消费/产出 **TypedStream**（见 `_types.py`）。
- 任意阶段可 **热插拔**：实现 Protocol → entry-point 注册 → 完成。

---

## 4. 最小用户旅程（零依赖路径）

```bash
uv add docpipe-mini            # 5 MB
python -m docpipe-mini paper.pdf > paper.jsonl
```

```python
import docpipe_mini as dp
for chunk in dp.serialize("paper.pdf"):
    print(chunk.to_jsonl())    # 已含 bbox + text
```

---

## 5. 如何新增一个格式（插件示例）

1. 实现 Protocol  
```python
class MyLoader(LoaderProto[PageStream], LoaderMixin, LogMixin):
    def can_serialize(self, path: Path) -> bool: ...
    def serialize(self, path: Path) -> Iterator[PageStream]: ...
```

2. 注册 entry-point（pyproject.toml）
```toml
[project.entry-points."docpipe.loader"]
my = "my_plugin:MyLoader"
```

3. 发布 wheel → 用户 `uv add my-plugin` 即可自动识别。

---

## 6. 目录布局（protocol-first）

```
src/docpipe/
├── _types.py          # TypedStream + DocumentChunk
├── _protocols.py      # 所有 Protocol 定义（零实现）
├── _mixins.py         # 默认 Mixin 实现（零依赖）
├── pipeline.py        # 唯一入口：pipeline(src, *, loader, processor, fmt)
├── loaders/
│   ├── _pdfium.py     # 满足 LoaderProto + LoaderMixin
│   └── _pymupdf.py    # 同上，但依赖 AGPL
├── formatters/
│   └── _jsonl.py      # 满足 FormatterProto + JsonlFormatterMixin
└── cli/
    └── _typer.py      # optional CLI
```

---

## 7. 开发守则（coding rules）

| 规则 | 说明 |
|------|------|
| **Protocol 先行** | 先写 `Protocol`，再写 `Mixin`，最后写具体类。 |
| **零依赖默认** | core wheel 仅依赖 stdlib；任何第三方依赖必须放到 **extras**。 |
| **组合 > 继承** | 禁止超过 1 层的继承；功能通过 **多继承 Mixin** 或 **entry-point** 插件完成。 |
| **mypy strict** | 所有 PR 必须通过 `mypy --strict`；Protocol 不满足即报错。 |
| **内存守护** | 所有可能爆内存的 Loader/Processor **必须** 在子进程运行，RSS 超限自动杀。 |

---

## 8. 常用命令

```bash
uv sync                        # 安装 core（零依赖）
uv sync --extra dev            # 含 pytest/mypy
pytest -m "not bench"          # 快测试
mypy --strict                  # 必须全绿
uv build                       # 确保 wheel ≤ 1 MB
```

---

## 9. 4 周冲刺路线图（Protocol-oriented 版）

| Week | 交付 | 协议 / Mixin 完成度 |
|------|------|--------------------|
| W1 | `TypedStream` + `ProcessorProto` + `mypy strict` 绿灯 | 100 % |
| W2 | `PdfiumLoader` 实现 `LoaderProto` + `JsonlFormatterMixin` | 100 % |
| W3 | `docx` / `xlsx` stdlib Loader + CLI | 100 % |
| W4 | entry-point 插件系统 + `pymupdf` 加速插件 + bench CI | 100 % → tag `0.1.0a2` |

---

## 10. PR #1 成功标准（Protocol-oriented）

- [ ] `PdfiumLoader` **实现** `LoaderProto[PageStream]` 并产出含 bbox 的 `BlockStream`。  
- [ ] `JsonlFormatterMixin` **实现** `FormatterProto` 输出 ≤ 2× 原文件大小的合法 JSONL。  
- [ ] `pytest -m "not bench"` 全过 + `mypy --strict` 全绿。  
- [ ] `uv build` 核心 wheel ≤ 1 MB，**零第三方依赖**。  

---

## 11. 可改进（非阻塞，建议后续迭代）

| 改进点 | 现状 | 负面示例 / 量化缺口 | 推荐做法（后续 PR） |
|--------|------|----------------------|----------------------|
| **缺少“负面示例”** | 文档只给出“应该怎么做” | 三层继承反例：<br>```python<br>class BaseLoader:<br>    def load(self, path): ...<br>class PDFLoader(BaseLoader):<br>    def load(self, path): ...<br>class FastPDFLoader(PDFLoader):  # 第三层<br>    def load(self, path): ...<br>```<br>→ 子类想换 `PDFium → PyMuPDF` 必须改祖先；mypy 无法推断中间类型；插件热插拔失效。 | 在 `docs/anti/` 放 `deep_inheritance_bad.py` 并对比 `protocol_mixin_good.py`，CI 跑 `pytest -m anti` 保证反面教材永远编译。 |
| **性能基准未固化** | 只有口号“300 ms/MB” | 无梯度、无硬件、无容器镜像；本地跑 bench 结果不可复现。 | 用 `pytest-bench` 写 `test_bench_pdf.py`：<br>- 文件梯度：1 MB / 10 MB / 100 MB<br>- fixture 自动下载同一份 `corpus.pdf`（SHA-256 校验）<br>- 输出 `benchmark.json` → CI 上传 as artifact，出趋势折线。 |
| **版本策略与语义化** | 目前直接打 `0.1.0a2` | 缺少“何时 beta / rc / major”的量化定义。 | 在 `pyproject.toml` 加 `version.strategy = "protocol-driven"`：<br>- Protocol 冻结（无 breaking 变更）→ **beta**<br>- 下游插件生态 ≥ 3 家正式接入 → **rc**<br>- 零 OCR 误码率 < 1 %（1000 样本）→ **1.0.0** |
| **错误模型缺一页** | 现在随意抛 `RuntimeError` | 内存爆管、pdfium segfault 时 Sentry 无法聚合；调用链被 subprocess 截断。 | 统一 `DocpipeError(ProtocolName, Stage, OriginalExc)`，<br>在 `MemoryGuardMixin` 里对子进程异常做 `__cause__` 桥接，并裁剪 traceback（只留 `src/docpipe/*` 层）。 |
| **安全边界** | 子进程 + `psutil.RSS` 仅在 Linux 精准 | Windows 下 JOB_OBJECT 未限制，RSS 采集不准，可能 OOM 前杀不掉。 | `MemoryGuardMixin` 加平台分支：<br>- Linux → `psutil.memory_full_info().rss`<br>- macOS → `psutil.memory_info().rss`<br>- Windows → 用 `win32job` 创建 JobObject，设 `JOB_OBJECT_LIMIT_PROCESS_MEMORY`，兜底 `2 × max_mem_mb` 硬杀。 |

> 以上改进均 **不阻塞当前 PR**，后续迭代时按序打钩即可。

---

Ready to code — remember:  
**"Define a Protocol, ship a Mixin, compose, never inherit deep."**
```