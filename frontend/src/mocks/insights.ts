import type { TimeRange } from "@/types/dashboard";
import type { Insight } from "@/types/insights";

export function getAvailableTeams(): string[] {
  return ["Eng", "Design", "Support", "Product"];
}

function nowIso() {
  return new Date().toISOString();
}

// Very light pseudo-random toggle to vary text per range
function pick<T>(arr: T[], seed: number): T {
  return arr[seed % arr.length];
}

export function getTeamInsights(range: TimeRange = "week"): Insight[] {
  const teams = getAvailableTeams();
  const seedBase = range === "week" ? 1 : range === "month" ? 2 : range === "quarter" ? 3 : 4;
  const items: Insight[] = [];

  teams.forEach((team, idx) => {
    const s = (idx + 1) * seedBase;
    const sev = pick(["Low", "Medium", "High"], s) as Insight["severity"];
    const cat = pick(["engagement", "burnout", "communication", "workload", "sentiment", "recognition"], s) as Insight["category"];
    const deltas = [
      { avgSentimentDelta: -0.12, messageVolumeDelta: 0.18 },
      { avgSentimentDelta: 0.05, messageVolumeDelta: -0.07 },
      { avgSentimentDelta: -0.22, messageVolumeDelta: 0.04 },
      { avgSentimentDelta: 0.1, messageVolumeDelta: 0.02 },
    ];
    const ctx = pick(deltas, s);

    const summaries = {
      engagement:
        `${team} shows a dip in participation during standups and fewer emoji reactions, suggesting lower day-to-day engagement.`,
      burnout:
        `${team} exhibits more after-hours messages and sharper tone, correlated with sprint crunch, indicating potential burnout risk.`,
      communication:
        `${team} has longer unresolved threads and increased back-and-forth in specs, pointing to misalignment in requirements.`,
      workload:
        `${team} has rising message volume but declining unique senders, hinting at workload concentration among a few contributors.`,
      sentiment:
        `${team}'s average sentiment trended downward compared to the previous ${range}, especially around incident-related threads.`,
      recognition:
        `${team} has fewer shout-outs and kudos than typical this ${range}, which can correlate with lower engagement over time.`,
    } as const;

    const recommendations = {
      engagement:
        `Rotate facilitation duties and try a quick win demo Friday. Ask each member to share a small win. Revisit meeting formats to shorten and add interaction.`,
      burnout:
        `Plan a lighter sprint next cycle, stagger on-call, and schedule 1:1s to check capacity. Encourage "office hours" posts to deflect after-hours DMs.`,
      communication:
        `Adopt a spec template with clear "decision owner" and "open questions". Timebox async debates and move to a 15-min sync when threads exceed 20 replies.`,
      workload:
        `Rebalance tasks by pairing senior contributors with juniors on high-load areas. Add a clear handoff checklist for PR reviewers to spread load.`,
      sentiment:
        `Acknowledge incident fatigue, recap what changed, and share next steps. Invite anonymous feedback in the retro to capture concerns.`,
      recognition:
        `Add a weekly kudos thread and call out specific behaviors tied to values. Encourage peers to nominate teammates for recognition.`,
    } as const;

    items.push({
      id: `insight-${team.toLowerCase()}-${range}`,
      scope: "team",
      team,
      title: `${team}: ${cat.charAt(0).toUpperCase() + cat.slice(1)} insight`,
      summary: summaries[cat],
      recommendation: recommendations[cat],
      severity: sev,
      category: cat,
      confidence: pick([0.62, 0.73, 0.81, 0.9], s),
      tags: [team, cat, range],
      createdAt: nowIso(),
      metricContext: ctx,
      range,
    });
  });

  // Add one cross-team/company-level insight
  items.push({
    id: `insight-company-${range}`,
    scope: "company",
    title: `Org-wide sentiment variability in the last ${range}`,
    summary:
      "Sentiment swings are higher than typical across multiple teams during release periods. Consider a shared launch checklist to reduce last-mile friction.",
    recommendation:
      "Introduce a cross-team launch owner, publish a shared cutover plan, and schedule a 30-min post-launch sync to capture lessons learned.",
    severity: "Medium",
    category: "sentiment",
    confidence: 0.78,
    tags: ["org", "launch", range],
    createdAt: nowIso(),
    range,
  });

  return items;
}


