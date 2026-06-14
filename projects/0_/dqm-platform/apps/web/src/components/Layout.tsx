import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "总览 Dashboard" },
  { to: "/import", label: "数据导入" },
  { to: "/graph", label: "知识图谱" },
  { to: "/agent", label: "Agent 协同" },
];

export function Layout() {
  return (
    <div className="app-shell">
      <nav className="top-nav">
        <div className="brand">
          <strong>DQM Platform</strong>
          <span>差异化质量管控演示平台</span>
        </div>
        <div className="nav-links">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.to === "/"}>
              {link.label}
            </NavLink>
          ))}
        </div>
      </nav>
      <Outlet />
    </div>
  );
}
