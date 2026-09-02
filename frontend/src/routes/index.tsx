import { useEffect, useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  CloudSun,
  Cpu,
  Download,
  Droplets,
  Eye,
  Gauge as GaugeIcon,
  Lightbulb,
  Radio,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Thermometer,
  Wrench,
  Zap,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { HealthBars, Panel, SeverityPill, severityText } from "@/components/skyguard/panel";
import { NetworkMap } from "@/components/skyguard/network-map";
import {
  SERIES_KEYS,
  TrendChart,
  TrendLegend,
  seriesLabel,
  type SeriesKey,
} from "@/components/skyguard/trend-chart";
import { ApiSettings } from "@/components/skyguard/api-settings";
import {
  api,
  demoAlerts,
  demoDashboard,
  demoStations,
  type Alert as SkyAlert,
  type Dashboard as SkyDashboard,
  type Reading,
  type Station,
} from "@/lib/skyguard-api";
import { cn } from "@/lib/utils";

const TITLE = "SkyGuard AI — Real-time AWS Anomaly Detection";
const DESCRIPTION =
  "Mission-control dashboard for automatic weather stations: live sensor telemetry, AI anomaly scoring, root-cause analysis and predictive maintenance.";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: DashboardPage,
});

const POLL_MS = 5000;

function DashboardPage() {
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<string | null>(null);
  const [visible, setVisible] = useState<SeriesKey[]>([
    "temperature",
    "pressure",
    "humidity",
    "anomaly_score",
  ]);
  const [clock, setClock] = useState<string | null>(null);

  useEffect(() => {
    const tick = () => setClock(new Date().toLocaleTimeString());
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const stationsQuery = useQuery({
    queryKey: ["stations"],
    queryFn: api.stations,
    refetchInterval: POLL_MS,
    retry: false,
  });

  const live = stationsQuery.isSuccess;
  const stations: Station[] = live && stationsQuery.data?.length ? stationsQuery.data : demoStations();
  const activeStation = selected ?? stations[0]?.station_id ?? "";

  const dashboardQuery = useQuery({
    queryKey: ["dashboard", activeStation],
    queryFn: () => api.dashboard(activeStation),
    enabled: live && Boolean(activeStation),
    refetchInterval: POLL_MS,
    retry: false,
  });

  const alertsQuery = useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.alerts(20),
    enabled: live,
    refetchInterval: POLL_MS,
    retry: false,
  });

  const dashboard: SkyDashboard =
    (live && dashboardQuery.data) || demoDashboard(activeStation || stations[0]!.station_id);
  const alerts: SkyAlert[] = (live && alertsQuery.data) || demoAlerts();
  const latest = dashboard.latest;
  const station = stations.find((s) => s.station_id === activeStation) ?? stations[0]!;

  const range = useMemo(() => rangeOf(dashboard.trend), [dashboard.trend]);

  const refresh = () => queryClient.invalidateQueries();

  const simulate = useMutation({
    mutationFn: () => api.simulate(activeStation, "temperature_spike"),
    onSuccess: () => {
      toast.success("Anomaly simulated", { description: `Injected a temperature spike at ${activeStation}.` });
      refresh();
    },
    onError: () => toast.error("Backend unreachable", { description: "Connect the SkyGuard API to simulate." }),
  });

  const acknowledge = useMutation({
    mutationFn: (id: number) => api.acknowledgeAlert(id),
    onSuccess: () => {
      toast.success("Alert acknowledged");
      refresh();
    },
    onError: () => toast.error("Could not acknowledge alert"),
  });

  const retrain = useMutation({
    mutationFn: api.retrain,
    onSuccess: () => toast.success("Model retrained"),
    onError: () => toast.error("Backend unreachable"),
  });

  const alert = dashboard.latest_alert;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-30 border-b border-border bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center gap-3 px-4 py-3">
          <div className="flex items-center gap-3">
            <span className="grid size-10 place-items-center rounded-lg bg-primary/15 text-primary ring-1 ring-primary/30">
              <CloudSun size={22} />
            </span>
            <div>
              <h1 className="text-lg leading-none font-bold tracking-tight">
                SKYGUARD <span className="text-primary">AI</span>
              </h1>
              <p className="mt-1 text-xs text-muted-foreground">
                Intelligent AWS Anomaly Detection System
              </p>
            </div>
          </div>

          <div className="ml-auto flex flex-wrap items-center gap-2">
            <ApiSettings live={live} onSaved={refresh} />
            <span className="num rounded-md border border-border bg-card px-2.5 py-1 text-xs text-muted-foreground tabular-nums">
              {clock ?? "--:--:--"}
            </span>
            <Select value={activeStation} onValueChange={setSelected}>
              <SelectTrigger className="w-56" aria-label="Select station">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {stations.map((s) => (
                  <SelectItem key={s.station_id} value={s.station_id}>
                    {s.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={refresh} aria-label="Refresh data">
              <RefreshCw size={16} />
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1600px] gap-4 p-4 xl:grid-cols-[260px_minmax(0,1fr)_360px]">
        {/* Stations */}
        <Panel title="AWS Stations" icon={Radio} bodyClassName="space-y-2">
          <div className="scroll-slim max-h-[26rem] space-y-2 overflow-y-auto pr-1">
            {stations.map((s) => (
              <button
                key={s.station_id}
                type="button"
                onClick={() => setSelected(s.station_id)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-md border border-border bg-card px-3 py-2 text-left transition-colors hover:border-primary/50 hover:bg-accent",
                  activeStation === s.station_id && "border-primary/70 bg-accent",
                )}
              >
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-semibold">{s.name}</span>
                  <span className="block text-xs text-muted-foreground">
                    Health <b className={cn("num", severityText[s.status])}>{s.health.toFixed(0)}%</b>
                    <span className="mx-1.5 opacity-40">|</span>
                    <b className={severityText[s.status]}>{s.status}</b>
                  </span>
                </span>
                <HealthBars health={s.health} severity={s.status} />
              </button>
            ))}
          </div>
        </Panel>

        {/* Center column */}
        <div className="grid min-w-0 gap-4">
          <Panel
            title={`Current Observation — ${station.name}`}
            icon={Activity}
            action={<SeverityPill severity={latest?.severity ?? station.status} />}
            bodyClassName="space-y-4"
          >
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Metric
                icon={Thermometer}
                tone="text-temp"
                label="Temperature"
                value={latest ? latest.temperature.toFixed(1) : "--"}
                unit="°C"
                min={range.temperature[0]}
                max={range.temperature[1]}
              />
              <Metric
                icon={GaugeIcon}
                tone="text-pressure"
                label="Pressure"
                value={latest ? latest.pressure.toFixed(1) : "--"}
                unit="hPa"
                min={range.pressure[0]}
                max={range.pressure[1]}
              />
              <Metric
                icon={Droplets}
                tone="text-humidity"
                label="Humidity"
                value={latest ? latest.humidity.toFixed(0) : "--"}
                unit="%"
                min={range.humidity[0]}
                max={range.humidity[1]}
              />
              <Metric
                icon={Activity}
                tone="text-score"
                label="Anomaly Score"
                value={latest ? latest.anomaly_score.toFixed(2) : "--"}
                unit=""
                min={range.anomaly_score[0]}
                max={range.anomaly_score[1]}
              />
            </div>

            <div className="rounded-md border border-border bg-card p-3">
              <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                <b className="text-sm">Real-time Parameter Trend</b>
                <TrendLegend visible={visible} />
              </div>
              <TrendChart data={dashboard.trend} visible={visible} />
            </div>
          </Panel>

          <div className="grid gap-4 lg:grid-cols-2">
            <Panel title="AI Root-cause Analysis" icon={BrainCircuit} bodyClassName="space-y-3">
              {contributions(latest).map((c) => (
                <div key={c.label} className="grid grid-cols-[9rem_1fr_2.5rem] items-center gap-2">
                  <span className="truncate text-xs text-muted-foreground">{c.label}</span>
                  <span className="h-1.5 rounded-full bg-muted">
                    <span
                      className="block h-full rounded-full bg-primary"
                      style={{ width: `${Math.round(c.value * 100)}%` }}
                    />
                  </span>
                  <span className="num text-right text-xs">{c.value.toFixed(2)}</span>
                </div>
              ))}
              <div className="flex gap-2 rounded-md border border-border bg-card p-3 text-xs leading-relaxed text-muted-foreground">
                <Lightbulb size={16} className="mt-0.5 shrink-0 text-warning" />
                <span>
                  <b className="text-foreground">Explanation: </b>
                  {latest?.explanation ||
                    latest?.root_cause ||
                    "All parameters are consistent with the historical pattern and neighbouring stations."}
                </span>
              </div>
            </Panel>

            <Panel
              title="Latest Alert"
              icon={AlertTriangle}
              action={alert ? <SeverityPill severity={alert.severity} /> : null}
              bodyClassName="space-y-3"
            >
              {alert ? (
                <>
                  <h2 className="text-base font-semibold">{alert.parameter} anomaly detected</h2>
                  <dl className="grid grid-cols-2 gap-y-1.5 text-xs">
                    <Row label="Confidence" value={`${Math.round(alert.score * 100)}%`} />
                    <Row label="Severity" value={alert.severity} tone={severityText[alert.severity]} />
                    <Row label="Probable cause" value={alert.root_cause} />
                    <Row label="Detected at" value={new Date(alert.timestamp).toLocaleString()} />
                  </dl>
                  {latest?.corrected_values && (
                    <div className="rounded-md border border-border bg-card p-2.5 text-xs">
                      <p className="mb-1 text-muted-foreground">Estimated correct values</p>
                      <p className="num">
                        {latest.corrected_values.temperature} °C · {latest.corrected_values.pressure} hPa ·{" "}
                        {latest.corrected_values.humidity} %
                      </p>
                    </div>
                  )}
                  <Button
                    className="w-full"
                    disabled={!live || acknowledge.isPending}
                    onClick={() => acknowledge.mutate(alert.id)}
                  >
                    <CheckCircle2 size={16} /> Acknowledge alert
                  </Button>
                </>
              ) : (
                <div className="flex h-full min-h-32 flex-col items-center justify-center gap-2 text-center text-sm text-muted-foreground">
                  <ShieldCheck size={26} className="text-normal" />
                  No active alerts for {station.name}.
                </div>
              )}
            </Panel>
          </div>
        </div>

        {/* Right column */}
        <div className="grid min-w-0 gap-4">
          <Panel title="Network Map" icon={Radio} bodyClassName="p-3.5 flex">
            <NetworkMap stations={stations} selected={activeStation} onSelect={setSelected} />
          </Panel>

          <Panel title="Anomaly History" icon={Activity} bodyClassName="p-0">
            <div className="scroll-slim max-h-72 overflow-auto">
              <table className="w-full table-fixed text-left text-[0.7rem]">
                <thead className="sticky top-0 bg-panel-header text-[0.65rem] font-medium text-muted-foreground">
                  <tr>
                    <th className="w-[3.6rem] px-2 py-2 font-medium">Time</th>
                    <th className="px-2 py-2 font-medium">Station</th>
                    <th className="px-2 py-2 font-medium">Parameter</th>
                    <th className="w-11 px-2 py-2 font-medium">Score</th>
                    <th className="w-[4.2rem] px-2 py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-3 py-6 text-center text-muted-foreground">
                        No anomalies recorded.
                      </td>
                    </tr>
                  )}
                  {alerts.map((a) => (
                    <tr key={a.id} className="border-t border-border/70">
                      <td className="num px-2 py-2 whitespace-nowrap text-muted-foreground">
                        {new Date(a.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                      <td className="truncate px-2 py-2">{a.station_id}</td>
                      <td className={cn("truncate px-2 py-2", severityText[a.severity])}>{a.parameter}</td>
                      <td className="num px-2 py-2">{a.score.toFixed(2)}</td>
                      <td className="px-2 py-2">
                        <span
                          className={cn(
                            "rounded-full px-2 py-0.5 text-[0.65rem]",
                            a.status === "Active"
                              ? "bg-critical/15 text-critical"
                              : "bg-muted text-muted-foreground",
                          )}
                        >
                          {a.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </div>

        {/* Bottom row */}
        <div className="grid gap-4 md:grid-cols-2 xl:col-span-3 xl:grid-cols-4">
          <Panel title="Predictive Maintenance" icon={Wrench}>
            <div className="flex items-center justify-between gap-3">
              <div className="space-y-1 text-xs text-muted-foreground">
                <p>
                  Next maintenance due{" "}
                  <b className="num text-foreground">{Math.max(1, Math.round(station.health / 4))} days</b>
                </p>
                <p>
                  Risk of failure{" "}
                  <b className={severityText[station.status]}>
                    {station.health > 85 ? "Low" : station.health > 70 ? "Medium" : "High"} (
                    {(100 - station.health).toFixed(0)}%)
                  </b>
                </p>
              </div>
              <HealthDial value={station.health} />
            </div>
          </Panel>

          <Panel title="Quick Actions" icon={Zap} bodyClassName="grid grid-cols-2 gap-2">
            <Button variant="outline" disabled={!live} onClick={() => simulate.mutate()}>
              <Sparkles size={15} /> Simulate
            </Button>
            <Button variant="outline" disabled={!live} asChild={live}>
              {live ? (
                <a href={api.exportUrl(activeStation)} download>
                  <Download size={15} /> Export CSV
                </a>
              ) : (
                <span>
                  <Download size={15} /> Export CSV
                </span>
              )}
            </Button>
            <Button variant="outline" disabled={!live} onClick={() => retrain.mutate()}>
              <BrainCircuit size={15} /> Retrain
            </Button>
            <Button variant="outline" onClick={refresh}>
              <RefreshCw size={15} /> Refresh
            </Button>
          </Panel>

          <Panel title="View Options" icon={Eye} bodyClassName="grid grid-cols-2 gap-2">
            {SERIES_KEYS.map((key) => (
              <label key={key} className="flex items-center gap-2 text-xs">
                <Checkbox
                  checked={visible.includes(key)}
                  onCheckedChange={(checked) =>
                    setVisible((prev) =>
                      checked ? [...prev, key] : prev.filter((k) => k !== key),
                    )
                  }
                />
                {seriesLabel(key)}
              </label>
            ))}
          </Panel>

          <Panel title="System Status" icon={Cpu}>
            <div className="flex items-center justify-between gap-3">
              <div className="space-y-1 text-xs text-muted-foreground">
                <p>
                  Data stream{" "}
                  <b className={live ? "text-normal" : "text-warning"}>{live ? "Live" : "Demo"}</b>
                </p>
                <p>
                  Model status <b className="text-foreground">IsolationForest</b>
                </p>
                <p>
                  Stations online <b className="num text-foreground">{stations.length}</b>
                </p>
              </div>
              <HealthDial value={average(stations.map((s) => s.health))} />
            </div>
          </Panel>
        </div>
      </main>
    </div>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
  unit,
  min,
  max,
  tone,
}: {
  icon: typeof Activity;
  label: string;
  value: string;
  unit: string;
  min: string;
  max: string;
  tone: string;
}) {
  return (
    <div className="flex items-start gap-3 rounded-md border border-border bg-card p-3">
      <Icon size={24} className={cn("mt-0.5 shrink-0", tone)} />
      <div className="min-w-0">
        <p className="text-[0.65rem] tracking-wider text-muted-foreground uppercase">{label}</p>
        <p className="num text-2xl leading-tight font-semibold">
          {value}
          <span className="ml-1 text-xs text-muted-foreground">{unit}</span>
        </p>
        <p className="num mt-0.5 text-[0.65rem] text-muted-foreground">
          Min {min} · Max {max}
        </p>
      </div>
    </div>
  );
}

function Row({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <>
      <dt className="text-muted-foreground">{label}</dt>
      <dd className={cn("text-right font-medium", tone)}>{value}</dd>
    </>
  );
}

function HealthDial({ value }: { value: number }) {
  return (
    <div
      className="grid size-16 shrink-0 place-items-center rounded-full"
      style={{
        background: `conic-gradient(var(--color-primary) ${value * 3.6}deg, var(--color-muted) 0deg)`,
      }}
    >
      <span className="num grid size-12 place-items-center rounded-full bg-panel text-sm font-semibold">
        {value.toFixed(0)}%
      </span>
    </div>
  );
}

function average(values: number[]) {
  if (values.length === 0) return 0;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

function rangeOf(trend: Reading[]) {
  const keys = ["temperature", "pressure", "humidity", "anomaly_score"] as const;
  const out = {} as Record<(typeof keys)[number], [string, string]>;
  for (const key of keys) {
    const values = trend.map((r) => r[key]);
    out[key] = values.length
      ? [Math.min(...values).toFixed(key === "humidity" ? 0 : 1), Math.max(...values).toFixed(key === "humidity" ? 0 : 1)]
      : ["--", "--"];
  }
  return out;
}

function contributions(latest: Reading | null) {
  const score = latest?.anomaly_score ?? 0.08;
  const base = [
    { label: "Temperature jump", value: score },
    { label: "Spatial mismatch", value: score * 0.92 },
    { label: "Humidity inconsistency", value: score * 0.78 },
    { label: "Pressure deviation", value: score * 0.71 },
    { label: "Pattern deviation", value: score * 0.45 },
  ];
  return base.map((c) => ({ ...c, value: Math.min(1, Math.max(0.02, c.value)) }));
}
