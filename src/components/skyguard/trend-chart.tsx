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

const SERIES: Record<SeriesKey, { label: string; color: string; axis: "weather" | "pressure" | "score" }> = {
  temperature: { label: "Temperature (°C)", color: "var(--color-temp)", axis: "weather" },
  pressure: { label: "Pressure (hPa)", color: "var(--color-pressure)", axis: "pressure" },
  humidity: { label: "Humidity (%)", color: "var(--color-humidity)", axis: "weather" },
  anomaly_score: { label: "Anomaly Score", color: "var(--color-score)", axis: "score" },
};

export function TrendChart({ data, visible }: { data: Reading[]; visible: SeriesKey[] }) {
  const points = data
    .filter((r) => r && r.timestamp)
    .map((r) => ({
      timestamp: new Date(r.timestamp).getTime(),
      temperature: Number(r.temperature),
      pressure: Number(r.pressure),
      humidity: Number(r.humidity),
      anomaly_score: Number(r.anomaly_score),
    }))
    .filter((r) => Number.isFinite(r.timestamp));

  if (points.length === 0) {
    return (
      <div className="flex h-full min-h-40 items-center justify-center text-sm text-muted-foreground">
        No readings yet for this station. Start Live Monitor to stream telemetry.
      </div>
    );
  }

  return (
    <div className="h-56 w-full sm:h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 8, right: 10, bottom: 0, left: -12 }}>
          <CartesianGrid stroke="var(--color-grid)" strokeDasharray="3 4" vertical={false} />
          <XAxis
            dataKey="timestamp"
            type="number"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(value) => new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: "var(--color-grid)" }}
            minTickGap={28}
          />
          <YAxis
            yAxisId="weather"
            width={42}
            domain={["auto", "auto"]}
            tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            yAxisId="pressure"
            orientation="right"
            width={48}
            domain={["auto", "auto"]}
            tick={{ fill: "var(--color-pressure)", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            yAxisId="score"
            orientation="right"
            width={42}
            domain={[0, 1]}
            hide
          />
          <Tooltip
            labelFormatter={(value) => new Date(Number(value)).toLocaleString([], {
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
            })}
            formatter={(value, name) => {
              if (name === "Anomaly Score") return [Number(value).toFixed(2), name];
              if (name === "Pressure (hPa)") return [Number(value).toFixed(1), name];
              if (name === "Humidity (%)") return [Number(value).toFixed(1), name];
              return [Number(value).toFixed(1), name];
            }}
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
              connectNulls
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
