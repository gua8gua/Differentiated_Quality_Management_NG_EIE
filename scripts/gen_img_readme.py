import json
from pathlib import Path

import fitz

pdf = Path(r"e:\PyFile\Differentiated_Quality_Management_NG_EIE\资料\申报书正文-西工大部分-提交.pdf")
out = Path(r"e:\PyFile\Differentiated_Quality_Management_NG_EIE\资料\img")
doc = fitz.open(pdf)
embedded = []
for page_idx in range(len(doc)):
    page = doc[page_idx]
    for img_idx, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base = doc.extract_image(xref)
        name = f"page{page_idx + 1:02d}_img{img_idx + 1:02d}.{base['ext']}"
        embedded.append(
            {"file": name, "page": page_idx + 1, "type": "embedded", "ext": base["ext"]}
        )

manifest = {
    "source": str(pdf),
    "pages": len(doc),
    "embedded_count": len(embedded),
    "embedded": embedded,
    "full_page_renders": [f"page{i + 1:02d}_full.png" for i in range(len(doc))],
}
(out / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)

readme = f"""# 申报书图像提取

> 来源：`资料/申报书正文-西工大部分-提交.pdf`（{len(doc)}页）  
> 提取日期：2026-06-14

## 文件说明

| 类型 | 命名 | 数量 | 用途 |
|------|------|------|------|
| 嵌入图像 | `pageXX_imgYY.{{ext}}` | {len(embedded)} | PDF 内嵌位图（技术方案示意图等） |
| 整页渲染 | `pageXX_full.png` | {len(doc)} | 每页 2x 分辨率 PNG，含矢量图与排版 |

## 技术方案图页参考

申报书第四章技术方案示意图主要出现在以下页面（建议优先查看嵌入图或整页渲染）：

| 图号（申报书） | 建议查看文件 |
|----------------|--------------|
| 图1 装备质量数据标准与治理 | `page13_full.png` 及同页 `*_img*` |
| 图2 缺失数据补全架构 | `page17_full.png` |
| 图3 时空扩散多模态补全 | `page18_full.png` |
| 图4 Lasso-FCE评价方法 | `page19_full.png` |
| 图5 风险识别技术路线 | `page20_full.png` |
| 图6–7 知识图谱 NER/RE | `page22_full.png`、`page23_full.png` |
| 图8 质量问题分析树 | `page26_full.png` |
| 图9 Seq2Seq故障检测 | `page27_full.png` |
| 图10 卷积运算流程 | `page28_full.png` |
| 图11 时序反转对比学习 | `page29_full.png` |
| 图12–13 垂类模型与风险预测 | `page30_full.png`、`page31_full.png` |
| 图14–17 三类智能体结构 | `page32_full.png`–`page35_full.png` |
| 图18 智能决策管理平台 | `page36_full.png` |

详细清单见 [`manifest.json`](./manifest.json)。
"""
(out / "README.md").write_text(readme, encoding="utf-8")
print("done", len(embedded), len(doc))
