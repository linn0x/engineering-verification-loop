# Engineering Verification Loop

中文 | [English](README.en.md)

Engineering Verification Loop 是一个面向 Codex 的技能包，用来把 Codex 从“代码执行者”推进成可以按需求自主完成完整工程研发生命周期的工程代理。你可以把一条产品或工程需求交给 Codex，让它从需求澄清、边界定义、风险拆解、方案设计、实现计划、代码修改、测试验证、性能/兼容性/模型检查、证据归档到交付总结一路推进。

它的核心不是“最后跑一轮检查”，而是让研发过程从一开始就带着证据约束前进：每个重要结论都要知道由什么验证，每个高风险点都要进入对应关卡，每个无法证明的主张都要被降级为限制、风险或下一步工作。遇到需求不清、上下文不足、权限缺失或证据不够时，它会明确阻塞点和下一步，而不是把未验证内容包装成完成。

这个仓库把当前本地安装的技能包整理成可发布到 GitHub 的分发版本。

## 我们可以用它做什么

用这个技能包，可以更放心地把一个工程任务交给 Codex 全流程推进：

- 从自然语言需求生成研发任务书：目标、非目标、约束、风险假设、验收标准和验证命令
- 让 Codex 自主编排需求分析、方案设计、实现计划、代码修改、测试、调试、优化、回归和交付总结
- 在写代码前明确哪些结论必须由单元测试、属性/差分测试、契约检查、模型检查、基准测试或 profiler 证明
- 对高风险 Go/Python 变更建立从需求到实现、从实现到验证、从验证到证据包的闭环
- 让 Codex 在开发过程中持续追问证据，避免“看起来能跑”的实现直接进入就绪状态
- 为 PR、发布、性能优化、兼容性变更留下可复核的工程记录
- 在无法继续时输出具体阻塞原因、缺失证据和下一步动作，而不是假装任务完成

## 适用场景

当一次变更需要为以下风险提供可辩护的证据时，使用这个技能包：

- 正确性关键逻辑、解析器、校验器、授权逻辑或状态转移
- 手写 Go/Python 实现与 Dafny 或 TLA 模型的一致性
- 在可测量性能约束下选择算法或数据结构
- 基准测试、实验结果或产品性能结论
- API、Schema、SDK、事件、OpenAPI、JSON Schema、GraphQL 或 Protobuf 兼容性
- CI 失败分类、复现和回归取证
- 基于 profiler 的 CPU、内存、分配或 I/O 优化
- 分布式协议在重试、分区、崩溃、时钟、法定人数或异步顺序下的行为

这个技能包刻意保持严格：没有证据支撑的结论会被记录为限制，而不是被当成已通过的关卡。

## 包含的技能

| 技能 | 用途 |
| --- | --- |
| `engineering-verification-loop` | 顶层编排、风险路由和证据包审计 |
| `dafny-verification` | 面向局部正确性属性的 Dafny 4+ 证明流程 |
| `property-based-differential-testing` | 属性测试、差分测试、变形测试和生成输入测试 |
| `algorithm-selection-benchmarking` | 算法/数据结构选择与基准证据 |
| `api-contract-compatibility` | OpenAPI、JSON fixture、Protobuf 和契约兼容性检查 |
| `ci-regression-forensics` | CI 失败分类、签名提取、诊断和 bisect 支持 |
| `reproducible-experiment-analysis` | 实验清单、重复指标、不确定性和可复现性审计 |
| `profiler-guided-optimization` | profiling 流程和优化前后指标 |
| `model-implementation-conformance` | 将 Dafny/TLA 模型属性映射到 Go/Python 实现证据 |
| `tla-distributed-model-checking` | 分布式协议的 TLC 和可选 Apalache 模型检查 |

## 仓库结构

```text
.
├── skills/                    # 会复制到 CODEX_HOME/skills 的 Codex 技能目录
├── scripts/
│   ├── install.sh             # 在本地安装或更新技能
│   └── validate.sh            # 校验仓库包结构和脚本
├── docs/
│   ├── INSTALL.md             # 详细安装指南
│   ├── DEPENDENCIES.md        # 各验证关卡需要的工具依赖
│   └── RELEASE_CHECKLIST.md   # 维护者发布检查清单
├── .github/workflows/         # GitHub Actions 校验工作流
├── VERSION
├── README.md                  # 默认中文 README
└── README.en.md               # 英文 README
```

## 快速安装

在这个仓库的克隆目录中运行：

```bash
./scripts/install.sh
```

默认情况下，安装脚本会把所有技能复制到：

```text
${CODEX_HOME:-$HOME/.codex}/skills
```

安装到自定义 Codex home：

```bash
./scripts/install.sh --dest "$HOME/.codex/skills"
```

只预览、不写入：

```bash
./scripts/install.sh --dry-run
```

完整安装和依赖配置见 [docs/INSTALL.md](docs/INSTALL.md)。

## 校验包

运行：

```bash
./scripts/validate.sh
```

校验内容包括：

- 每个打包技能都有有效的 `SKILL.md` frontmatter
- Python 脚本可以编译
- shell 脚本可以通过 `bash -n` 解析
- JSON 模板可以解析
- 可执行脚本具备可执行权限

这并不证明每个专门验证关卡都能在目标项目中运行。各关卡需要的工具见 [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md)。

## 基本用法

安装后，可以让 Codex 对一个具体工程变更使用顶层技能：

```text
Use $engineering-verification-loop to verify this Go/Python change.
```

编排器会：

1. 识别当前风险
2. 将每类风险路由到对应的专门技能
3. 要求提供相关命令证据
4. 组装证据包
5. 运行 `skills/engineering-verification-loop/scripts/audit-evidence-bundle.py`
6. 报告已通过关卡、失败关卡、无证据支撑的结论和下一个阻塞关卡

## 证据包

核心发布工件是证据包格式，位于：

```text
skills/engineering-verification-loop/assets/templates/evidence-bundle.json
```

用它记录：

- 变更目标和实现语言
- 当前风险
- 形式化覆盖映射
- 工作负载和结论范围
- 带有 `sha256`、生产命令和退出码的工件
- 按风险分类的专门证据
- 结构化的无证据支撑结论

使用以下命令审计：

```bash
skills/engineering-verification-loop/scripts/audit-evidence-bundle.py path/to/evidence-bundle.json --repo-root .
```

## 许可证

Apache License 2.0。见 [LICENSE](LICENSE)。
