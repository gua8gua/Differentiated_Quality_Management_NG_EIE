import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface AgentPanelProps {
  agents: DashboardData["agents"];
}

export function AgentPanel({ agents }: AgentPanelProps) {
  return (
    <section className="card">
      <h2>三类质量管控智能体协同</h2>
      <div className="grid three">
        {agents.map((agent) => (
          <article className="agent" key={agent.code}>
            <span>{agent.code}</span>
            <h3>{agent.name}</h3>
            <p>
              <strong>输入：</strong>
              {agent.input}
            </p>
            <p>
              <strong>输出：</strong>
              {agent.output}
            </p>
            <p>
              <strong>建议：</strong>
              {agent.recommendation}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

