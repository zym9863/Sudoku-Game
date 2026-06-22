import { BarChart3, Timer } from "lucide-react";

import { formatDuration } from "../utils/sudoku";

function BestTime({ label, value }) {
  return (
    <div className="best-time">
      <span>{label}</span>
      <strong>{value == null ? "--:--" : formatDuration(value)}</strong>
    </div>
  );
}

export function StatsPanel({ game, stats, elapsedSeconds }) {
  return (
    <aside className="stats-panel" aria-label="游戏统计">
      <div className="panel-heading">
        <Timer size={18} />
        <span>本局</span>
      </div>
      <div className="metric-grid">
        <div className="metric">
          <span>时间</span>
          <strong>{formatDuration(elapsedSeconds)}</strong>
        </div>
        <div className="metric">
          <span>错误</span>
          <strong>{game?.mistakeCount ?? 0}</strong>
        </div>
        <div className="metric">
          <span>提示</span>
          <strong>{game?.hintCount ?? 0}</strong>
        </div>
        <div className="metric">
          <span>状态</span>
          <strong>{game?.status === "completed" ? "完成" : "进行"}</strong>
        </div>
      </div>

      <div className="panel-heading summary-heading">
        <BarChart3 size={18} />
        <span>累计</span>
      </div>
      <div className="metric-grid compact">
        <div className="metric">
          <span>完成</span>
          <strong>{stats?.completedGames ?? 0}</strong>
        </div>
        <div className="metric">
          <span>活跃</span>
          <strong>{stats?.activeGames ?? 0}</strong>
        </div>
      </div>
      <div className="best-times">
        <BestTime label="简单最佳" value={stats?.bestTimes?.easy} />
        <BestTime label="中等最佳" value={stats?.bestTimes?.medium} />
        <BestTime label="困难最佳" value={stats?.bestTimes?.hard} />
      </div>
    </aside>
  );
}

