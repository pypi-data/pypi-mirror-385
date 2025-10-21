# note that these imports are only needed if you are annotating your code with types
from typing import Dict

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Task


class SaveNetboxResults:
    def __init__(self, data: Dict[str, None]) -> None:
        self.data = data

    def task_started(self, task: Task) -> None:
        pass

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        pass

    def task_instance_started(self, task: Task, host: Host) -> None:
        pass

    def task_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        if not self.data.get(host.name, None):
            self.data[host.name] = {}

        if hasattr(result, "netbox_results"):
            self.data[host.name].update(result.netbox_results.to_dict())

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        pass

    def subtask_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        pass
