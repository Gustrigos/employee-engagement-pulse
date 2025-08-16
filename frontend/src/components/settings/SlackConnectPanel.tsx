"use client";
import Image from "next/image";
import { Button } from "@/components/ui/button";

interface Props {
  isConnected: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
}

export function SlackConnectPanel({ isConnected, onConnect, onDisconnect }: Props) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-black/10 dark:border-white/10 p-4">
      <div className="flex items-center gap-3">
        <Image src="/placeholder.png" alt="Slack logo" width={32} height={32} className="rounded" />
        <div>
          <p className="text-sm font-medium">Slack</p>
          <p className="text-xs text-foreground/60">
            {isConnected ? "Connected" : "Not connected"}
          </p>
        </div>
      </div>
      {isConnected ? (
        <Button variant="outline" onClick={onDisconnect}>
          Disconnect
        </Button>
      ) : (
        <Button onClick={onConnect}>Connect</Button>
      )}
    </div>
  );
}


