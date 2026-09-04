import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import type { Severity } from "@/lib/skyguard-api";

export function Panel({
  title,
  icon: Icon,
  action,
  className,
  bodyClassName,
  children,
}: {
  title: string;
  icon: LucideIcon;
  action?: ReactNode;
  className?: string;
  bodyClassName?: string;
  children: ReactNode;
}) {
  return (
    <section className={cn("panel-surface flex min-h-0 flex-col overflow-hidden", className)}>
      <header className="panel-title justify-between">
        <span className="flex items-center gap-2">
          <Icon size={15} className="text-primary" aria-hidden />
          {title}
        </span>
        {action}
      </header>
      <div className={cn("min-h-0 flex-1 p-3.5", bodyClassName)}>{children}</div>
    </section>
  );
}

export const severityText: Record<Severity, string> = {
  Normal: "text-normal",
  Warning: "text-warning",
  Critical: "text-critical",
};

export const severityBg: Record<Severity, string> = {
  Normal: "bg-normal",
  Warning: "bg-warning",
  Critical: "bg-critical",
};

export function SeverityPill({ severity }: { severity: Severity }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[0.65rem] font-semibold tracking-[0.14em] uppercase",
        severity === "Critical" && "border-critical/50 bg-critical/15 text-critical",
        severity === "Warning" && "border-warning/50 bg-warning/15 text-warning",
        severity === "Normal" && "border-normal/50 bg-normal/15 text-normal",
      )}
    >
      <i className={cn("pulse-dot", severityText[severity])} aria-hidden />
      {severity}
    </span>
  );
}

export function HealthBars({ health, severity }: { health: number; severity: Severity }) {
  const filled = Math.max(1, Math.round((health / 100) * 4));
  return (
    <div className="flex items-end gap-0.5" aria-hidden>
      {[0, 1, 2, 3].map((i) => (
        <span
          key={i}
          className={cn(
            "w-1 rounded-xs",
            i === 0 && "h-1.5",
            i === 1 && "h-2.5",
            i === 2 && "h-3.5",
            i === 3 && "h-4.5",
            i < filled ? severityBg[severity] : "bg-border",
          )}
        />
      ))}
    </div>
  );
}
