import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface GraphTraceCardProps {
  graphTrace: DashboardData["graphTrace"];
}

export function GraphTraceCard({ graphTrace }: GraphTraceCardProps) {
  return (
    <article className="card">
      <h2>图谱根因追溯</h2>
      <p className="highlight">{graphTrace.phenomenon}</p>
      {graphTrace.paths.map((path) => (
        <div className="path" key={path.join("-")}>
          {path.map((node, index) => (
            <span key={`${node}-${index}`}>
              {node}
              {index < path.length - 1 ? " → " : ""}
            </span>
          ))}
        </div>
      ))}
      <p>{graphTrace.summary}</p>
    </article>
  );
}

