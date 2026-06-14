import type { DashboardData } from "../../../../packages/shared-types/contracts";

interface DisposalReportProps {
  report: NonNullable<DashboardData["disposalReport"]>;
}

export function DisposalReport({ report }: DisposalReportProps) {
  return (
    <section className="card">
      <h2>质量风险处置报告</h2>
      <div className="report-grid">
        <div>
          <span>问题现象</span>
          <strong>{report.phenomenon}</strong>
        </div>
        <div>
          <span>风险等级</span>
          <strong className="risk">{report.riskLevel}</strong>
        </div>
        <div>
          <span>责任对象</span>
          <strong>{report.responsibleObject}</strong>
        </div>
      </div>
      <h3>证据链</h3>
      <ul>
        {report.evidenceChain.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <h3>根因路径</h3>
      <div className="path">{report.rootCausePath.join(" → ")}</div>
      <p>
        <strong>处置建议：</strong>
        {report.recommendation}
      </p>
    </section>
  );
}

