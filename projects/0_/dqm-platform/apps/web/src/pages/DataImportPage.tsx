import { Alert, Button, Form, Input, Select, Upload, message } from "antd";
import { InboxOutlined } from "@ant-design/icons";
import { useEffect, useState } from "react";
import type { DatasetContextForm, MetadataOptions, StreamLogEvent } from "../../../../packages/shared-types/contracts";
import { analyzeDataset, checkApiHealth, fetchMetadataOptions, subscribeJobStream, uploadDataset } from "../services/api";

const { Dragger } = Upload;

const defaultContext: DatasetContextForm = {
  name: "",
  modality: "tabular",
  quality_object: "component",
  use_case: "governance",
  standards: ["project_custom"],
  description: "",
  tags: [],
};

export function DataImportPage() {
  const [form] = Form.useForm<DatasetContextForm & { dataset_type: string }>();
  const [options, setOptions] = useState<MetadataOptions | null>(null);
  const [uploadId, setUploadId] = useState<string>("");
  const [filename, setFilename] = useState<string>("");
  const [jobId, setJobId] = useState<string>("");
  const [logs, setLogs] = useState<StreamLogEvent[]>([]);
  const [status, setStatus] = useState<string>("idle");
  const [apiReady, setApiReady] = useState<boolean | null>(null);

  useEffect(() => {
    checkApiHealth().then(setApiReady);
    fetchMetadataOptions()
      .then(setOptions)
      .catch(() => message.warning("无法加载元数据选项，使用默认值。"));
  }, []);

  async function handleUpload(file: File) {
    try {
      const result = await uploadDataset(file);
      setUploadId(result.upload_id);
      setFilename(result.filename);
      localStorage.setItem("dqm_upload_id", result.upload_id);
      form.setFieldValue("name", file.name.replace(/\.[^.]+$/, ""));
      message.success(result.message);
    } catch {
      message.error("上传失败，请确认 platform API (8020) 已启动。");
    }
    return false;
  }

  async function handleAnalyze() {
    if (!uploadId) {
      message.error("请先上传数据文件。");
      return;
    }
    try {
      const values = await form.validateFields();
      setLogs([]);
      setStatus("running");
      const result = await analyzeDataset(
        uploadId,
        {
          name: values.name,
          modality: values.modality,
          quality_object: values.quality_object,
          use_case: values.use_case,
          standards: values.standards,
          description: values.description,
          tags: values.tags ?? [],
        },
        values.dataset_type,
      );
      setJobId(result.job_id);
      subscribeJobStream(result.job_id, {
        onLog: (event) => setLogs((prev) => [...prev, event]),
        onDone: (payload) => {
          setStatus(String(payload.status ?? "completed"));
          message.success("分析完成，可返回总览页查看结果。");
        },
        onError: () => {
          setStatus("failed");
          message.error("任务日志流连接失败。");
        },
      });
    } catch {
      setStatus("failed");
      message.error("启动分析失败，请检查表单与后端 API。");
    }
  }

  return (
    <main className="page">
      {apiReady === false ? (
        <Alert
          type="warning"
          showIcon
          message="后端 API 未就绪"
          description="请先运行 projects/0_/dqm-platform/start.ps1 或手动启动 platform API (8020)。"
          style={{ marginBottom: 16 }}
        />
      ) : null}

      <section className="card page-intro">
        <h2>数据导入与上下文配置</h2>
        <p>
          上传 CSV/数据文件，并指定所属对象、模态、用途与标准。平台会调用 dqm-data-lab 与 dqm-kg-rag 执行治理、风险摘要和图谱追溯。
        </p>
      </section>

      <section className="grid two">
        <div className="card import-card">
          <h3>1. 上传文件</h3>
          <Dragger beforeUpload={handleUpload} showUploadList={false} accept=".csv,.txt,.json" disabled={apiReady === false}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此处</p>
            <p className="ant-upload-hint">支持 CSV、TXT、JSON；推荐先用 SECOM 样例 CSV</p>
          </Dragger>
          {filename ? <Alert style={{ marginTop: 16 }} type="success" message={`已上传：${filename}`} /> : null}
        </div>

        <div className="card import-card">
          <h3>2. 数据上下文</h3>
          <Form form={form} layout="vertical" initialValues={{ ...defaultContext, dataset_type: "auto" }}>
            <Form.Item name="name" label="数据集名称" rules={[{ required: true }]}>
              <Input placeholder="例如 SECOM 批次-A" />
            </Form.Item>
            <Form.Item name="modality" label="数据模态" rules={[{ required: true }]}>
              <Select options={(options?.modalities ?? ["tabular"]).map((value: string) => ({ value, label: value }))} />
            </Form.Item>
            <Form.Item name="quality_object" label="质量对象" rules={[{ required: true }]}>
              <Select options={(options?.quality_objects ?? ["component"]).map((value: string) => ({ value, label: value }))} />
            </Form.Item>
            <Form.Item name="use_case" label="用途" rules={[{ required: true }]}>
              <Select options={(options?.use_cases ?? ["governance"]).map((value: string) => ({ value, label: value }))} />
            </Form.Item>
            <Form.Item name="standards" label="适用标准">
              <Select mode="multiple" options={(options?.standards ?? ["project_custom"]).map((value: string) => ({ value, label: value }))} />
            </Form.Item>
            <Form.Item name="dataset_type" label="数据集适配器">
              <Select options={(options?.dataset_types ?? ["auto"]).map((value: string) => ({ value, label: value }))} />
            </Form.Item>
            <Form.Item name="description" label="描述">
              <Input.TextArea rows={3} placeholder="补充批次、产线、装备型号等信息" />
            </Form.Item>
            <Button type="primary" onClick={handleAnalyze} loading={status === "running"} disabled={apiReady === false}>
              启动全流程分析
            </Button>
          </Form>
        </div>
      </section>

      <section className="card log-card">
        <h3>3. 运行日志 {jobId ? `(job: ${jobId})` : ""}</h3>
        <div className="log-stream">
          {logs.length === 0 ? <p>上传并启动分析后，这里会实时显示各阶段日志。</p> : null}
          {logs.map((log, index) => (
            <div key={`${log.stage}-${index}`} className="log-item">
              <span>{log.timestamp ?? ""}</span>
              <strong>[{log.stage}]</strong>
              <span>{log.summary}</span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
