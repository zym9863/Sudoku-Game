import { CheckCircle2, Lightbulb, RefreshCw } from "lucide-react";

const DIFFICULTIES = [
  { value: "easy", label: "简单" },
  { value: "medium", label: "中等" },
  { value: "hard", label: "困难" }
];

export function GameToolbar({ difficulty, busyAction, disabled, onNewGame, onCheck, onHint }) {
  return (
    <section className="toolbar" aria-label="游戏操作">
      <div className="difficulty-tabs" role="tablist" aria-label="难度">
        {DIFFICULTIES.map((item) => (
          <button
            key={item.value}
            type="button"
            role="tab"
            aria-selected={difficulty === item.value}
            className={difficulty === item.value ? "is-active" : ""}
            disabled={disabled || Boolean(busyAction)}
            onClick={() => onNewGame(item.value)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div className="command-row">
        <button
          type="button"
          className="command-button"
          disabled={disabled || Boolean(busyAction)}
          onClick={() => onNewGame(difficulty)}
        >
          <RefreshCw size={18} />
          <span>新局</span>
        </button>
        <button
          type="button"
          className="command-button"
          disabled={disabled || Boolean(busyAction)}
          onClick={onCheck}
        >
          <CheckCircle2 size={18} />
          <span>检查</span>
        </button>
        <button
          type="button"
          className="command-button accent"
          disabled={disabled || Boolean(busyAction)}
          onClick={onHint}
        >
          <Lightbulb size={18} />
          <span>提示</span>
        </button>
      </div>
    </section>
  );
}
