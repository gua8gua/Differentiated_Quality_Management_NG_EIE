interface PlatformHeaderProps {
  source: "api" | "mock";
  loading?: boolean;
}

export function PlatformHeader({ source, loading }: PlatformHeaderProps) {
  return (
    <header className="platform-header">
      <div>
        <strong>DQM Platform</strong>
        <span>差异化质量管控演示平台</span>
      </div>
      <div className="platform-header__meta">
        <span className={`status-pill ${source}`}>
          {loading ? "加载中..." : source === "api" ? "API 实时数据" : "本地 Mock 数据"}
        </span>
        <a href="http://127.0.0.1:8020/docs" target="_blank" rel="noreferrer">
          API 文档
        </a>
      </div>
    </header>
  );
}
