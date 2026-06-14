import { Alert, Button, Input, Tag, message } from "antd";
import * as echarts from "echarts";
import { useEffect, useRef, useState } from "react";
import type { ChatMessage, RealtimeMetric, StreamLogEvent } from "../../../../packages/shared-types/contracts";
import { checkApiHealth, parseSseChunk, sendChatMessage, subscribeRealtimeMetrics } from "../services/api";

const quickPrompts = [
  "当前风险等级是多少？",
  "给出图谱根因路径摘要",
  "三类智能体建议是什么？",
  "分析上传文件",
];

export function AgentPage() {
  const [sessionId, setSessionId] = useState<string>();
  const [uploadId, setUploadId] = useState<string>(() => localStorage.getItem("dqm_upload_id") ?? "");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [logs, setLogs] = useState<StreamLogEvent[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [apiReady, setApiReady] = useState<boolean | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const metricsRef = useRef<RealtimeMetric[]>([]);

  useEffect(() => {
    checkApiHealth().then(setApiReady);
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;
    chartInstance.current = echarts.init(chartRef.current);
    const resize = () => chartInstance.current?.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      chartInstance.current?.dispose();
    };
  }, []);

  useEffect(() => {
    if (!apiReady) return;
    const source = subscribeRealtimeMetrics((metric) => {
      metricsRef.current = [...metricsRef.current.slice(-30), metric];
      const labels = metricsRef.current.map((item) => item.tick);
      chartInstance.current?.setOption({
        title: { text: "实时质量指标模拟", left: "center", textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis" },
        legend: { top: 28, data: ["质量评分", "异常率(×100)", "传感器值"] },
        grid: { top: 70, left: 40, right: 20, bottom: 30 },
        xAxis: { type: "category", data: labels },
        yAxis: { type: "value" },
        series: [
          { name: "质量评分", type: "line", smooth: true, data: metricsRef.current.map((item) => item.qualityScore) },
          { name: "异常率(×100)", type: "line", smooth: true, data: metricsRef.current.map((item) => item.anomalyRate * 100) },
          { name: "传感器值", type: "line", smooth: true, data: metricsRef.current.map((item) => item.sensorValue) },
        ],
      });
    });
    return () => source.close();
  }, [apiReady]);

  async function handleSend(text: string) {
    if (!text.trim() || streaming) return;
    if (!apiReady) {
      message.error("请先启动 platform API (8020)。");
      return;
    }

    setStreaming(true);
    setMessages((prev) => [...prev, { role: "user", content: text, timestamp: new Date().toISOString() }]);
    setInput("");

    try {
      const reader = await sendChatMessage(text, sessionId, uploadId || undefined);
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() ?? "";
        for (const part of parts) {
          parseSseChunk(`${part}\n\n`, {
            onLog: (event) => setLogs((prev) => [...prev, event]),
            onMessage: (payload) => {
              setMessages((prev) => [...prev, { role: payload.role, content: payload.content, timestamp: new Date().toISOString() }]);
              if (payload.session_id) setSessionId(payload.session_id);
            },
            onDone: (payload) => {
              if (payload.session_id) setSessionId(String(payload.session_id));
            },
          });
        }
      }
    } catch {
      message.error("Agent 对话失败，请确认后端 API 已启动。");
    } finally {
      setStreaming(false);
    }
  }

  return (
    <main className="page agent-page">
      {apiReady === false ? (
        <Alert
          type="warning"
          showIcon
          message="后端 API 未就绪"
          description="请先运行 start.ps1 启动 platform API，再进行 Agent 对话。"
          style={{ marginBottom: 16 }}
        />
      ) : null}

      <section className="grid two">
        <div className="card chat-card">
          <h2>LangGraph 质量管控 Agent</h2>
          <p>支持问答、日志输出与「分析上传文件」触发全流程。配置 OPENAI_API_KEY 后启用大模型回复。</p>
          <div className="quick-prompts">
            {quickPrompts.map((prompt) => (
              <Button key={prompt} size="small" onClick={() => handleSend(prompt)} disabled={!apiReady}>
                {prompt}
              </Button>
            ))}
          </div>
          <div className="chat-box">
            {messages.length === 0 ? <p className="chat-placeholder">发送问题开始对话，或点击上方快捷提示。</p> : null}
            {messages.map((item, index) => (
              <div key={`${item.role}-${index}`} className={`chat-bubble ${item.role}`}>
                <Tag color={item.role === "user" ? "blue" : "green"}>{item.role}</Tag>
                <pre>{item.content}</pre>
              </div>
            ))}
          </div>
          <div className="chat-input-row">
            <Input
              value={uploadId}
              onChange={(event) => {
                setUploadId(event.target.value);
                localStorage.setItem("dqm_upload_id", event.target.value);
              }}
              placeholder="可选：填入 upload_id 后发送「分析上传文件」"
            />
            <Input.Search
              value={input}
              onChange={(event) => setInput(event.target.value)}
              enterButton="发送"
              loading={streaming}
              disabled={!apiReady}
              onSearch={(value) => handleSend(value)}
              placeholder="输入问题，或发送「分析上传文件」"
            />
          </div>
        </div>

        <div className="card log-card">
          <h3>Agent / 流水线日志</h3>
          <div className="log-stream tall">
            {logs.length === 0 ? <p>对话与流水线事件会显示在这里。</p> : null}
            {logs.map((log, index) => (
              <div key={`${log.stage}-${index}`} className="log-item">
                <span>{log.timestamp ?? ""}</span>
                <strong>[{log.stage}]</strong>
                <span>{log.summary}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="card realtime-card">
        <div ref={chartRef} className="realtime-chart" />
      </section>
    </main>
  );
}
