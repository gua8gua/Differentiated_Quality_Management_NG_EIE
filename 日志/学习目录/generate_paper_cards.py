# -*- coding: utf-8 -*-
"""批量生成论文学习卡片"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
NOTES = ROOT / "日志" / "论文整理"
OUT = Path(__file__).resolve().parent / "03-论文学习卡片"

DIR_MAP = {
    "01-数据标准化": "01-数据标准化",
    "02-数据治理与增强": "02-数据治理与增强",
    "03-数据评价": "03-数据评价",
    "04-风险识别与预测": "04-风险识别与预测",
}

META = {
    1: {
        "summary": "通过访谈医疗从业者，梳理大数据平台里数据质量问题的来源与改进路径（定性研究）。",
        "domains": ["L1", "L6"],
        "before": ["ISO 8000 数据质量三维", "ETL 与数据溯源概念"],
        "after": ["能说明全生命周期数据质量挑战", "理解标准体系建设的动机"],
        "proposal": "1.1 质量数据标准体系、全生命周期管理",
        "terms": ["ETL", "数据质量", "全生命周期"],
        "resources": [
            "ISO 8000 概述：https://quality.arc42.org/standards/iso-8000",
            "[01-术语词典](../01-术语词典.md) — ETL、数据质量",
        ],
        "pdf": "资料/参考文献/01-数据标准化/01-医疗大数据平台数据质量提升.pdf",
    },
    2: {
        "summary": "为物联网数据设计自适应加权融合框架，综合多源估计得到更可靠的质量评分。",
        "domains": ["L1", "L3"],
        "before": ["传感器数据基础", "加权融合概念"],
        "after": ["理解 IoT 数据质量评估流程", "能解释自适应加权融合思路"],
        "proposal": "1.3 多源不确定信息融合评价",
        "terms": ["IoT", "自适应加权融合", "MCDM"],
        "resources": [
            "[L1 §2.3 IoT](../../02-知识域/L1-数据标准与工业互联网.md)",
            "MDPI Sensors 原文 DOI 页面",
        ],
        "pdf": "资料/参考文献/01-数据标准化/02-IoT数据质量自适应加权融合评估.pdf",
    },
    3: {
        "summary": "在制造业场景下，把数据质量问题与决策风险挂钩，提出评估与缓解框架。",
        "domains": ["L1", "L4", "L6"],
        "before": ["数据质量维度", "风险管理基础"],
        "after": ["理解数据质量如何驱动决策风险", "掌握 FMEA/风险矩阵局限"],
        "proposal": "2.2 质量风险识别与预测",
        "terms": ["FMEA", "决策风险", "数据质量"],
        "resources": [
            "[L6 平台闭环](../../02-知识域/L6-平台工程与闭环系统.md)",
            "[L4 §2.4 FMEA](../../02-知识域/L4-机器学习与可靠性预测.md)",
        ],
        "pdf": "资料/参考文献/01-数据标准化/03-制造业数据质量决策风险评估缓解.pdf",
    },
    4: {
        "summary": "用数据驱动方法分析复杂产品关键部件的需求与设计可靠性，衔接数字孪生思路。",
        "domains": ["L1", "L4"],
        "before": ["复杂产品研制流程", "可靠性工程入门"],
        "after": ["理解需求-可靠性脱节问题", "了解数字孪生在设计阶段的作用"],
        "proposal": "1.1 全生命周期质量数据管理",
        "terms": ["数字孪生", "设计可靠性", "需求分析"],
        "resources": [
            "[L1 §2.7](../02-知识域/L1-数据标准与工业互联网.md)",
            "[项目工作通俗介绍](../../项目工作通俗介绍.md)",
        ],
        "pdf": "资料/参考文献/01-数据标准化/04-复杂产品关键部件数据驱动需求与可靠性.pdf",
    },
    5: {
        "summary": "用熵权法+因子分析评估建材行业工业互联网成熟度，方法可迁移到装备企业调研。",
        "domains": ["L1", "L3"],
        "before": ["熵权法原理", "因子分析基础"],
        "after": ["会解读成熟度评价指标", "理解客观赋权在评价中的作用"],
        "proposal": "1.3 评价指标体系（客观权重）",
        "terms": ["熵权法", "因子分析", "MCDM", "工业互联网"],
        "resources": [
            "[L1 §2.4](../02-知识域/L1-数据标准与工业互联网.md)",
            "《综合评价理论、方法与应用》（郭亚军）",
        ],
        "pdf": "资料/参考文献/01-数据标准化/05-建材行业工业互联网成熟度评估.pdf",
    },
    6: {
        "summary": "用 q 阶正交模糊集（q-ROF）做多准则决策，评价电力装备供应商质量水平。",
        "domains": ["L1", "L3"],
        "before": ["模糊集基础", "MCDM 流程"],
        "after": ["了解 q-ROF 模糊决策", "理解供应商/装备质量综合评价思路"],
        "proposal": "1.3.2 模糊综合评价",
        "terms": ["q-ROF", "MCDM", "模糊综合评价"],
        "resources": [
            "[01-术语词典 — q-ROF](../01-术语词典.md)",
            "[L3 §2.4 模糊评价](../02-知识域/L3-综合评价与决策方法.md)",
        ],
        "pdf": "资料/参考文献/01-数据标准化/06-电力装备供应商q阶正交模糊评价.pdf",
        "pdf_note": "**PDF 待补**（DOI: 10.1016/j.heliyon.2024.e40390）",
    },
    7: {
        "summary": "讨论 ASME/ISO 如何在三维点云与先进制造时代重新定义几何「基准」。",
        "domains": ["L1"],
        "before": ["GD&T/基准概念", "数字孪生数据类型"],
        "after": ["理解标准升级对质量数据描述的推动", "了解点云与基准的关系"],
        "proposal": "1.1 质量数据描述规范",
        "terms": ["Datum", "ASME", "ISO", "点云"],
        "resources": [
            "[L1 §2.6](../02-知识域/L1-数据标准与工业互联网.md)",
            "ASME Y14.5 基准相关公开资料",
        ],
        "pdf": "资料/参考文献/01-数据标准化/07-面向先进制造的基准数学定义.pdf",
    },
    8: {
        "summary": "用 RANSAC 回归+自适应阈值清洗风电 SCADA 数据中的异常点。",
        "domains": ["L2"],
        "before": ["线性回归", "离群点概念"],
        "after": ["掌握 RANSAC 清洗流程", "理解自适应阈值优于固定 3σ"],
        "proposal": "1.2.1 软阈值滑动窗口异常检测",
        "terms": ["RANSAC", "自适应阈值", "异常检测"],
        "resources": [
            "scikit-learn 异常检测：https://scikit-learn.org/stable/modules/outlier_detection.html",
            "[L2 §2.1](../02-知识域/L2-数据治理与异常处理.md)",
        ],
        "pdf": "资料/参考文献/02-数据治理与增强/08-RANSAC自适应阈值风电数据清洗.pdf",
    },
    9: {
        "summary": "用模糊投票+多段 LOESS 插值修复时间序列中的异常与缺失段。",
        "domains": ["L2"],
        "before": ["时间序列插值", "LOESS 基础"],
        "after": ["理解多方法投票修复", "了解大跨度缺失的处理策略"],
        "proposal": "1.2.2 多变量时序缺失补全",
        "terms": ["LOESS", "模糊投票", "插值", "缺失补全"],
        "resources": [
            "pandas 缺失值处理文档",
            "[L2 §2.2](../02-知识域/L2-数据治理与异常处理.md)",
        ],
        "pdf": "资料/参考文献/02-数据治理与增强/09-模糊投票多段插值数据异常修复.pdf",
    },
    10: {
        "summary": "针对稀有聚集总体，用稳健回归与自适应抽样改进均值估计，说明 3σ/IQR 局限。",
        "domains": ["L2"],
        "before": ["正态分布假设", "3σ/IQR 规则"],
        "after": ["理解固定阈值失效原因", "了解稳健统计替代方案"],
        "proposal": "1.2.1 动态阈值异常检测",
        "terms": ["3σ", "IQR", "稳健回归", "重尾分布"],
        "resources": [
            "[L2 §2.1](../02-知识域/L2-数据治理与异常处理.md)",
            "statsmodels 稳健回归入门",
        ],
        "pdf": "资料/参考文献/02-数据治理与增强/10-稀有聚集总体稳健回归与自适应抽样.pdf",
    },
    11: {
        "summary": "对比半监督异常检测与监督方法预测材料泊松比，适合少样本标注场景。",
        "domains": ["L2", "L4"],
        "before": ["异常检测分类", "监督/半监督区别"],
        "after": ["会选择半监督 vs 全监督策略", "理解标注稀缺时的检测方案"],
        "proposal": "1.2.1 智能异常值检测",
        "terms": ["半监督异常检测", "监督学习"],
        "resources": [
            "scikit-learn 半监督模块",
            "[L2 §2.1](../02-知识域/L2-数据治理与异常处理.md)",
        ],
        "pdf": "资料/参考文献/02-数据治理与增强/11-泊松比预测半监督异常检测.pdf",
    },
    12: {
        "summary": "对高维数据流做层次稀疏表示聚类，降低冗余但计算成本较高。",
        "domains": ["L2"],
        "before": ["聚类基础", "先读 [13] 稀疏表示"],
        "after": ["理解稀疏表示+聚类组合", "评估实时性约束"],
        "proposal": "1.2.1 高维特征冗余处理",
        "terms": ["稀疏表示", "层次聚类", "数据流"],
        "resources": [
            "先读卡片 [13]",
            "sklearn.cluster 文档",
        ],
        "pdf": "资料/参考文献/02-数据治理与增强/12-高维数据流层次稀疏表示聚类.pdf",
    },
    13: {
        "summary": "提出高效稀疏表示方法，用于高维数据学习与特征筛选。",
        "domains": ["L2"],
        "before": ["线性代数", "Lasso/稀疏正则"],
        "after": ["理解稀疏表示降冗余", "能关联到特征选择任务"],
        "proposal": "1.2.1 差异化特征有效性筛选",
        "terms": ["稀疏表示", "特征选择", "高维数据"],
        "resources": [
            "[L2 §2.3](../02-知识域/L2-数据治理与异常处理.md)",
            "sklearn.feature_selection 文档",
        ],
        "pdf": "资料/参考文献/02-数据治理与增强/13-高维数据高效稀疏表示学习.pdf",
        "extra": "> **注**：[14] 与本文重复引用，见申报书题录。",
    },
    15: {
        "summary": "融合贝叶斯与马尔可夫多源先验，评估高可靠系统三态（正常/潜在/失效）可靠性。",
        "domains": ["L2", "L4"],
        "before": ["贝叶斯推断", "马尔可夫链概念"],
        "after": ["理解多源先验融合", "了解小样本可靠性评估"],
        "proposal": "1.2.2 小样本缺失补全与共形预测",
        "terms": ["贝叶斯", "马尔可夫", "三态可靠性", "共形预测"],
        "resources": [
            "[L2 §2.4](../02-知识域/L2-数据治理与异常处理.md)",
            "PyMC 概率编程入门",
        ],
        "pdf": "资料/参考文献/02-数据治理与增强/15-多源先验信息高可靠系统三态评估.pdf",
    },
    16: {
        "summary": "用 ML 区间预测评估高铁路基压实质量，给出带置信区间的质量判定。",
        "domains": ["L2", "L4"],
        "before": ["点估计 vs 区间估计", "ML 回归基础"],
        "after": ["理解区间预测价值", "能解释不确定性量化在质量评估中的应用"],
        "proposal": "1.2.2 缺失补全与不确定性",
        "terms": ["区间预测", "不确定性量化", "多源融合"],
        "resources": [
            "[L2 §2.4](../02-知识域/L2-数据治理与异常处理.md)",
            "Quantile Regression 资料",
        ],
        "pdf": "资料/参考文献/02-数据治理与增强/16-ML区间预测高铁路基压实质量评估.pdf",
    },
    17: {
        "summary": "提出最大熵-最小残差模型，为综合评价与多属性决策提供更稳健的权重方案。",
        "domains": ["L3"],
        "before": ["熵权法", "多属性决策流程"],
        "after": ["理解 CEI 权重争议", "掌握最大熵-最小残差思路"],
        "proposal": "1.3 质量数据评价模型",
        "terms": ["最大熵", "最小残差", "CEI", "MCDM", "DEA"],
        "resources": [
            "[L3 §2.2](../02-知识域/L3-综合评价与决策方法.md)",
            "《综合评价理论、方法与应用》",
        ],
        "pdf": "资料/参考文献/03-数据评价/17-最大熵最小残差综合评价模型.pdf",
    },
    18: {
        "summary": "用证据推理法融合异质区间信息，做多准则科研质量评价。",
        "domains": ["L3"],
        "before": ["概率基础", "D-S 证据理论入门"],
        "after": ["理解异质信息融合", "掌握证据推理在评价中的应用"],
        "proposal": "1.3.1 D-S 证据理论融合",
        "terms": ["D-S", "证据推理", "异质信息", "区间不确定"],
        "resources": [
            "[L3 §2.4](../02-知识域/L3-综合评价与决策方法.md)",
            "Dempster-Shafer 简明教程",
        ],
        "pdf": "资料/参考文献/03-数据评价/18-异质信息多准则科研质量评价.pdf",
    },
    19: {
        "summary": "Entropy-TOPSIS-IF 组合方法评价城市公共卫生应急能力，主客观权重结合。",
        "domains": ["L3"],
        "before": ["TOPSIS 原理", "直觉模糊集"],
        "after": ["会解读 Entropy-TOPSIS-IF 流程", "理解主客观组合赋权"],
        "proposal": "1.3.1 灰色关联+Lasso+D-S+FCE",
        "terms": ["熵权法", "TOPSIS", "IF", "MCDM"],
        "resources": [
            "[L3 §2.2–2.4](../02-知识域/L3-综合评价与决策方法.md)",
            "《综合评价》TOPSIS 章节",
        ],
        "pdf": "资料/参考文献/03-数据评价/19-熵权TOPSIS-IF城市公共卫生评价.pdf",
    },
    20: {
        "summary": "结合知识图谱与价值熵评价非定制化数据资产，桥接评价与知识工程。",
        "domains": ["L3", "L5"],
        "before": ["知识图谱三元组", "熵权法", "TOPSIS"],
        "after": ["理解 KG+熵 评价框架", "能关联到质控知识图谱建设"],
        "proposal": "1.3 评价 + 2.1 知识图谱",
        "terms": ["KG", "价值熵", "TOPSIS", "数据资产"],
        "resources": [
            "[L5 §2.1](../02-知识域/L5-知识图谱-NLP-大模型.md)",
            "Neo4j Getting Started：https://neo4j.com/docs/getting-started/",
        ],
        "pdf": "资料/参考文献/03-数据评价/20-知识图谱价值熵数据资产评价.pdf",
    },
    21: {
        "summary": "用德尔菲+AHP 开发并验证 OCT 图像质量评价准则，示范指标构建流程。",
        "domains": ["L3"],
        "before": ["AHP 层次分析法", "专家调查方法"],
        "after": ["掌握指标开发与验证流程", "理解 AHP 定权重"],
        "proposal": "1.3.2 AHP 多层级权重",
        "terms": ["德尔菲法", "AHP", "质量准则"],
        "resources": [
            "[L3 §2.3](../02-知识域/L3-综合评价与决策方法.md)",
            "AHP 在线教程",
        ],
        "pdf": "资料/参考文献/03-数据评价/21-前节段OCT图像质量评价准则.pdf",
    },
    22: {
        "summary": "QUADAS-3 是诊断准确性研究质量评估的修订工具，强调偏倚与报告规范。",
        "domains": ["L3"],
        "before": ["系统评价/证据质量概念"],
        "after": ["理解高质量评估工具的设计原则", "能借鉴到本项目评价模型质检"],
        "proposal": "评价模型本身的质量控制",
        "terms": ["QUADAS-3", "偏倚评估", "诊断准确性"],
        "resources": [
            "PubMed：https://pubmed.ncbi.nlm.nih.gov/41698208/",
            "Cochrane Risk of Bias 工具",
        ],
        "pdf": "资料/参考文献/03-数据评价/22-QUADAS-3诊断准确性质量评估工具.pdf",
    },
    23: {
        "summary": "QUADAS-3 解释与详述指南，说明各条目如何打分与应用。",
        "domains": ["L3"],
        "before": ["先读 [22]"],
        "after": ["能按指南使用 QUADAS-3", "理解 E&E 文档的作用"],
        "proposal": "评价框架质量控制（与 [22] 配套）",
        "terms": ["QUADAS-3", "E&E", "评估流程"],
        "resources": [
            "与 [22] 同读",
            "GRADE 证据质量框架简介",
        ],
        "pdf": "资料/参考文献/03-数据评价/23-QUADAS-3解释与详述指南.pdf",
    },
    24: {
        "summary": "QUAIDE 清单用于评估诊断内镜 AI 临床前研究质量，可借鉴 AI 模型质检。",
        "domains": ["L3", "L5"],
        "before": ["AI 模型评估基础"],
        "after": ["了解 AI 临床前研究质量标准", "关联 RAG/大模型可信度校验"],
        "proposal": "2.2.3 大模型+RAG 可信度",
        "terms": ["QUAIDE", "AI 质量评估", "临床前研究"],
        "resources": [
            "[L3 §2.5](../02-知识域/L3-综合评价与决策方法.md)",
            "QUAIDE 原文 Supplementary",
        ],
        "pdf": "资料/参考文献/03-数据评价/24-QUAIDE诊断内镜AI临床前研究质量评估.pdf",
    },
    25: {
        "summary": "提出 AI 预测模型五项关键质量准则，呼应数据质量五维框架。",
        "domains": ["L3", "L4", "L5"],
        "before": ["ML 模型评估指标", "数据质量五维"],
        "after": ["掌握五项 AI 质量准则", "能用于评价本项目预测模型"],
        "proposal": "2.2 风险预测模型评价",
        "terms": ["AI 预测模型", "质量准则", "可解释性"],
        "resources": [
            "[L3 数据质量五维](../02-知识域/L3-综合评价与决策方法.md)",
            "TRIPOD-AI / PROBAST 指南对比",
        ],
        "pdf": "资料/参考文献/03-数据评价/25-AI预测模型五项关键质量准则.pdf",
    },
    26: {
        "summary": "在传感器退化与失效条件下，构建系统控制风险评估框架。",
        "domains": ["L4", "L6"],
        "before": ["传感器故障模式", "风险矩阵"],
        "after": ["理解传感器退化对决策的影响", "了解动态风险量化需求"],
        "proposal": "2.2 质量风险识别",
        "terms": ["传感器退化", "FMEA", "PHM", "风险评估"],
        "resources": [
            "[L4 §2.4](../02-知识域/L4-机器学习与可靠性预测.md)",
            "[L6 闭环系统](../02-知识域/L6-平台工程与闭环系统.md)",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/26-传感器退化失效系统控制风险评估.pdf",
    },
    27: {
        "summary": "用 ML 算法基于工艺条件数据预测连铸夹杂物，处理类别不平衡问题。",
        "domains": ["L4"],
        "before": ["分类指标", "不平衡学习"],
        "after": ["理解少样本/不平衡下的 ML 局限", "了解 Seq2Seq 等替代思路"],
        "proposal": "2.2.2 少样本 Seq2Seq 自编码器",
        "terms": ["RF", "类别不平衡", "欠采样", "工艺数据"],
        "resources": [
            "scikit-learn RandomForestClassifier",
            "imbalanced-learn 文档",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/27-连铸过程夹杂物机器学习预测.pdf",
    },
    28: {
        "summary": "BP 神经网络结合 Icepak 仿真评估电容与晶体管可靠性，应对退化数据稀疏。",
        "domains": ["L4"],
        "before": ["神经网络基础", "可靠性试验概念"],
        "after": ["理解仿真+数据混合建模", "了解电子元器件寿命预测"],
        "proposal": "2.2.2 寿命预测与机理可释智能体",
        "terms": ["BP", "Icepak", "加速寿命测试"],
        "resources": [
            "PyTorch MLP 教程",
            "[L4 §2.1](../02-知识域/L4-机器学习与可靠性预测.md)",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/28-BP神经网络Icepak电容晶体管可靠性.pdf",
    },
    29: {
        "summary": "汽车工业案例展示 ML 预测模型在质量控制中的应用与决策偏差问题。",
        "domains": ["L4", "L6"],
        "before": ["工业 QC 流程", "ML 回归/分类"],
        "after": ["理解 QC 中数据质量与决策偏差", "了解平台集成需求"],
        "proposal": "2.3 三类智能体",
        "terms": ["质量控制", "测量不确定性", "决策偏差"],
        "resources": [
            "scikit-learn 官方教程",
            "[L6 平台架构](../02-知识域/L6-平台工程与闭环系统.md)",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/29-汽车工业质量控制ML预测案例.pdf",
    },
    30: {
        "summary": "与 [3] 同一篇；风险方向侧重 FMEA/风险矩阵局限与大模型 RAG 多故障级联。",
        "domains": ["L1", "L4", "L5", "L6"],
        "before": ["先读 [3]", "FMEA 基础", "RAG 概念"],
        "after": ["理解跨方向引用逻辑", "从风险视角重读 [3]"],
        "proposal": "2.2 大模型+RAG 多故障级联",
        "terms": ["FMEA", "风险矩阵", "RAG"],
        "resources": [
            "[L5 §2.3 RAG](../02-知识域/L5-知识图谱-NLP-大模型.md)",
            "卡片 [03-数据标准化/03-*.md](01-数据标准化/03-制造业数据质量决策风险评估缓解.md)",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/30-制造业数据质量决策风险评估缓解-同03.pdf",
        "extra": "> **注**：与 [3] 为同一篇（DOI: 10.3390/s24206586），详见 [3] 卡片。",
    },
    31: {
        "summary": "Kaneko 用 RF/梯度提升树预测精密电气元件缺陷率并诊断失效原因。",
        "domains": ["L4", "L5"],
        "before": ["集成学习", "特征重要性"],
        "after": ["掌握缺陷率预测+根因诊断流程", "理解多工序组合效应"],
        "proposal": "2.1 领域本体 + 2.2.2 集成学习",
        "terms": ["RF", "XGBoost", "缺陷率", "集成学习"],
        "resources": [
            "XGBoost 文档：https://xgboost.readthedocs.io/",
            "[L4 §2.5](../02-知识域/L4-机器学习与可靠性预测.md)",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/31-精密电气元件量产缺陷率预测与故障诊断.pdf",
    },
    32: {
        "summary": "Wiener 稳健建模处理加速退化试验中的多源不确定性，估计 RUL。",
        "domains": ["L4"],
        "before": ["随机过程基础", "剩余寿命概念"],
        "after": ["理解 Wiener 退化模型", "掌握多源不确定性处理思路"],
        "proposal": "2.2.2 时序对比学习寿命预测",
        "terms": ["Wiener", "RUL", "加速退化", "PHM"],
        "resources": [
            "[L4 §2.4 Wiener](../02-知识域/L4-机器学习与可靠性预测.md)",
            "检索 'Wiener process degradation model tutorial'",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/32-Wiener稳健建模加速退化多源不确定性.pdf",
    },
    33: {
        "summary": "对比判别分析、神经网络与决策树做 LED 封装质量分类。",
        "domains": ["L4", "L5"],
        "before": ["分类算法对比", "本体/实体概念"],
        "after": ["会选择合适分类器", "理解质量实体形式化需求"],
        "proposal": "2.1 质控知识图谱",
        "terms": ["判别分析", "决策树", "神经网络", "质量分类"],
        "resources": [
            "sklearn 分类器对比",
            "[L5 §2.1 KG](../02-知识域/L5-知识图谱-NLP-大模型.md)",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/33-LED封装质量控制判别分析神经网络决策树.pdf",
    },
    34: {
        "summary": "综述工业自动视觉检测应用，含增量学习与 CNN 缺陷检测。",
        "domains": ["L4", "L5", "L6"],
        "before": ["CNN 基础", "迁移学习"],
        "after": ["了解工业视觉 QC 全景", "理解增量学习与图谱更新"],
        "proposal": "2.1.2/2.2.3 大模型+RAG 与图谱增量更新",
        "terms": ["AVI", "CNN", "增量学习", "缺陷检测"],
        "resources": [
            "PyTorch Vision 教程",
            "[L4 §2.2 CNN](../02-知识域/L4-机器学习与可靠性预测.md)",
        ],
        "pdf": "资料/参考文献/04-风险识别与预测/34-工业自动视觉检测应用.pdf",
    },
}

DOMAIN_LINKS = {
    "L1": "../../02-知识域/L1-数据标准与工业互联网.md",
    "L2": "../../02-知识域/L2-数据治理与异常处理.md",
    "L3": "../../02-知识域/L3-综合评价与决策方法.md",
    "L4": "../../02-知识域/L4-机器学习与可靠性预测.md",
    "L5": "../../02-知识域/L5-知识图谱-NLP-大模型.md",
    "L6": "../../02-知识域/L6-平台工程与闭环系统.md",
}

CARD_NUMBERS = [
    1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 15, 16,
    17, 18, 19, 20, 21, 22, 23, 24, 25,
    26, 27, 28, 29, 30, 31, 32, 33, 34,
]


def parse_note(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m_num = re.search(r"# \[(\d+)\]", text)
    num = int(m_num.group(1)) if m_num else 0
    title_cn = re.sub(r"# \[\d+\]\s*", "", text.split("\n")[0]).strip()
    title_en = ""
    doi = ""
    venue = ""
    for line in text.split("\n"):
        if line.startswith("- **题目**"):
            title_en = line.split("：", 1)[-1].strip()
        elif line.startswith("- **DOI**"):
            doi = line.split("：", 1)[-1].strip()
        elif line.startswith("- **出处**"):
            venue = line.split("：", 1)[-1].strip()
    assoc = ""
    if "## 与本项目的关联" in text:
        assoc = text.split("## 与本项目的关联", 1)[1].strip()
        assoc = re.sub(r"\n## .*", "", assoc, flags=re.DOTALL).strip()
    return {
        "num": num,
        "title_cn": title_cn,
        "title_en": title_en,
        "doi": doi,
        "venue": venue,
        "association": assoc,
    }


def find_note(num: int) -> Path | None:
    for sub in NOTES.iterdir():
        if not sub.is_dir():
            continue
        for f in sub.glob(f"{num:02d}-*.md"):
            if "重复" in f.name and num != 30:
                continue
            return f
    return None


def card_dir(num: int) -> str:
    if num <= 7:
        return "01-数据标准化"
    if num <= 16:
        return "02-数据治理与增强"
    if num <= 25:
        return "03-数据评价"
    return "04-风险识别与预测"


def slug_from_note(path: Path) -> str:
    name = path.stem  # e.g. 08-RANSAC...
    return name.split("-", 1)[1] if "-" in name else name


def fix_md_links(text: str) -> str:
    """卡片在 03-论文学习卡片/{subdir}/ 下，修正相对路径。"""
    return (
        text.replace("](../02-知识域/", "](../../02-知识域/")
        .replace("](../01-术语词典.md", "](../../01-术语词典.md")
        .replace("](../00-总览", "](../../00-总览")
        .replace("](../../项目工作通俗介绍.md", "](../../../项目工作通俗介绍.md")
    )


def render_card(num: int, note: dict, meta: dict, note_path: Path) -> str:
    domains = meta["domains"]
    domain_lines = "\n".join(
        f"- [x] [{d} {d}](../02-知识域/L{d}-{'数据标准与工业互联网' if d=='L1' else '数据治理与异常处理' if d=='L2' else '综合评价与决策方法' if d=='L3' else '机器学习与可靠性预测' if d=='L4' else '知识图谱-NLP-大模型' if d=='L5' else '平台工程与闭环系统'}.md)"
        for d in domains
    )
    # fix domain links properly
    domain_lines = "\n".join(f"- [x] [{d}]({DOMAIN_LINKS[d]})" for d in domains)
    before = "\n".join(f"- {b}" for b in meta["before"])
    after = "\n".join(f"- {a}" for a in meta["after"])
    terms = "、".join(f"`{t}`" for t in meta["terms"])
    resources = "\n".join(f"{i+1}. {fix_md_links(r)}" for i, r in enumerate(meta["resources"]))
    pdf_line = meta.get("pdf_note", f"`{meta['pdf']}`")
    if not meta.get("pdf_note"):
        pdf_line = f"`{meta['pdf']}`"
    extra = meta.get("extra", "")
    assoc = note.get("association", "")
    assoc_block = "\n".join(f"- {line.lstrip('- ')}" for line in assoc.split("\n") if line.strip()) if assoc else f"- {meta['proposal']}"

    return f"""# [{num:02d}] {note['title_cn']}

