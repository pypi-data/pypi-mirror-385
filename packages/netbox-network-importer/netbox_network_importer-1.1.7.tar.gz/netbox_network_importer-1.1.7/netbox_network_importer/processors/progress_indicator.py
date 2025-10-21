# Progress indicator processor for showing task completion percentage
import math

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Task


class ProgressIndicator:
    """
    Processor that shows progress updates for task execution
    Prints completion percentage every 10% of devices processed
    """

    def __init__(self, total_hosts: int = 0) -> None:
        self.total_hosts = total_hosts  # Can be set from outside
        self.completed_hosts = 0
        self.task_name = ""
        self.last_reported_percentage = 0
        self.hosts_seen = set()  # Track unique hosts we've seen

    def task_started(self, task: Task) -> None:
        """Called when a task starts - reset counters"""
        self.completed_hosts = 0
        self.task_name = task.name.replace("_", " ").title()  # Make it more readable
        self.last_reported_percentage = 0
        self.hosts_seen = set()

        # Announce the task start with device count if we know it
        if self.total_hosts > 0:
            print(
                f"🔄 Starting {self.task_name} on {self.total_hosts} device{'s' if self.total_hosts != 1 else ''}..."
            )
        else:
            print(f"🔄 Starting {self.task_name}...")

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        """Called when a task completes - show final status"""
        if self.total_hosts > 0:
            failed_count = len(result.failed_hosts) if result.failed_hosts else 0
            success_count = self.total_hosts - failed_count

            if failed_count == 0:
                print(
                    f"✅ {self.task_name} completed successfully: {success_count}/{self.total_hosts} device{'s' if self.total_hosts != 1 else ''}"
                )
            else:
                print(
                    f"⚠️  {self.task_name} completed: {success_count}/{self.total_hosts} device{'s' if self.total_hosts != 1 else ''} successful"
                )
                print(
                    f"❌ {failed_count} device{'s' if failed_count != 1 else ''} failed"
                )
        else:
            print(f"✅ {self.task_name} completed (no devices to process)")

    def task_instance_started(self, task: Task, host: Host) -> None:
        """Called when processing starts for a specific host"""
        # Count unique hosts as we see them if we don't have a total yet
        if host.name not in self.hosts_seen:
            self.hosts_seen.add(host.name)
            # Only update total if we don't have it set already
            if self.total_hosts == 0:
                self.total_hosts = len(self.hosts_seen)

    def task_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        """Called when processing completes for a specific host - update progress"""
        self.completed_hosts += 1

        # Use the total we have (either set initially or discovered)
        if self.total_hosts > 0:
            percentage = (self.completed_hosts / self.total_hosts) * 100

            # Determine reporting strategy based on total number of devices
            if self.total_hosts >= 20:
                # For 20+ devices, report every 10%
                reporting_threshold = 10
                current_threshold = (
                    math.floor(percentage / reporting_threshold) * reporting_threshold
                )
                last_threshold = (
                    math.floor(self.last_reported_percentage / reporting_threshold)
                    * reporting_threshold
                )

                if current_threshold > last_threshold and current_threshold > 0:
                    print(
                        f"📊 {self.task_name}: {current_threshold}% complete ({self.completed_hosts}/{self.total_hosts} devices)"
                    )

            elif self.total_hosts >= 10:
                # For 10-19 devices, report every 20%
                reporting_threshold = 20
                current_threshold = (
                    math.floor(percentage / reporting_threshold) * reporting_threshold
                )
                last_threshold = (
                    math.floor(self.last_reported_percentage / reporting_threshold)
                    * reporting_threshold
                )

                if current_threshold > last_threshold and current_threshold > 0:
                    print(
                        f"📊 {self.task_name}: {current_threshold}% complete ({self.completed_hosts}/{self.total_hosts} devices)"
                    )

            elif self.total_hosts >= 5:
                # For 5-9 devices, report at 50% milestone
                if (
                    self.completed_hosts == math.ceil(self.total_hosts / 2)
                    and self.completed_hosts < self.total_hosts
                ):
                    print(
                        f"📊 {self.task_name}: 50% complete ({self.completed_hosts}/{self.total_hosts} devices)"
                    )

            # For fewer than 5 devices, we'll just rely on start/end messages

            self.last_reported_percentage = percentage

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        """Called when a subtask starts for a specific host"""
        pass

    def subtask_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        """Called when a subtask completes for a specific host"""
        pass
