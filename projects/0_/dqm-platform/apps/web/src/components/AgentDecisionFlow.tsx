import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface AgentDecisionFlowProps {
  decisions: NonNullable<DashboardData["agentDecisions"]>;
}

export function AgentDecisionFlow({ decisions }: AgentDecisionFlowProps) {
  return (
    <section className="card">
      <h2>智能体协同决策流程</h2>
      <div className="decision-flow">
        {decisions.map((decision) => (
          <article key={decision.agent}>
            <strong>{decision.agent}</strong>
            <p>{decision.judgment}</p>
            <p className="highlight">{decision.recommendation}</p>
            <span>置信度 {(decision.confidence * 100).toFixed(0)}%</span>
          </article>
        ))}
      </div>
    </section>
  );
}

