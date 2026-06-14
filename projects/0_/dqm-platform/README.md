# dqm-platform

统一展示与后端聚合平台，对应最终演示系统。

## 目标

- 展示项目任务、总体技术路线、三项核心工作与两大申报书创新点。
- 展示 `dqm-data-lab` 输出的数据治理报告。
- 展示 `dqm-kg-rag` 输出的图谱节点、根因路径与 RAG 解释。
- 用 mock JSON 展示风险预测、RUL、DTW 相似片段和三类智能体协同。

## 工作流程与模块

### 后端 API

| 模块 | 职责 |
|---|---|
| `apps/api/services.py` | 读取 mock dashboard 数据、按 section 提供数据、输出平台工作流 |
| `apps/api/main.py` | FastAPI 入口，提供健康检查、dashboard、分区数据和 workflow 接口 |

接口：

- `GET /health`
- `GET /dashboard`
- `GET /dashboard/{section_name}`
- `GET /workflow`

### 前端 Web

| 模块 | 职责 |
|---|---|
| `src/services/dashboard.ts` | 加载 dashboard mock 数据并提供格式化函数 |
| `src/components/Hero.tsx` | 项目总览头图 |
| `src/components/CoreWorks.tsx` | 三项核心工作 |
| `src/components/WorkflowPanel.tsx` | 数据治理、图谱追溯、风险 mock、智能体 mock 的平台工作流 |
| `src/components/DataQualityCard.tsx` | 数据治理结果 |
| `src/components/GraphTraceCard.tsx` | 图谱根因追溯 |
| `src/components/RiskPredictionCard.tsx` | 风险预测 mock |
| `src/components/RulCard.tsx` | RUL 曲线数据 |
| `src/components/AgentPanel.tsx` | 三类智能体协同 |

### Mock 数据

`mock-data/dashboard.json` 统一承载：

- `overview`
- `dataQuality`
- `graphTrace`
- `riskPrediction`
- `workflow`
- `agents`

## 页面与功能

| 路由 | 功能 |
|------|------|
| `/` | 总览 Dashboard：治理结果、风险预测、智能体协同 |
| `/import` | **数据导入**：上传 CSV，配置模态/对象/用途/标准，SSE 实时日志 |
| `/graph` | **知识图谱**：ReactFlow 可视化，根因路径高亮 |
| `/agent` | **Agent 协同**：LangGraph 对话、流水线日志、ECharts 实时指标模拟 |

### 数据导入需填写的上下文

| 字段 | 说明 | 可选值示例 |
|------|------|-----------|
| 数据集名称 | 业务标识 | SECOM 批次-A |
| 数据模态 | 数据类型 | tabular / timeseries / image / text … |
| 质量对象 | 管控对象 | component / process / whole_equipment / software |
| 用途 | 分析目标 | governance / risk_prediction / anomaly_detection … |
| 适用标准 | 质量规范 | ISO8000 / GB_T_34960_5 / project_custom |
| 数据集适配器 | 解析方式 | auto / generic_csv / secom / cmapss |

### Agent 与大模型

- 默认使用 **LangGraph + 规则/mock 回复**（无需 API Key）
- 配置环境变量后启用 OpenAI 大模型：

```powershell
$env:OPENAI_API_KEY = "your-key"
$env:OPENAI_MODEL = "gpt-4o-mini"
```

### 新增 API

```
GET  /metadata/options
POST /datasets/upload
POST /datasets/analyze
GET  /jobs/{job_id}
GET  /jobs/{job_id}/stream      # SSE
GET  /graph
POST /graph/trace
POST /chat                      # SSE 流式对话
GET  /chat/{session_id}/history
GET  /realtime/stream           # SSE 实时指标模拟
```

## 快速开始

### 方式一：一键启动（推荐）

```powershell
cd projects/0_/dqm-platform
.\start.ps1
```

脚本会打开两个窗口：

- 后端 API：`http://127.0.0.1:8020`（Swagger：`http://127.0.0.1:8020/docs`）
- 前端页面：`http://127.0.0.1:5173`

浏览器访问 **http://127.0.0.1:5173** 即可查看完整演示页面。

若只想启动其中一项：

```powershell
.\start.ps1 -WebOnly   # 仅前端（读取本地 mock-data/dashboard.json）
.\start.ps1 -ApiOnly   # 仅后端 API
```

### 方式二：手动启动

前端 Web：

```powershell
cd projects/0_/dqm-platform/apps/web
npm install
npm run dev
```

启动后访问：**http://127.0.0.1:5173**

后端聚合 API：

```powershell
cd projects/0_/dqm-platform/apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8020
```

### 页面包含什么

演示页面为 React 单页应用，展示：

- 项目总览与三项核心工作
- 数据治理结果（SECOM 样例）
- 知识图谱根因追溯
- 风险预测、RUL、DTW 相似片段
- 三类智能体协同、处置报告、反馈评价

数据来源：

1. 先运行 `projects/0_/run_full_flow.py` 生成最新 `mock-data/dashboard.json`
2. 前端优先请求 API `/dashboard`；若 API 未启动则自动回退到本地 mock 文件

### 生产预览

```powershell
cd projects/0_/dqm-platform/apps/web
npm run build
npm run preview
```

预览地址默认为 **http://127.0.0.1:4173**

