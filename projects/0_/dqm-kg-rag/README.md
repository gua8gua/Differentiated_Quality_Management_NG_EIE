# dqm-kg-rag

质控知识图谱与 GraphRAG 服务项目，对应核心工作二。

## 目标

- 构建 50-100 个实体规模的质控知识图谱种子数据。
- 支持从 CSV 三元组导入本地图谱。
- 输入异常现象，输出根因追溯路径。
- 提供 FastAPI 接口给 `dqm-platform` 调用。

## 工作流程与模块

| 阶段 | 模块 | 职责 |
|---|---|---|
| 01 本体定义 | `ontology/catalog.py` | 定义装备对象、软件对象、元器件状态、质量现象、质量指标、处置措施等实体类型，以及影响、导致、可能原因等关系类型 |
| 02 数据导入 | `importers/csv_importer.py` | 从 CSV 读取三元组，并校验必需字段 |
| 03 图谱存储 | `store.py` | 构建内存图谱、输出节点边、执行图谱校验 |
| 04 根因推理 | `reasoning/tracing.py` | 从异常现象出发，沿图谱路径追溯原因与处置措施 |
| 05 RAG 解释 | `rag.py` | 融合风险等级、证据与追溯路径，生成解释文本 |
| 06 工作流编排 | `workflow.py` | 串联本体、导入校验、追溯、解释四个阶段，输出阶段结果 |
| 07 API 服务 | `api.py` | 对外提供图谱、追溯、解释、工作流接口 |
| 08 关系型持久化 | `persistence/relational.py` | SQLite 建表、外键/唯一约束、三元组插入、统计查询 |
| 09 图数据库持久化 | `persistence/graph.py` | Neo4j 唯一约束、本体节点插入、质量实体和关系 MERGE |

## 快速开始

```powershell
cd projects/0_/dqm-kg-rag
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn dqm_kg_rag.api:app --reload --port 8010
```

## 接口

- `GET /health`
- `GET /graph`
- `GET /ontology`
- `GET /validate`
- `POST /trace`
- `POST /explain`
- `POST /workflow`

## 示例请求

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8010/workflow `
  -ContentType "application/json" `
  -Body '{"phenomenon":"接收通道噪声升高","risk_level":"中","evidence":["SNR下降"]}'
```

## 关系型数据库：SQLite

默认数据库文件：

`data/quality_kg.sqlite`

建表和约束：

```powershell
cd projects/0_/dqm-kg-rag
python -m dqm_kg_rag.cli init-sqlite --db data/quality_kg.sqlite
```

插入种子三元组：

```powershell
python -m dqm_kg_rag.cli import-sqlite --db data/quality_kg.sqlite --triples data/seed_triples/quality_triples.csv
```

查看统计：

```powershell
python -m dqm_kg_rag.cli sqlite-stats --db data/quality_kg.sqlite
```

SQLite 约束包括：

- `entity_types.name` 主键。
- `relation_types.name` 主键。
- `entities(name, type)` 唯一约束。
- `triples(head_id, relation, tail_id)` 唯一约束。
- `triples.head_id / tail_id / relation` 外键约束。
- `quality_cases.risk_level` CHECK 约束：`低 / 中 / 高`。

## 图数据库：Neo4j

安装依赖：

```powershell
pip install -e .
```

建立 Neo4j 约束：

```powershell
python -m dqm_kg_rag.cli neo4j-constraints --uri bolt://localhost:7687 --username neo4j --password password --database neo4j
```

插入三元组：

```powershell
python -m dqm_kg_rag.cli import-neo4j --uri bolt://localhost:7687 --username neo4j --password password --database neo4j --triples data/seed_triples/quality_triples.csv
```

Neo4j 写入模型：

- 节点：`:QualityEntity {name, type}`
- 关系：`:QUALITY_RELATION {relation, description, source}`
- 本体类型节点：`:EntityType`、`:RelationType`

Neo4j 约束包括：

- `QualityEntity(name, type)` 复合唯一约束。
- `EntityType.name` 唯一约束。
- `RelationType.name` 唯一约束。

