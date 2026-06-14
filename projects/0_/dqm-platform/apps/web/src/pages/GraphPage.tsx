import { Button, Input, Select, message } from "antd";
import { useCallback, useEffect, useMemo, useState } from "react";
import { GraphError, GraphLegend, GraphLoading, GraphVisualization } from "../components/GraphVisualization";
import type { GraphData } from "../../../../packages/shared-types/contracts";
import { fetchGraph, traceGraph } from "../services/api";

export function GraphPage() {
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [source, setSource] = useState<"kg-rag" | "platform">("platform");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [phenomenon, setPhenomenon] = useState("");
  const [highlightNodes, setHighlightNodes] = useState<Set<string>>(new Set());
  const [highlightEdges, setHighlightEdges] = useState<Set<string>>(new Set());
  const [traceSummary, setTraceSummary] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchGraph()
      .then(({ data, source: graphSource }) => {
        setGraph(data);
        setSource(graphSource);
        const firstPhenomenon = data.nodes.find((node) => node.type === "质量现象")?.id ?? data.nodes[0]?.id ?? "";
        setPhenomenon(firstPhenomenon);
        setError("");
      })
      .catch(() => {
        setError("请确认 dqm-kg-rag (8010) 或 platform API (8020) 已启动。");
      })
      .finally(() => setLoading(false));
  }, []);

  const phenomenaOptions = useMemo(
    () =>
      (graph?.nodes.filter((node) => node.type === "质量现象") ?? []).map((node) => ({
        value: node.id,
        label: node.label || node.id,
      })),
    [graph],
  );

  const runTrace = useCallback(async () => {
    if (!phenomenon) {
      message.warning("请先选择质量现象。");
      return;
    }
    try {
      const result = (await traceGraph(phenomenon)) as {
        paths?: Array<{ nodes: string[]; relations?: string[] }>;
        recommended_actions?: string[];
      };
      const nodes = new Set<string>();
      const edges = new Set<string>();
      (result.paths ?? []).forEach((path) => {
        path.nodes.forEach((node) => nodes.add(node));
        path.nodes.slice(0, -1).forEach((node, index) => {
          edges.add(`${node}->${path.nodes[index + 1]}:${path.relations?.[index] ?? ""}`);
        });
      });
      setHighlightNodes(nodes);
      setHighlightEdges(edges);
      setTraceSummary(result.recommended_actions?.[0] ?? "已完成路径追溯。");
    } catch {
      message.error("追溯失败，请检查现象名称或服务是否可用。");
    }
  }, [phenomenon]);

  return (
    <main className="page graph-page">
      <section className="card page-intro">
        <h2>质控知识图谱</h2>
        <p>调用 dqm-kg-rag 已有 API（GET /graph、POST /trace）以力导向图展示节点关系，并高亮根因追溯路径。</p>
        {graph ? <GraphLegend source={source} nodeCount={graph.nodes.length} edgeCount={graph.edges.length} /> : null}
        <div className="graph-toolbar">
          <Select
            style={{ minWidth: 280 }}
            value={phenomenon || undefined}
            onChange={setPhenomenon}
            options={phenomenaOptions}
            placeholder="选择质量现象"
            disabled={!graph}
          />
          <Input
            style={{ width: 280 }}
            value={phenomenon}
            onChange={(event) => setPhenomenon(event.target.value)}
            placeholder="或直接输入现象节点 ID"
          />
          <Button type="primary" onClick={runTrace} disabled={!graph}>
            追溯根因路径
          </Button>
        </div>
        {traceSummary ? <p className="trace-summary">{traceSummary}</p> : null}
      </section>

      <section className="card graph-canvas">
        {loading ? <GraphLoading /> : null}
        {!loading && error ? <GraphError message={error} /> : null}
        {!loading && graph ? (
          <GraphVisualization graph={graph} highlightNodes={highlightNodes} highlightEdges={highlightEdges} />
        ) : null}
      </section>
    </main>
  );
}
