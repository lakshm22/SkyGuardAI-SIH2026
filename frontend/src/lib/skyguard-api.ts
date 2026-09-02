/**
 * SkyGuard AI API client.
 *
 * Talks to the FastAPI backend (default http://localhost:8000/api).
 * The base URL is configurable at runtime (stored in localStorage) so the same
 * build works against a local dev backend or a deployed one.
 * When the backend is unreachable the UI falls back to demo data.
 */

export const API_STORAGE_KEY = "skyguard.apiBase";

const DEFAULT_API_BASE =
  (import.meta.env["VITE_SKYGUARD_API_URL"] as string | undefined) ?? "http://localhost:8000/api";

export function getApiBase(): string {
  if (typeof window === "undefined") return DEFAULT_API_BASE;
  return window.localStorage.getItem(API_STORAGE_KEY) || DEFAULT_API_BASE;
}

export function setApiBase(url: string) {
  if (typeof window === "undefined") return;
  const clean = url.trim().replace(/\/+$/, "");
  if (clean) window.localStorage.setItem(API_STORAGE_KEY, clean);
  else window.localStorage.removeItem(API_STORAGE_KEY);
}

export function defaultApiBase() {
  return DEFAULT_API_BASE;
}

export type Severity = "Normal" | "Warning" | "Critical";

export interface Station {
  station_id: string;
  name: string;
  latitude: number;
  longitude: number;
  health: number;
  status: Severity;
  last_seen?: string | null;
}

export interface Reading {
  id: number;
  station_id: string;
  timestamp: string;
  temperature: number;
  pressure: number;
  humidity: number;
  anomaly: boolean;
  anomaly_score: number;
  confidence: number;
  severity: Severity;
  root_cause: string;
  explanation: string;
  corrected_values: { temperature: number; pressure: number; humidity: number } | null;
}

export interface Alert {
  id: number;
  station_id: string;
  timestamp: string;
  parameter: string;
  severity: Severity;
  score: number;
  status: "Active" | "Resolved";
  root_cause: string;
  explanation: string;
}

export interface Dashboard {
  station: Pick<Station, "station_id" | "name" | "latitude" | "longitude" | "health" | "status">;
  latest: Reading | null;
  trend: Reading[];
  latest_alert: Alert | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  // Only send Content-Type when there is a body: keeps GETs as simple
  // requests so no CORS preflight is needed against the FastAPI service.
  const headers = init?.body ? { "Content-Type": "application/json", ...(init?.headers ?? {}) } : init?.headers;
  const res = await fetch(`${getApiBase()}${path}`, { ...init, ...(headers ? { headers } : {}) });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}

export const api = {
  health: () => request<{ status: string; model: string }>("/health"),
  stations: () => request<Station[]>("/stations"),
  dashboard: (stationId: string) =>
    request<Dashboard>(`/dashboard/${encodeURIComponent(stationId)}`),
  alerts: (limit = 20) => request<Alert[]>(`/alerts?limit=${limit}`),
  acknowledgeAlert: (id: number) =>
    request<Alert>(`/alerts/${id}`, { method: "PATCH", body: JSON.stringify({ status: "Resolved" }) }),
  simulate: (station_id: string, anomaly_type: string) =>
    request<unknown>("/simulate", { method: "POST", body: JSON.stringify({ station_id, anomaly_type }) }),
  retrain: () => request<{ message: string }>("/model/retrain", { method: "POST" }),
  exportUrl: (stationId?: string) =>
    `${getApiBase()}/export/readings${stationId ? `?station_id=${encodeURIComponent(stationId)}` : ""}`,
};

/* ---------------------------------- demo ---------------------------------- */

const DEMO_STATIONS: Station[] = [
  ["Chennai AWS-01", 96, "Normal", 13.08, 80.27],
  ["Coimbatore AWS-02", 88, "Normal", 11.01, 76.95],
  ["Madurai AWS-03", 76, "Warning", 9.93, 78.11],
  ["Trichy AWS-04", 65, "Warning", 10.79, 78.7],
  ["Ooty AWS-05", 93, "Normal", 11.41, 76.69],
  ["Rameswaram AWS-06", 59, "Critical", 9.28, 79.31],
].map(([name, health, status, lat, lon]) => ({
  station_id: name as string,
  name: name as string,
  latitude: lat as number,
  longitude: lon as number,
  health: health as number,
  status: status as Severity,
  last_seen: null,
}));

export function demoStations(): Station[] {
  return DEMO_STATIONS;
}

export function demoDashboard(stationId: string): Dashboard {
  const station = DEMO_STATIONS.find((s) => s.station_id === stationId) ?? DEMO_STATIONS[0]!;
  const base = Date.now() - 50 * 60_000;
  const trend: Reading[] = Array.from({ length: 24 }, (_, i) => {
    const wobble = Math.sin(i / 2.3);
    return {
      id: i,
      station_id: station.station_id,
      timestamp: new Date(base + i * 2 * 60_000).toISOString(),
      temperature: Number((31.2 + wobble * 0.8).toFixed(1)),
      pressure: Number((1007.6 + wobble * 1.4).toFixed(1)),
      humidity: Number((70 + wobble * 4).toFixed(0)),
      anomaly: false,
      anomaly_score: Number((0.08 + Math.abs(wobble) * 0.05).toFixed(2)),
      confidence: 0.9,
      severity: "Normal",
      root_cause: "Normal operating range",
      explanation: "",
      corrected_values: null,
    };
  });
  const latest = trend[trend.length - 1]!;
  return {
    station,
    latest,
    trend,
    latest_alert:
      station.status === "Normal"
        ? null
        : {
            id: 1,
            station_id: station.station_id,
            timestamp: new Date().toISOString(),
            parameter: "Temperature",
            severity: station.status,
            score: 0.97,
            status: "Active",
            root_cause: "Temperature sensor malfunction",
            explanation:
              "Temperature is much higher than the historical pattern and neighbouring stations. Humidity and pressure are also inconsistent with normal conditions.",
          },
  };
}

export function demoAlerts(): Alert[] {
  const rows: Array<[string, string, Severity, number, "Active" | "Resolved"]> = [
    ["Chennai AWS-01", "Temperature", "Critical", 0.97, "Active"],
    ["Madurai AWS-03", "Humidity", "Warning", 0.62, "Resolved"],
    ["Trichy AWS-04", "Pressure", "Warning", 0.58, "Resolved"],
    ["Coimbatore AWS-02", "Temperature", "Warning", 0.55, "Resolved"],
    ["Rameswaram AWS-06", "Humidity", "Critical", 0.96, "Resolved"],
  ];
  return rows.map(([station_id, parameter, severity, score, status], i) => ({
    id: i + 1,
    station_id,
    timestamp: new Date(Date.now() - (i + 1) * 55 * 60_000).toISOString(),
    parameter,
    severity,
    score,
    status,
    root_cause: `${parameter} deviation`,
    explanation: "",
  }));
}
