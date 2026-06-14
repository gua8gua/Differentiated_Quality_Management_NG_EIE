"""Destructive merge of 日志/ duplicate documents."""
from pathlib import Path
import re
import shutil

ROOT = Path(r"e:\PyFile\Differentiated_Quality_Management_NG_EIE")
LOG = ROOT / "日志"

LINK_MAP = {
    "申报书第四章-技术方案索引.md": "01-申报书技术方案.md",
    "任务整理与初步规划.md": "02-任务与进度规划.md",
    "技术板块专业划分方案.md": "01-申报书技术方案.md",
    "日志1-数据与语义需求分析.md": "03-数据与数据集.md",
    "雷达软件元器件数据集调研.md": "03-数据与数据集.md",
    "项目领域与关键词索引.md": "04-领域关键词索引.md",
    "论文三项核心工作规划.md": "05-论文核心工作规划.md",
}

OLD_FILES = list(LINK_MAP.keys())


def read(name: str) -> str:
    return (LOG / name).read_text(encoding="utf-8")


def write(name: str, content: str) -> None:
    (LOG / name).write_text(content, encoding="utf-8")


def strip_section(text: str, start_marker: str) -> str:
    idx = text.find(start_marker)
    return text[:idx].rstrip() if idx >= 0 else text


# --- 00 总览 ---
write(
    "00-项目总览.md",
    """# 项目文档总览

> 新一代电子信息装备差异化质量管控（西工大部分）  
> 权威来源：`资料/申报书正文-西工大部分-提交.pdf`  
> 图像索引：`资料/img/README.md`  
> 更新日期：2026-06-14

---

## 文档导航

| 编号 | 文档 | 用途 |
|------|------|------|
| 00 | [项目总览](./00-项目总览.md) | 本页：统一入口 |
| 01 | [申报书技术方案](./01-申报书技术方案.md) | **工作划分权威**：第四章 §1/§2 章节树、命名规范 |
| 02 | [任务与进度规划](./02-任务与进度规划.md) | WBS、阶段 P1–P8、考核指标 |
| 03 | [数据与数据集](./03-数据与数据集.md) | 数据类型/标准 + 本地/公开数据集调研 |
| 04 | [领域关键词索引](./04-领域关键词索引.md) | 文献检索关键词、七大领域、会议期刊 |
| 05 | [论文核心工作规划](./05-论文核心工作规划.md) | 三项核心工作、实现方法、创新点 |
| — | [参考项目-开源与同类系统](./参考项目-开源与同类系统.md) | 开源对标与选型 |
| — | [学习目录/](./学习目录/00-总览.md) | 分阶段学习材料与术语 |

## 外部关联

- 数据集镜像：[`datasets/`](../datasets/目录.md)
- 参考实现：[`projects/`](../projects/目录.md)
- 申报书图像：[`资料/img/`](../资料/img/README.md)

## 阅读顺序建议

1. **01** → 看懂你要完成的技术方案章节编号  
2. **02** → 对齐进度与依赖  
3. **03** → 选数据做原型（建议从 `datasets/01_tabular_secom` 起步）  
4. **04** → 文献检索  
5. **05** → 论文主线收敛  
6. **学习目录** → 零基础分阶段补课
""",
)

# --- 01 申报书技术方案 ---
ch4 = read("申报书第四章-技术方案索引.md")
ch4 = ch4.replace("# 申报书第四章 · 技术方案索引", "# 申报书技术方案（第四章索引）")
ch4 = re.sub(
    r"> \*\*权威来源\*\*：.*?创建日期：.*?\n\n---\n",
    "> **权威来源**：`资料/申报书正文-西工大部分-提交.pdf` → **四、技术方案**  \n"
    "> **用途**：工作划分、文档命名、阶段规划均以本章为准；六域 A–F 为辅助学习分层。  \n"
    "> 技术方案示意图：[`资料/img/`](../资料/img/README.md)  \n"
    "> 更新日期：2026-06-14\n\n---\n",
    ch4,
    count=1,
)
tech = read("技术板块专业划分方案.md")
# extract problem diagnosis section
m = re.search(r"## 二、现有划分的问题诊断\n\n(.*?)\n\n---\n\n## 三、", tech, re.S)
appendix = ""
if m:
    appendix = (
        "\n\n---\n\n## 附录：常见划分误区（合并自技术板块方案）\n\n"
        + m.group(1).strip()
        + "\n\n> 完整四层架构方案已并入本章 §1–§6；勿再以「数据类/检测类/平台」三分法组织任务。\n"
    )
