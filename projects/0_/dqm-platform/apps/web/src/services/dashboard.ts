import dashboardData from "../../../../mock-data/dashboard.json";
import type { DashboardData } from "../../../../packages/shared-types/contracts";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export function loadDashboard(): DashboardData {
  return dashboardData as DashboardData;
}

export async function fetchDashboard(): Promise<{ data: DashboardData; source: "api" | "mock" }> {
  try {
    const response = await fetch(`${API_BASE}/dashboard`, { signal: AbortSignal.timeout(2500) });
    if (!response.ok) {
      throw new Error(`API ${response.status}`);
    }
    return { data: (await response.json()) as DashboardData, source: "api" };
  } catch {
    return { data: loadDashboard(), source: "mock" };
  }
}

export function percent(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}
