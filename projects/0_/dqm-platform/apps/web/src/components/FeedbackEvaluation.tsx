import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface FeedbackEvaluationProps {
  feedback: NonNullable<DashboardData["feedbackEvaluation"]>;
}

export function FeedbackEvaluation({ feedback }: FeedbackEvaluationProps) {
  const items = [
    ["响应及时性", feedback.timeliness],
    ["处置有效性", feedback.effectiveness],
    ["响应完备性", feedback.completeness],
  ] as const;

  return (
    <section className="card">
      <h2>反馈响应效果评价</h2>
      <div className="feedback-grid">
        {items.map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <strong>{(value * 100).toFixed(0)}%</strong>
          </div>
        ))}
        <div>
          <span>复发风险</span>
          <strong className="risk">{feedback.recurrenceRisk}</strong>
        </div>
      </div>
      <p>{feedback.summary}</p>
    </section>
  );
}