ch4 = strip_section(ch4, "## 7. 相关文档")
ch4 += (
    appendix
    + "\n\n## 7. 相关文档\n\n"
    + "- [任务与进度规划](./02-任务与进度规划.md)\n"
    + "- [数据与数据集](./03-数据与数据集.md)\n"
    + "- [学习目录总览](./学习目录/00-总览.md)\n"
    + "- [论文核心工作规划](./05-论文核心工作规划.md)\n"
)
write("01-申报书技术方案.md", ch4)

# --- 02 任务规划 ---
task = read("任务整理与初步规划.md")
task = task.replace(
    "# 新一代电子信息装备差异化质量管控技术 —— 任务整理与初步规划",
    "# 任务与进度规划",
)
task = re.sub(
    r"> \*\*工作划分权威\*\*：.*?创建日期：.*?\n",
    "> **工作划分权威**：[申报书技术方案](./01-申报书技术方案.md)  \n"
    "> 来源：`资料/申报书正文-西工大部分-提交.pdf`  \n"
    "> 更新日期：2026-06-14\n",
    task,
    count=1,
)
task = task.replace(
    "[申报书第四章-技术方案索引](./申报书第四章-技术方案索引.md)",
    "[申报书技术方案](./01-申报书技术方案.md)",
)
task = strip_section(task, "## 六、相关文档")
task += (
    "\n\n## 六、相关文档\n\n"
    "- [申报书技术方案](./01-申报书技术方案.md) — **工作划分权威**\n"
    "- [数据与数据集](./03-数据与数据集.md)\n"
    "- [论文核心工作规划](./05-论文核心工作规划.md)\n"
)
write("02-任务与进度规划.md", task)

# --- 03 数据与数据集 ---
log1 = read("日志1-数据与语义需求分析.md")
radar = read("雷达软件元器件数据集调研.md")

# log1: sections 0, 1, 2.1-2.2, 3.1-3.3
log1_body = strip_section(log1, "## 四、开源与公开数据资源")
log1_body = log1_body.replace(
    "# 日志1：任务数据类型、标准与开源资源评估 · 数据与语义工作分析",
    "## A. 数据类型、格式与标准",
)
log1_body = re.sub(r"> 依据：.*?范围：.*?\n\n---\n\n", "", log1_body, count=1)
log1_body = log1_body.replace(
    "[申报书第四章-技术方案索引](./申报书第四章-技术方案索引.md)",
    "[申报书技术方案](./01-申报书技术方案.md)",
)

radar_body = strip_section(radar, "## 七、相关文档")
radar_body = radar_body.replace(
    "# 雷达、软件、元器件相关数据集调研",
    "## B. 数据集调研（雷达 / 软件 / 元器件）",
)
radar_body = re.sub(r"> 来源：.*?创建日期：.*?\n\n---\n\n", "", radar_body, count=1)

data03 = f"""# 数据与数据集

> 合并自：数据语义需求分析 + 雷达/软件/元器件数据集调研  
> 关联：[申报书技术方案](./01-申报书技术方案.md) §1、§2.1；[datasets/](../datasets/目录.md)  
> 更新日期：2026-06-14

---

{log1_body.strip()}

---

{radar_body.strip()}

---

## C. 开源数据速查

> 详细本地镜像状态见 [`datasets/目录.md`](../datasets/目录.md) 与 [`manifest.json`](../datasets/manifest.json)。

| 场景 | 推荐数据集 | 支撑章节 |
|------|------------|----------|
| 高维工艺/元器件质量 | UCI SECOM（本地 `01_tabular_secom`） | §1.2.1、§1.3 |
| PHM/退化/RUL | CWRU、NASA C-MAPSS | §2.2.2 |
| 工业视觉 QC | MVTec AD | §1.2、§2.2.2 |
| 工控时序异常 | HAI、mfg009 | §2.5 联调 |
| 知识图谱/RAG | IOF、SAREF 样例 | §2.1 |
| MCDM 评价 | `08_synthetic_mcdm` | §1.3 |

**起步建议**：先用 `datasets/01_tabular_secom` 完成「元器件质量数据治理 + 异常识别」最小闭环，再扩展雷达整机与软件质量。

---

## 相关文档

- [申报书技术方案](./01-申报书技术方案.md)
- [任务与进度规划](./02-任务与进度规划.md)
- [论文核心工作规划](./05-论文核心工作规划.md)
- [datasets 目录](../datasets/目录.md)
"""
write("03-数据与数据集.md", data03)

