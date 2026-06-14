import type { DashboardData } from "../../../../packages/shared-types/contracts";
import { percent } from "../services/dashboard";

interface DataQualityCardProps {
  dataQuality: DashboardData["dataQuality"];
}

export function DataQualityCard({ dataQuality }: DataQualityCardProps) {
  return (
    <article className="card">
      <h2>数据治理结果</h2>
      <dl className="metrics">
        <div>
          <dt>缺失率</dt>
          <dd>{percent(dataQuality.missingRate)}</dd>
        </div>
        <div>
          <dt>异常率</dt>
          <dd>{percent(dataQuality.anomalyRate)}</dd>
        </div>
      </dl>
      <h3>关键特征</h3>
      <div className="chip-row">
        {dataQuality.topFeatures.map((feature) => (
          <span key={feature}>{feature}</span>
        ))}
      </div>
    </article>
  );
}

