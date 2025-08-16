"use client";
import * as React from "react";
import { SlackConnectPanel } from "@/components/settings/SlackConnectPanel";
import { ChannelPicker } from "@/components/settings/ChannelPicker";
import { useSlackChannels } from "@/hooks/settings/useSlackChannels";

export default function SettingsPage() {
  const {
    isConnected,
    connect,
    disconnect,
    channels,
    addChannelByName,
    addChannels,
    removeChannel,
    clearChannels,
    suggestions,
  } = useSlackChannels();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>

      <section className="space-y-3">
        <h2 className="text-sm font-medium">Integrations</h2>
        <SlackConnectPanel
          isConnected={isConnected}
          onConnect={connect}
          onDisconnect={disconnect}
        />
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-medium">Slack Channels</h2>
        <ChannelPicker
          value={channels}
          suggestions={suggestions}
          onAddByName={addChannelByName}
          onAddMany={addChannels}
          onRemove={removeChannel}
          onClear={clearChannels}
        />
      </section>
    </div>
  );
}


