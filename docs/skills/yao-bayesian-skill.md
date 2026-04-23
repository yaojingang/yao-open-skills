# Yao Bayesian Skill

## 中文说明

`yao-bayesian-skill` 用来把“不确定该不该做”的现实问题，变成一份可执行的贝叶斯决策报告。

它不只是算一个概率，而是把问题拆成：

- 要判断的假设
- 参考类和先验
- 证据分级
- 后验更新
- 敏感性分析
- 行动建议
- 下一步最有价值的信息

最终可以自动导出 `json`、`markdown`、`html`、`pdf`、`docx` 五种结果。

### 适合什么时候用

- 产品、增长、市场、运营等不确定性决策
- 个人旅行、求职、搬家、投入与放弃类判断
- 想把“感觉上该不该做”变成可解释的判断链路
- 需要一份团队能直接讨论的决策报告

### 主流程

1. 先把问题结构化成一个明确假设和行动集合
2. 对证据做分级，并构造可解释先验
3. 做赔率更新或 Beta-binomial 更新
4. 比较行动阈值和期望值
5. 生成中文主报告和双语 HTML 报告

### 输出物

- 结构化结果 `json`
- 中文主报告 `markdown`
- 带 `简版 / 专业版` 切换的双语 `html`
- 中文 `pdf`
- 中文 `docx`

### 命令

基础 bundle 导出：

```bash
python3 skills/yao-bayesian-skill/scripts/generate_report_bundle.py input.json out/
```

例如：

```bash
python3 skills/yao-bayesian-skill/scripts/generate_report_bundle.py \
  skills/yao-bayesian-skill/input/bayesian_decision_request.template.json \
  out/
```

### 公开发布约定

`reports/` 下的运行产物默认属于本地输出，不随公开副本一起维护。公开仓库保留的是 Skill 本体、输入样例、脚本、模板、引用资料和评估配置。

## English Usage

`yao-bayesian-skill` turns uncertain real-world choices into an auditable Bayesian decision report.

It does more than compute a single probability. It walks through:

- hypothesis framing
- reference class and prior setup
- evidence grading
- posterior updates
- sensitivity analysis
- action recommendation
- next-information guidance

The skill can export the same decision result as `json`, `markdown`, `html`, `pdf`, and `docx`.

### When to use it

- product, growth, market, and operations decisions under uncertainty
- personal decisions such as travel, relocation, and timing choices
- cases where you want an explicit reasoning chain rather than a vague judgment
- team discussions that need a shareable decision artifact

### Main workflow

1. Structure the problem into a hypothesis and action set.
2. Grade evidence and build an explainable prior.
3. Run odds updates or a Beta-binomial update.
4. Compare actions with thresholds and expected value.
5. Export a Chinese-first bundle plus a bilingual HTML report.

### Command

```bash
python3 skills/yao-bayesian-skill/scripts/generate_report_bundle.py input.json out/
```

### Publishing boundary

Generated runtime artifacts under local report directories are treated as local outputs by default. The public collection keeps the reusable skill sources, examples, scripts, templates, references, and eval config instead.
