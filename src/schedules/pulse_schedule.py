from os import getenv

from agno.scheduler import ScheduleManager


PULSE_INTERVAL_CRON = getenv("PULSE_INTERVAL_CRON", "*/30 * * * *")


def register_pulse_schedule(mgr: ScheduleManager) -> None:
    """Register the recurring Pulse Dispatcher heartbeat schedule."""
    mgr.create(
        name="neo-pulse-heartbeat",
        cron=PULSE_INTERVAL_CRON,
        endpoint="/agents/neo-pulse/runs",
        payload={
            "message": (
                "Run your pulse cycle: scan Plane for ready and stalled work, "
                "dispatch eligible items, log your findings."
            ),
        },
        description="Recurring Pulse Dispatcher heartbeat — scans, dispatches, and learns.",
        if_exists="update",
    )
