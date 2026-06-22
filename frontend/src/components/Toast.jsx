import { AlertTriangle, CheckCircle2, WifiOff } from "lucide-react";

const icons = {
  error: WifiOff,
  warning: AlertTriangle,
  success: CheckCircle2
};

export function Toast({ toast, onClose }) {
  if (!toast) return null;
  const Icon = icons[toast.type] || AlertTriangle;

  return (
    <div className={`toast ${toast.type || "warning"}`} role="status">
      <Icon size={18} />
      <span>{toast.message}</span>
      <button type="button" aria-label="关闭提示" onClick={onClose}>
        ×
      </button>
    </div>
  );
}

