import { useState } from "react";
import { Plug, RefreshCw } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { defaultApiBase, getApiBase, setApiBase } from "@/lib/skyguard-api";
import { cn } from "@/lib/utils";

export function ApiSettings({ live, onSaved }: { live: boolean; onSaved: () => void }) {
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState("");

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (next) setValue(getApiBase());
        setOpen(next);
      }}
    >
      <DialogTrigger asChild>
        <button
          type="button"
          className={cn(
            "flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[0.65rem] font-semibold tracking-[0.12em] uppercase transition-colors",
            live
              ? "border-normal/50 bg-normal/10 text-normal"
              : "border-warning/50 bg-warning/10 text-warning",
          )}
        >
          <i className="pulse-dot" aria-hidden />
          {live ? "Live" : "Demo data"}
        </button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plug size={16} className="text-primary" /> Backend connection
          </DialogTitle>
          <DialogDescription>
            SkyGuard reads from the FastAPI service. Enter its API base URL — the dashboard falls
            back to demo data whenever the service is unreachable.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Label htmlFor="api-base">API base URL</Label>
          <Input
            id="api-base"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={defaultApiBase()}
            spellCheck={false}
          />
          <p className="text-xs text-muted-foreground">
            Default: <span className="num">{defaultApiBase()}</span> (run{" "}
            <span className="num">python run.py</span> in the backend folder).
          </p>
        </div>
        <DialogFooter>
          <Button
            onClick={() => {
              setApiBase(value);
              setOpen(false);
              onSaved();
            }}
          >
            <RefreshCw size={15} /> Save & reconnect
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
