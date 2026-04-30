# Yao Tutorial Skill

`yao-tutorial-skill` 是一个面向教程成品生产的 Skill：输入一个主题，或输入一组参考资料、网址、论文、GitHub 仓库、草稿，它会把这些信息整理成一套带来源、带大纲、带章节配图、带多格式导出的完整教程。

它适合用来做“从入门到精通”类教程、系统化学习文档、产品或技术教材、方法论手册，以及需要正式交付的长篇教学内容。

## 它会做什么

1. 把输入归一化为 `brief.json`，明确主题、受众、目标、材料、格式和限制。
2. 优先吸收用户给的资料；资料不足时，再补充官方文档、论文、GitHub、实践案例和高质量分享。
3. 生成来源登记和证据映射，避免教程变成无依据的泛泛写作。
4. 设计面向小白的教程大纲，使用 `第1章`、`1.1` 这类清晰编号。
5. 写出完整教程正文，默认中文约 `5000-10000` 字。
6. 为每个编号章节生成一个 HTML 可视化配图，再截图嵌入正文。
7. 导出 `Markdown`、`Word`、`PDF` 和 `HTML`。
8. 运行验证脚本，检查章节、配图、引用、截图、导出文件、页眉页脚和本地路径泄漏。

## 典型输出

```text
output/
├── brief.json
├── outline.md
├── tutorial.md
├── research/
│   ├── source-register.md
│   └── evidence-map.md
├── visuals/
│   ├── visual-spec.json
│   └── index.html
├── assets/
│   └── screenshots/
└── exports/
    ├── tutorial.html
    ├── tutorial.docx
    └── tutorial.pdf
```

## 关键约束

- 用户资料足够时，以用户资料为主线，不机械扩大搜索范围。
- 用户资料不足时，外部来源优先级为官方/一手来源、论文、GitHub、权威实践分享。
- 每个重要判断都应有来源 ID 或来源附录支撑。
- 每个编号章节都必须有一个对应视觉规格和一张嵌入配图。
- HTML 报告要使用居中内容容器、粘性目录、日期和章节跳转。
- Word/PDF 默认不保留页眉页脚，避免路径、页码和打印信息影响阅读。

## 主要文件

- [`SKILL.md`](SKILL.md): Skill 入口和最小工作流
- [`references/input-adaptation.md`](references/input-adaptation.md): 输入资料优先级和补充研究逻辑
- [`references/research-sourcing.md`](references/research-sourcing.md): 来源选择和证据登记规则
- [`references/tutorial-outline-and-writing.md`](references/tutorial-outline-and-writing.md): 大纲与正文写作规则
- [`references/visual-html-workflow.md`](references/visual-html-workflow.md): HTML 配图画板生成规则
- [`references/export-workflow.md`](references/export-workflow.md): Word/PDF/HTML 导出规则
- [`scripts/validate_package.py`](scripts/validate_package.py): 输出包验证脚本
