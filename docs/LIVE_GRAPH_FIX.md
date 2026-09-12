# Live Graph Update Fix

## What changed

The dashboard previously refreshed the complete dashboard payload every 3 seconds. The chart therefore depended on the general dashboard request rather than having its own telemetry refresh path.

The graph now uses the dedicated backend trend endpoint:

`GET /api/stations/{station_id}/trend?hours=1`

The frontend polls this endpoint every **1 second** while retaining the existing 3-second dashboard polling for cards, alerts, and station metadata.

## Live flow

```text
AWS / simulator / Live Monitor
        |
        v
POST /api/readings
        |
        v
Anomaly engine + database commit
        |
        v
GET /api/stations/{station_id}/trend
        |
        |  every 1 second
        v
React Query -> liveDash.trend
        |
        v
TrendChart re-render
```

## Additional reliability fixes

- Background polling continues while the browser tab is not focused.
- The frontend keeps the last successful station data during a transient polling error instead of immediately falling back to static demo data.
- The trend endpoint is capped at 240 readings per response to prevent the chart payload from growing indefinitely.
- The selected station has its own trend query key, so changing stations switches the live graph cleanly.

## Expected demo behavior

When **Live Monitor** is enabled at 5 seconds, each station receives a new backend reading approximately every 5 seconds. The graph polls every second, so a newly committed point normally becomes visible within about one second of the backend commit.

This is live polling, not WebSocket/SSE streaming. It is intentionally simple and suitable for the SIH demonstration.