## 1. 基本信息

| 字段 | 内容 |
|---|---|
| 编号 | [{num}] |
| 中文题名 | {note['title_cn']} |
| 英文题名 | {note.get('title_en') or '—'} |
| 出处 | {note.get('venue') or '—'} |
| DOI | {note.get('doi') or '—'} |
| 本地 PDF | {pdf_line} |
| 原笔记 | [日志/论文整理](../../../论文整理/{card_dir(num)}/{note_path.name}) |

{extra}

---

## 2. 一句话摘要

{meta['summary']}

---

## 3. 本文用到的知识点

{domain_lines}

---

## 4. 读本文前建议先学

{before}

---

## 5. 读完后应掌握

{after}

---

## 6. 申报书关联

{assoc_block}

---

## 7. 术语速查

{terms} → 详见 [01-术语词典](../../01-术语词典.md)

---

## 8. 推荐补学资源

{resources}

---

## 9. 相关链接

- 论文总览：[00-论文总览](../../../论文整理/00-论文总览.md)
- 目录总览：[00-总览](../../00-总览.md)
"""


def main():
    created = []
    for num in CARD_NUMBERS:
        note_path = find_note(num)
        if not note_path:
            print(f"SKIP {num}: note not found")
            continue
        note = parse_note(note_path)
        meta = META[num]
        slug = slug_from_note(note_path)
        out_dir = OUT / card_dir(num)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{num:02d}-{slug}.md"
        content = render_card(num, note, meta, note_path)
        out_file.write_text(content, encoding="utf-8")
        created.append(str(out_file.relative_to(OUT.parent)))
        print(f"OK {out_file.name}")

    # index
    index = OUT / "00-论文索引.md"
    lines = [
        "# 论文索引",
        "",
        "> 共 33 张学习卡片（[14] 与 [13] 重复；[30] 指向 [3]；[6] PDF 待补）",
        "> 按申报书章节对应关系见 [00-总览](../00-总览.md)。",
        "",
    ]
    for dname in ["01-数据标准化", "02-数据治理与增强", "03-数据评价", "04-风险识别与预测"]:
        lines.append(f"## {dname}")
        lines.append("")
        sub = OUT / dname
        for f in sorted(sub.glob("*.md")):
            num = int(f.name[:2])
            title = META[num]["summary"][:40] + "…"
            lines.append(f"- **[{num:02d}]** [{f.stem}]({dname}/{f.name}) — {title}")
        lines.append("")
    index.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nIndex: {index}")
    print(f"Created {len(created)} cards")


if __name__ == "__main__":
    main()
