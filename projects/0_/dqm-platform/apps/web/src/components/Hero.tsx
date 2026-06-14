import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface HeroProps {
  data: DashboardData;
}

export function Hero({ data }: HeroProps) {
  return (
    <section className="hero">
      <div>
        <p className="eyebrow">Differentiated Quality Management</p>
        <h1>{data.overview.title}</h1>
        <p>{data.overview.subtitle}</p>
        <div className="chip-row">
          {data.overview.objects.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </div>
      <div className="score-card">
        <span>数据质量评分</span>
        <strong>{data.dataQuality.qualityScore}</strong>
        <small>{data.dataQuality.dataset} 基础治理结果</small>
      </div>
    </section>
  );
}

