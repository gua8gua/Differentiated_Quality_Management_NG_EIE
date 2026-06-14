import { Alert, Spin, Tag } from "antd";
import * as echarts from "echarts";
import { useEffect, useMemo, useRef } from "react";
import type { GraphData } from "../../../../packages/shared-types/contracts";

const typeColors: Record<string, string> = {
  质量现象: "#f6bd60",
  质量原因: "#84a59d",
  质量指标: "#f28482",
  装备对象: "#9db4f0",
  处置策略: "#b8c0ff",
  过程状态: "#90dbf4",
  失效机理: "#cdb4db",
  未知: "#d8e2ec",
};

interface GraphVisualizationProps {
  graph: GraphData;
  highlightNodes: Set<string>;
  highlightEdges?: Set<string>;
}

export function GraphVisualization({ graph, highlightNodes, highlightEdges }: GraphVisualizationProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  const categories = useMemo(() => {
    const types = [...new Set(graph.nodes.map((node) => node.type || "未知"))];
    return types.map((name) => ({ name }));
  }, [graph.nodes]);

  const option = useMemo(() => {
    const categoryIndex = new Map(categories.map((item, index) => [item.name, index]));
    return {
      tooltip: {
        formatter: (params: { dataType?: string; data?: { id?: string; label?: string; relation?: string } }) => {
          if (params.dataType === "edge") {
            return `${params.data?.label ?? ""}`;
          }
          return `${params.data?.id ?? ""}`;
        },
      },
      legend: [{ data: categories.map((item) => item.name), top: 0 }],
      series: [
        {
          type: "graph",
          layout: "force",
          roam: true,
          draggable: true,
          focusNodeAdjacency: true,
          label: {
            show: true,
            position: "right",
            fontSize: 11,
            formatter: (params: { data?: { id?: string } }) => {
              const id = params.data?.id ?? "";
              return id.length > 12 ? `${id.slice(0, 12)}…` : id;
            },
          },
          force: {
            repulsion: 260,
            edgeLength: [80, 160],
            gravity: 0.08,
          },
          categories,
          data: graph.nodes.map((node) => {
            const type = node.type || "未知";
            const highlighted = highlightNodes.has(node.id);
            return {
              id: node.id,
              name: node.id,
              category: categoryIndex.get(type) ?? 0,
              symbolSize: highlighted ? 42 : 24,
              itemStyle: {
                color: typeColors[type] ?? "#fff",
                borderColor: highlighted ? "#c1121f" : "#94a3b8",
                borderWidth: highlighted ? 3 : 1,
              },
            };
          }),
          links: graph.edges.map((edge, index) => {
            const edgeKey = `${edge.source}->${edge.target}:${edge.label}`;
            const highlighted = highlightEdges?.has(edgeKey) || highlightNodes.has(edge.source) || highlightNodes.has(edge.target);
            return {
              source: edge.source,
              target: edge.target,
              label: { show: true, formatter: edge.label, fontSize: 10 },
              lineStyle: {
                color: highlighted ? "#c1121f" : "#94a3b8",
                width: highlighted ? 2.5 : 1,
                curveness: 0.15,
              },
            };
          }),
        },
      ],
    };
  }, [graph, categories, highlightNodes, highlightEdges]);

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
    chartInstance.current?.setOption(option, true);
  }, [option]);

  return <div ref={chartRef} className="graph-echart" />;
}

interface GraphLegendProps {
  source: "kg-rag" | "platform";
  nodeCount: number;
  edgeCount: number;
}

export function GraphLegend({ source, nodeCount, edgeCount }: GraphLegendProps) {
  return (
    <div className="graph-meta">
      <Tag color={source === "kg-rag" ? "green" : "gold"}>
        数据源：{source === "kg-rag" ? "dqm-kg-rag /graph" : "platform /graph"}
      </Tag>
      <span>节点 {nodeCount} · 关系 {edgeCount}</span>
    </div>
  );
}

export function GraphLoading() {
  return (
    <div className="graph-loading">
      <Spin size="large" />
      <p>正在从知识图谱 API 加载节点关系…</p>
    </div>
  );
}

export function GraphError({ message }: { message: string }) {
  return <Alert type="error" showIcon message="图谱加载失败" description={message} />;
}