# --- 04 领域关键词 ---
kw = read("项目领域与关键词索引.md")
kw = kw.replace(
    "# 新一代电子信息装备差异化质量管控 —— 涉及领域与查询关键词",
    "# 领域关键词索引",
)
kw = strip_section(kw, "## 六、相关文档索引")
kw = strip_section(kw, "## 七、零基础学习目录")  # moved to 学习目录/01-学习路线.md
kw += (
    "\n\n## 六、相关文档\n\n"
    "- [申报书技术方案](./01-申报书技术方案.md)\n"
    "- [数据与数据集](./03-数据与数据集.md)\n"
    "- [论文核心工作规划](./05-论文核心工作规划.md)\n"
    "- [学习路线](./学习目录/01-学习路线.md)\n"
)
write("04-领域关键词索引.md", kw)

# --- 05 论文 ---
paper = read("论文三项核心工作规划.md")
paper = paper.replace("# 论文三项核心工作规划", "# 论文核心工作规划")
paper = re.sub(
    r"> 关联文档：.*?\n",
    "> 关联文档：[申报书技术方案](./01-申报书技术方案.md)、[数据与数据集](./03-数据与数据集.md)  \n",
    paper,
    count=1,
)
paper = paper.replace("创建日期：2026-06-14", "更新日期：2026-06-14")
for old, new in LINK_MAP.items():
    paper = paper.replace(f"](./{old})", f"](./{new})")
write("05-论文核心工作规划.md", paper)

# --- 学习路线 ---
kw_full = read("项目领域与关键词索引.md")
m2 = re.search(r"## 七、零基础学习目录\n\n(.*)", kw_full, re.S)
if m2:
    route = (
        "# 零基础学习路线\n\n"
        "> 从「看懂申报书」到「能做小型原型、参与平台实现」的分阶段目录。  \n"
        "> 关键词检索见 [领域关键词索引](../04-领域关键词索引.md)；工作划分见 [申报书技术方案](../01-申报书技术方案.md)。  \n"
        "> 更新日期：2026-06-14\n\n---\n\n"
        + m2.group(1).strip()
        + "\n"
    )
    (LOG / "学习目录" / "01-学习路线.md").write_text(route, encoding="utf-8")

# --- move _申报书提取.txt ---
src_txt = LOG / "_申报书提取.txt"
dst_txt = ROOT / "资料" / "_申报书提取.txt"
if src_txt.exists() and not dst_txt.exists():
    shutil.move(str(src_txt), str(dst_txt))

# --- delete old files ---
for f in OLD_FILES:
    p = LOG / f
    if p.exists():
        p.unlink()

# --- update references repo-wide ---
REF_PATTERNS = [
    (r"日志/申报书第四章-技术方案索引\.md", "日志/01-申报书技术方案.md"),
    (r"\./申报书第四章-技术方案索引\.md", "./01-申报书技术方案.md"),
    (r"\.\./申报书第四章-技术方案索引\.md", "../01-申报书技术方案.md"),
    (r"\.\./\.\./申报书第四章-技术方案索引\.md", "../../01-申报书技术方案.md"),
    (r"\.\./\.\./\.\./申报书第四章-技术方案索引\.md", "../../../01-申报书技术方案.md"),
    (r"日志/任务整理与初步规划\.md", "日志/02-任务与进度规划.md"),
    (r"\./任务整理与初步规划\.md", "./02-任务与进度规划.md"),
    (r"\.\./任务整理与初步规划\.md", "../02-任务与进度规划.md"),
    (r"日志/技术板块专业划分方案\.md", "日志/01-申报书技术方案.md"),
    (r"\./技术板块专业划分方案\.md", "./01-申报书技术方案.md"),
    (r"\.\./技术板块专业划分方案\.md", "../01-申报书技术方案.md"),
    (r"日志/日志1-数据与语义需求分析\.md", "日志/03-数据与数据集.md"),
    (r"\./日志1-数据与语义需求分析\.md", "./03-数据与数据集.md"),
    (r"日志/雷达软件元器件数据集调研\.md", "日志/03-数据与数据集.md"),
    (r"\./雷达软件元器件数据集调研\.md", "./03-数据与数据集.md"),
    (r"\.\./日志/雷达软件元器件数据集调研\.md", "../日志/03-数据与数据集.md"),
    (r"日志/项目领域与关键词索引\.md", "日志/04-领域关键词索引.md"),
    (r"\./项目领域与关键词索引\.md", "./04-领域关键词索引.md"),
    (r"日志/论文三项核心工作规划\.md", "日志/05-论文核心工作规划.md"),
    (r"\./论文三项核心工作规划\.md", "./05-论文核心工作规划.md"),
]

for md in ROOT.rglob("*.md"):
    if "node_modules" in md.parts:
        continue
    text = md.read_text(encoding="utf-8")
    new = text
    for pat, repl in REF_PATTERNS:
        new = re.sub(pat, repl, new)
    if new != text:
        md.write_text(new, encoding="utf-8")
        print("updated", md.relative_to(ROOT))

print("merge complete")
