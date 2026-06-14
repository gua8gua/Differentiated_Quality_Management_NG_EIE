import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface WorkflowPanelProps {
  workflow: NonNullable<DashboardData["workflow"]>;
}

export function WorkflowPanel({ workflow }: WorkflowPanelProps) {
  return (
    <section className="card">
      <h2>平台工作流</h2>
      <div className="workflow">
        {workflow.map((item) => (
          <article key={item.stage}>
            <span>{item.stage}</span>
            <strong>{item.project}</strong>
            <p>{item.output}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

