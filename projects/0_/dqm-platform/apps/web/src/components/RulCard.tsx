import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface RulCardProps {
  rul: DashboardData["riskPrediction"]["rul"];
}

export function RulCard({ rul }: RulCardProps) {
  return (
    <article className="card">
      <h2>RUL 曲线数据</h2>
      <div className="bars">
        {rul.map((item) => (
          <div className="bar-row" key={item.cycle}>
            <span>Cycle {item.cycle}</span>
            <div>
              <i style={{ width: `${item.value / 1.4}%` }} />
            </div>
            <b>{item.value}</b>
          </div>
        ))}
      </div>
    </article>
  );
}

