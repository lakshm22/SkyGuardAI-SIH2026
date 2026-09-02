import { cn } from "@/lib/utils";
import type { Station } from "@/lib/skyguard-api";
import { severityBg } from "./panel";

/** Projects lat/lon into the panel using the bounds of the station set. */
function project(stations: Station[]) {
  const lats = stations.map((s) => s.latitude);
  const lons = stations.map((s) => s.longitude);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);
  const spanLat = maxLat - minLat || 1;
  const spanLon = maxLon - minLon || 1;
  return stations.map((s) => ({
    station: s,
    x: 14 + ((s.longitude - minLon) / spanLon) * 72,
    y: 14 + ((maxLat - s.latitude) / spanLat) * 68,
  }));
}

export function NetworkMap({
  stations,
  selected,
  onSelect,
}: {
  stations: Station[];
  selected: string;
  onSelect: (id: string) => void;
}) {
  const nodes = project(stations);

  return (
    <div className="relative h-full min-h-64 w-full flex-1 overflow-hidden rounded-md border border-border bg-[oklch(0.18_0.03_250)]">
      <div
        className="absolute inset-0 opacity-40"
        style={{
          backgroundImage:
            "linear-gradient(var(--color-grid) 1px, transparent 1px), linear-gradient(90deg, var(--color-grid) 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
        aria-hidden
      />
      <svg className="absolute inset-0 h-full w-full" aria-hidden>
        {nodes.map((a, i) =>
          nodes.slice(i + 1).map((b) => (
            <line
              key={`${a.station.station_id}-${b.station.station_id}`}
              x1={`${a.x}%`}
              y1={`${a.y}%`}
              x2={`${b.x}%`}
              y2={`${b.y}%`}
              stroke="var(--color-grid)"
              strokeWidth={1}
              strokeDasharray="3 5"
            />
          )),
        )}
      </svg>
      {nodes.map(({ station, x, y }) => (
        <button
          key={station.station_id}
          type="button"
          onClick={() => onSelect(station.station_id)}
          className="absolute -translate-x-1/2 -translate-y-1/2 focus:outline-none"
          style={{ left: `${x}%`, top: `${y}%` }}
          aria-label={`${station.name} — ${station.status}`}
        >
          <span
            className={cn(
              "block size-3 rounded-full ring-2 ring-background",
              severityBg[station.status],
              selected === station.station_id && "ring-primary",
            )}
          />
          <span className="mt-1 block whitespace-nowrap text-[0.6rem] text-muted-foreground">
            {station.name.replace(/ AWS.*/, "")}
          </span>
        </button>
      ))}
      <div className="absolute bottom-2 left-2 flex gap-3 rounded-md bg-background/70 px-2 py-1 text-[0.6rem] text-muted-foreground backdrop-blur">
        <span className="flex items-center gap-1">
          <i className="size-1.5 rounded-full bg-normal" />
          Normal
        </span>
        <span className="flex items-center gap-1">
          <i className="size-1.5 rounded-full bg-warning" />
          Warning
        </span>
        <span className="flex items-center gap-1">
          <i className="size-1.5 rounded-full bg-critical" />
          Critical
        </span>
      </div>
    </div>
  );
}
