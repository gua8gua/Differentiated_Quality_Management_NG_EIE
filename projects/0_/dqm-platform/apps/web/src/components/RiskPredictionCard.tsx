import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface RiskPredictionCardProps {
  riskPrediction: DashboardData["riskPrediction"];
}

export function RiskPredictionCard({ riskPrediction }: RiskPredictionCardProps) {
  return (
    <article className="card">
      <h2>风险预测 Mock</h2>
      <p>
        当前风险等级：<strong className="risk">{riskPrediction.riskLevel}</strong>
      </p>
      {riskPrediction.classification ? (
        <>
          <h3>SECOM 分类指标</h3>
          <p>
            F1：{riskPrediction.classification.f1}，召回率：{riskPrediction.classification.recall}，
            准确率：{riskPrediction.classification.accuracy}
          </p>
        </>
      ) : null}
      {riskPrediction.trend ? (
        <p>
          趋势特征：{riskPrediction.trend.feature}，变化量：{riskPrediction.trend.delta}
        </p>
      ) : null}
      <h3>DTW 相似片段</h3>
      <ul>
        {riskPrediction.dtwSimilarSegments.map((segment) => (
          <li key={segment.caseId}>
            {segment.caseId}：{segment.label}，相似度 {segment.similarity}
          </li>
        ))}
      </ul>
    </article>
  );
}

