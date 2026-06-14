"""Rename embedded figures and update manifest."""
import json
from pathlib import Path

IMG = Path(r"e:\PyFile\Differentiated_Quality_Management_NG_EIE\资料\img")

RENAMES = [
    ("page14_img01.jpeg", "01_质控数据标准与治理技术路线图.jpeg"),
    ("page17_img01.jpeg", "02_多变量时序列缺失补全与不确定性量化架构.jpeg"),
    ("page18_img01.jpeg", "03_时空扩散多模态数据预测模型架构.jpeg"),
    ("page20_img01.jpeg", "04_Lasso模糊综合质量数据评估方法.jpeg"),
    ("page21_img01.jpeg", "05_智能化质量风险识别反馈响应技术路线.jpeg"),
    ("page23_img01.jpeg", "06_知识图谱命名实体识别BERT-BiLSTM-CRF.jpeg"),
    ("page24_img01.jpeg", "07_知识图谱关系抽取提示微调.jpeg"),
    ("page27_img01.jpeg", "08_质量问题分析树结构示意图.jpeg"),
    ("page28_img01.jpeg", "09_Seq2Seq自编码器少样本故障检测.jpeg"),
    ("page28_img02.jpeg", "10_格拉姆角场卷积特征提取流程.jpeg"),
    ("page29_img01.jpeg", "11_时序反转对比学习RUL预测.jpeg"),
    ("page30_img01.jpeg", "12_装备质控领域垂类模型架构.jpeg"),
    ("page31_img01.jpeg", "13_大模型潜在质量风险预测方法.jpeg"),
    ("page32_img01.jpeg", "14_三类质量管控智能体协同机制.jpeg"),
    ("page33_img01.jpeg", "15_整机质量管控智能体结构.jpeg"),
    ("page34_img01.jpeg", "16_软件质量管控智能体结构.jpeg"),
    ("page35_img01.jpeg", "17_元器件质量管控智能体结构.jpeg"),
    ("page37_img01.jpeg", "18_质量管控智能决策管理平台架构.jpeg"),
]

figures = []
for i, (old, new) in enumerate(RENAMES, 1):
    src = IMG / old
    dst = IMG / new
    if src.exists():
        src.rename(dst)
        figures.append({"id": i, "file": new, "old_file": old})
        print(f"renamed: {old} -> {new}")
    elif dst.exists():
        figures.append({"id": i, "file": new, "old_file": old})
        print(f"exists: {new}")
    else:
        print(f"missing: {old}")

manifest = {
    "source": "资料/申报书正文-西工大部分-提交.pdf",
    "count": len(figures),
    "naming": "编号_内容.jpeg（编号对应申报书图1–图18）",
    "figures": figures,
}
(IMG / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("done", len(figures))
