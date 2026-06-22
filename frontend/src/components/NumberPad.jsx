import { Eraser, Pencil } from "lucide-react";

export function NumberPad({ noteMode, busy, onNumber, onErase, onToggleNotes }) {
  return (
    <section className="number-pad" aria-label="数字输入">
      <div className="pad-grid">
        {Array.from({ length: 9 }, (_, index) => {
          const value = index + 1;
          return (
            <button
              key={value}
              type="button"
              className="number-button"
              disabled={busy}
              onClick={() => onNumber(value)}
            >
              {value}
            </button>
          );
        })}
      </div>
      <div className="pad-actions">
        <button
          type="button"
          className={`tool-button ${noteMode ? "is-active" : ""}`}
          title="笔记"
          aria-pressed={noteMode}
          disabled={busy}
          onClick={onToggleNotes}
        >
          <Pencil size={18} />
          <span>笔记</span>
        </button>
        <button type="button" className="tool-button" title="清除" disabled={busy} onClick={onErase}>
          <Eraser size={18} />
          <span>清除</span>
        </button>
      </div>
    </section>
  );
}

