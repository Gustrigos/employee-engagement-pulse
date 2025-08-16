from fastapi import APIRouter, Query

from app.models.pydantic_types import Insight, InsightFilters, TimeRange

router = APIRouter(prefix="/insights", tags=["insights"])


def _pick(arr: list, seed: int):
    return arr[seed % len(arr)]


@router.get("/teams", response_model=list[Insight])
async def get_team_insights(range: TimeRange = Query("week")) -> list[Insight]:
    teams = ["Eng", "Design", "Support", "Product"]
    seed_base = 1 if range == "week" else 2 if range == "month" else 3 if range == "quarter" else 4
    items: list[Insight] = []

    for idx, team in enumerate(teams):
        s = (idx + 1) * seed_base
        sev = _pick(["Low", "Medium", "High"], s)
        cat = _pick(["engagement", "burnout", "communication", "workload", "sentiment", "recognition"], s)
        deltas = [
            {"avgSentimentDelta": -0.12, "messageVolumeDelta": 0.18},
            {"avgSentimentDelta": 0.05, "messageVolumeDelta": -0.07},
            {"avgSentimentDelta": -0.22, "messageVolumeDelta": 0.04},
            {"avgSentimentDelta": 0.1, "messageVolumeDelta": 0.02},
        ]
        ctx = _pick(deltas, s)

        summaries = {
            "engagement": f"{team} shows a dip in participation during standups and fewer emoji reactions, suggesting lower day-to-day engagement.",
            "burnout": f"{team} exhibits more after-hours messages and sharper tone, correlated with sprint crunch, indicating potential burnout risk.",
            "communication": f"{team} has longer unresolved threads and increased back-and-forth in specs, pointing to misalignment in requirements.",
            "workload": f"{team} has rising message volume but declining unique senders, hinting at workload concentration among a few contributors.",
            "sentiment": f"{team}'s average sentiment trended downward compared to the previous {range}, especially around incident-related threads.",
            "recognition": f"{team} has fewer shout-outs and kudos than typical this {range}, which can correlate with lower engagement over time.",
        }
        recommendations = {
            "engagement": "Rotate facilitation duties and try a quick win demo Friday. Ask each member to share a small win. Revisit meeting formats to shorten and add interaction.",
            "burnout": "Plan a lighter sprint next cycle, stagger on-call, and schedule 1:1s to check capacity. Encourage \"office hours\" posts to deflect after-hours DMs.",
            "communication": "Adopt a spec template with clear \"decision owner\" and \"open questions\". Timebox async debates and move to a 15-min sync when threads exceed 20 replies.",
            "workload": "Rebalance tasks by pairing senior contributors with juniors on high-load areas. Add a clear handoff checklist for PR reviewers to spread load.",
            "sentiment": "Acknowledge incident fatigue, recap what changed, and share next steps. Invite anonymous feedback in the retro to capture concerns.",
            "recognition": "Add a weekly kudos thread and call out specific behaviors tied to values. Encourage peers to nominate teammates for recognition.",
        }

        items.append(
            Insight(
                id=f"insight-{team.lower()}-{range}",
                scope="team",
                team=team,
                title=f"{team}: {cat.capitalize()} insight",
                summary=summaries[cat],
                recommendation=recommendations[cat],
                severity=sev,  # type: ignore[arg-type]
                category=cat,  # type: ignore[arg-type]
                confidence=_pick([0.62, 0.73, 0.81, 0.9], s),
                tags=[team, cat, range],
                createdAt=__import__("datetime").datetime.utcnow().isoformat(),
                metricContext=ctx,
                range=range,
            )
        )

    items.append(
        Insight(
            id=f"insight-company-{range}",
            scope="company",
            title=f"Org-wide sentiment variability in the last {range}",
            summary="Sentiment swings are higher than typical across multiple teams during release periods. Consider a shared launch checklist to reduce last-mile friction.",
            recommendation="Introduce a cross-team launch owner, publish a shared cutover plan, and schedule a 30-min post-launch sync to capture lessons learned.",
            severity="Medium",  # type: ignore[arg-type]
            category="sentiment",  # type: ignore[arg-type]
            confidence=0.78,
            tags=["org", "launch", range],
            createdAt=__import__("datetime").datetime.utcnow().isoformat(),
            range=range,
        )
    )

    return items