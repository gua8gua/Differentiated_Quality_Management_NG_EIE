# dqm-data-lab

质量数据治理与评价实验项目，对应核心工作一。

## 目标

- 读取 `datasets/01_tabular_secom`、`datasets/03_phm_nasa_cmapss`、`datasets/08_synthetic_mcdm`。
- 完成缺失值统计、缺失填充、标准化、异常检测、特征筛选。
- 输出平台可展示的质量报告 JSON。
- 提供基础风险检测结果，供 `dqm-kg-rag` 和 `dqm-platform` 使用。
- 通过数据上下文和适配器机制，支持不同模态、标准、对象和用途的数据接入。

## 可扩展接口

### 数据上下文

`DatasetContext` 描述每批数据的工程语义：

| 字段 | 说明 | 示例 |
|---|---|---|
| `modality` | 数据模态 | `tabular`、`timeseries`、`image`、`text`、`audio`、`multimodal` |
| `quality_object` | 质量对象 | `whole_equipment`、`software`、`component`、`process` |
| `use_case` | 使用目的 | `governance`、`quality_evaluation`、`anomaly_detection`、`risk_prediction` |
| `standards` | 对齐标准 | `ISO8000`、`GB_T_34960_5`、`IEC62424`、`project_custom` |

### 数据集适配器

当前内置适配器：

| 适配器 | 数据目录 | 模态 | 用途 |
|---|---|---|---|
| `secom` | `datasets/01_tabular_secom` | 表格 | 元器件/过程质量治理与异常检测 |
| `cmapss` | `datasets/03_phm_nasa_cmapss` | 时序 | 退化数据治理与风险预测 |
| `mcdm` | `datasets/08_synthetic_mcdm` | 表格 | 多准则质量评价 |

后续新增图像、文本、声学等模态时，只需实现 `DatasetAdapter.load()` 并注册到 `registry.py`。

## 治理与清洗阶段模块

当前基础治理管线已经拆成独立阶段，后续可按阶段替换算法：

| 阶段 | 模块 | 职责 | 当前基础实现 |
|---|---|---|---|
| 01 | `stages/profiling.py` | 数据资产剖析 | 行列数、数值列数、缺失率、高缺失字段 |
| 02 | `stages/standardization.py` | 标准化 | 字段命名规范化，记录模态/对象/用途/标准 |
| 03 | `stages/standardization.py` | 数值指标选择 | 提取数值列，非数值模态等待专用特征适配器 |
| 04 | `stages/cleaning.py` | 缺失清洗 | 中位数填补 |
| 05 | `stages/cleaning.py` | 量纲统一 | Z-score 标准化 |
| 06 | `stages/anomaly.py` | 异常检测 | IsolationForest |
| 07 | `stages/feature_selection.py` | 特征筛选 | 随机森林重要性或方差筛选 |
| 08 | `stages/evaluation.py` | 质量评价 | 完整性、异常可控性、可建模性、一致性加权评分 |
| 09 | `stages/reporting.py` | 报告输出 | `data_quality_report.json`、`risk_summary.json` |

每个阶段返回 `GovernanceStageResult`，会写入 `data_quality_report.json` 的 `stage_results` 字段，方便平台展示治理过程。

## 快速开始

```powershell
cd projects/0_/dqm-data-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m dqm_data_lab run --dataset ../../../datasets/01_tabular_secom --dataset-type secom --name SECOM --quality-object component --use-case governance --standards ISO8000,project_custom --out reports
```

自动识别数据集类型：

```powershell
python -m dqm_data_lab run --dataset ../../../datasets/03_phm_nasa_cmapss --dataset-type auto --name "C-MAPSS FD001" --modality timeseries --quality-object component --use-case risk_prediction --out reports_cmapss
```

## 输出

- `reports/data_quality_report.json`：数据治理与质量评价报告。
- `reports/risk_summary.json`：基础异常检测 / 风险分类摘要。

