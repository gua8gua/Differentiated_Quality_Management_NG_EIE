import type {
  AnalyzeResponse,
  ChatMessage,
  DashboardData,
  DatasetContextForm,
  GraphData,
  MetadataOptions,
  RealtimeMetric,
  StreamLogEvent,
  UploadResponse,
} from "../../../../packages/shared-types/contracts";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const KG_BASE = import.meta.env.VITE_KG_BASE ?? "/kg";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

async function kgRequest<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const response = await fetch(`${KG_BASE}${path}`, { ...init, signal: AbortSignal.timeout(3000) });
    if (!response.ok) return null;
    return response.json() as Promise<T>;
  } catch {
    return null;
  }
}

export async function fetchMetadataOptions(): Promise<MetadataOptions> {
  return request<MetadataOptions>("/metadata/options");
}

export async function uploadDataset(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_BASE}/datasets/upload`, { method: "POST", body: form });
  if (!response.ok) {
    throw new Error("上传失败");
  }
  return response.json();
}

export async function analyzeDataset(
  uploadId: string,
  context: DatasetContextForm,
  datasetType = "auto",
): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>("/datasets/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ upload_id: uploadId, context, dataset_type: datasetType }),
  });
}

/** 优先调用 dqm-kg-rag GET /graph，失败时回退 platform API */
export async function fetchGraph(): Promise<{ data: GraphData; source: "kg-rag" | "platform" }> {
  const kgGraph = await kgRequest<GraphData>("/graph");
  if (kgGraph?.nodes?.length) {
    return { data: kgGraph, source: "kg-rag" };
  }
  const platformGraph = await request<GraphData>("/graph");
  return { data: platformGraph, source: "platform" };
}

/** 优先调用 dqm-kg-rag POST /trace，失败时回退 platform API */
export async function traceGraph(phenomenon: string, maxDepth = 3) {
  const kgTrace = await kgRequest("/trace", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phenomenon, max_depth: maxDepth }),
  });
  if (kgTrace) return kgTrace;

  return request("/graph/trace", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phenomenon, max_depth: maxDepth }),
  });
}

export function subscribeJobStream(
  jobId: string,
  handlers: {
    onLog: (event: StreamLogEvent) => void;
    onDone: (payload: Record<string, unknown>) => void;
    onError?: (error: Error) => void;
  },
) {
  const source = new EventSource(`${API_BASE}/jobs/${jobId}/stream`);
  source.addEventListener("log", (event) => handlers.onLog(JSON.parse(event.data)));
  source.addEventListener("done", (event) => {
    handlers.onDone(JSON.parse(event.data));
    source.close();
  });
  source.onerror = () => {
    handlers.onError?.(new Error("任务流连接中断"));
    source.close();
  };
  return source;
}

export async function sendChatMessage(message: string, sessionId?: string, uploadId?: string) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, upload_id: uploadId }),
  });
  if (!response.ok || !response.body) {
    throw new Error("Agent 对话请求失败");
  }
  return response.body.getReader();
}

export function parseSseChunk(
  chunk: string,
  handlers: {
    onLog?: (event: StreamLogEvent) => void;
    onMessage?: (message: ChatMessage & { session_id?: string }) => void;
    onDone?: (payload: Record<string, unknown>) => void;
    onMetric?: (metric: RealtimeMetric) => void;
  },
) {
  const blocks = chunk.split("\n\n").filter(Boolean);
  for (const block of blocks) {
    const lines = block.split("\n");
    const eventLine = lines.find((line) => line.startsWith("event:"));
    const dataLine = lines.find((line) => line.startsWith("data:"));
    if (!eventLine || !dataLine) continue;
    const event = eventLine.replace("event:", "").trim();
    const data = JSON.parse(dataLine.replace("data:", "").trim());
    if (event === "log") handlers.onLog?.(data);
    if (event === "message") handlers.onMessage?.(data);
    if (event === "done") handlers.onDone?.(data);
    if (event === "metric") handlers.onMetric?.(data);
  }
}

export function subscribeRealtimeMetrics(onMetric: (metric: RealtimeMetric) => void) {
  const source = new EventSource(`${API_BASE}/realtime/stream`);
  source.addEventListener("metric", (event) => onMetric(JSON.parse(event.data)));
  source.onerror = () => source.close();
  return source;
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2000) });
    return response.ok;
  } catch {
    return false;
  }
}

export async function fetchDashboardData(): Promise<{ data: DashboardData; source: "api" | "mock" }> {
  try {
    const response = await fetch(`${API_BASE}/dashboard`, { signal: AbortSignal.timeout(2500) });
    if (!response.ok) throw new Error("API unavailable");
    return { data: (await response.json()) as DashboardData, source: "api" };
  } catch {
    const module = await import("../../../../mock-data/dashboard.json");
    return { data: module.default as DashboardData, source: "mock" };
  }
}
