import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Reading } from "@/lib/skyguard-api";

export type SeriesKey = "temperature" | "pressure" | "humidity" | "anomaly_score";

const SERIES: Record<SeriesKey, { label: string; color: string; axis: "left" | "right" }> = {
  temperature: { label: "Temperature (°C)", color: "var(--color-temp)", axis: "left" },
  pressure: { label: "Pressure (hPa)", color: "var(--color-pressure)", axis: "right" },
  humidity: { label: "Humidity (%)", color: "var(--color-humidity)", axis: "left" },
  anomaly_score: { label: "Anomaly Score", color: "var(--color-score)", axis: "left" },
};

export function TrendChart({ data, visible }: { data: Reading[]; visible: SeriesKey[] }) {
  const points = data.map((r) => ({
    t: new Date(r.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    temperature: r.temperature,
    pressure: r.pressure,
    humidity: r.humidity,
    anomaly_score: r.anomaly_score,
  }));

  if (points.length === 0) {
    return (
      <div className="flex h-full min-h-40 items-center justify-center text-sm text-muted-foreground">
        No readings yet for this station.
      </div>
    );
  }

  return (
    <div className="h-56 w-full sm:h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
          <CartesianGrid stroke="var(--color-grid)" strokeDasharray="3 4" vertical={false} />
          <XAxis
            dataKey="t"
            tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: "var(--color-grid)" }}
            minTickGap={24}
          />
          <YAxis
            yAxisId="left"
            width={44}
            domain={[0, 100]}
            tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            width={48}
            domain={["dataMin - 3", "dataMax + 3"]}
            tick={{ fill: "var(--color-pressure)", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              background: "var(--color-popover)",
              border: "1px solid var(--color-border)",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "var(--color-muted-foreground)" }}
          />
          {visible.map((key) => (
            <Line
              key={key}
              yAxisId={SERIES[key].axis}
              type="monotone"
              dataKey={key}
              name={SERIES[key].label}
              stroke={SERIES[key].color}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function TrendLegend({ visible }: { visible: SeriesKey[] }) {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
      {visible.map((key) => (
        <span key={key} className="flex items-center gap-1.5">
          <i
            className="h-0.5 w-4 rounded-full"
            style={{ backgroundColor: SERIES[key].color }}
            aria-hidden
          />
          {SERIES[key].label}
        </span>
      ))}
    </div>
  );
}

export const SERIES_KEYS = Object.keys(SERIES) as SeriesKey[];
export const seriesLabel = (key: SeriesKey) => SERIES[key].label;
