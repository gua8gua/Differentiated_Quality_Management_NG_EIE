import { useEffect, useState } from "react";
import { AgentPanel } from "../components/AgentPanel";
import { AgentDecisionFlow } from "../components/AgentDecisionFlow";
import { CoreWorks } from "../components/CoreWorks";
import { DataQualityCard } from "../components/DataQualityCard";
import { DisposalReport } from "../components/DisposalReport";
import { FeedbackEvaluation } from "../components/FeedbackEvaluation";
import { GraphTraceCard } from "../components/GraphTraceCard";
import { Hero } from "../components/Hero";
import { PlatformHeader } from "../components/PlatformHeader";
import { RiskPredictionCard } from "../components/RiskPredictionCard";
import { RulCard } from "../components/RulCard";
import { WorkflowPanel } from "../components/WorkflowPanel";
import { fetchDashboardData } from "../services/api";
import type { DashboardData } from "../../../../packages/shared-types/contracts";

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [source, setSource] = useState<"api" | "mock">("mock");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData().then((result) => {
      setData(result.data);
      setSource(result.source);
      setLoading(false);
    });
  }, []);

  if (!data) {
    return (
      <main className="page">
        <PlatformHeader source={source} loading={loading} />
        <section className="card loading-card">
          <h2>正在加载演示数据...</h2>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <PlatformHeader source={source} loading={loading} />
      <Hero data={data} />
      <CoreWorks works={data.overview.coreWorks} />
      {data.workflow ? <WorkflowPanel workflow={data.workflow} /> : null}
      <section className="grid two">
        <DataQualityCard dataQuality={data.dataQuality} />
        <GraphTraceCard graphTrace={data.graphTrace} />
      </section>
      <section className="grid two">
        <RiskPredictionCard riskPrediction={data.riskPrediction} />
        <RulCard rul={data.riskPrediction.rul} />
      </section>
      <AgentPanel agents={data.agents} />
      {data.agentDecisions ? <AgentDecisionFlow decisions={data.agentDecisions} /> : null}
      {data.disposalReport ? <DisposalReport report={data.disposalReport} /> : null}
      {data.feedbackEvaluation ? <FeedbackEvaluation feedback={data.feedbackEvaluation} /> : null}
    </main>
  );
}
