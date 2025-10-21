from dataclasses import asdict, dataclass
from typing import Dict, Optional

from django.db.models import Q
from kubernetes.utils.quantity import parse_quantity

from baseten_internal.errors import Error
from oracles.models import OracleInstanceType


DEFAULT_CPU = "500m"
DEFAULT_MEMORY = "512Mi"
ACCELERATOR_KEY = "accelerator"
NODE_COUNT_KEY = "node_count"


def parse_memory_to_mebi(memory: str) -> int:
    return int(parse_quantity(memory) / 1024 / 1024)


def parse_cpu_to_milli(cpu: str) -> int:
    return int(parse_quantity(cpu) * 1000)


@dataclass
class ParsedTrussResources:
    """Holder class for resources based on the truss config.

    Units of everything match what there are defined to be in `OracleInstanceType`
    """

    millicpu_limit: int
    memory_limit: int
    gpu_type: Optional[OracleInstanceType.GpuType] = None
    gpu_count: int = 0
    node_count: Optional[int] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    def __str__(self):
        node_count_part = ""
        if self.node_count is not None and self.node_count > 1:
            node_count_part = f", Node Count: {self.node_count}"

        return f"GPU Type: {'None' if self.gpu_type is None else self.gpu_type.value}, GPU Count: {self.gpu_count}, CPU Limit: {self.millicpu_limit}, CPU Memory Limit: {self.memory_limit}{node_count_part}"


class TrussResourceConfigError(Error):
    pass


class InstanceNotSupportedError(TrussResourceConfigError):
    pass


class AcceleratorNotSupportedError(TrussResourceConfigError):
    pass


def get_accelerator(acc_spec: str) -> tuple[OracleInstanceType.GpuType, int]:
    parts = acc_spec.split(":")
    count = 1
    if len(parts) not in [1, 2]:
        raise TrussResourceConfigError("`accelerator` does not match parsing requirements.")
    if len(parts) == 2:
        count = int(parts[1])
    try:
        acc = OracleInstanceType.GpuType[parts[0]]
    except KeyError as exc:
        raise AcceleratorNotSupportedError(f"Accelerator {acc_spec} not supported") from exc
    return (acc, count)


def parse_resources(resources: dict) -> ParsedTrussResources:
    parsed = ParsedTrussResources(
        millicpu_limit=parse_cpu_to_milli(resources.get("cpu", DEFAULT_CPU)),
        memory_limit=parse_memory_to_mebi(resources.get("memory", DEFAULT_MEMORY)),
    )

    if resources.get("use_gpu", False):
        parsed.gpu_count = 1

    acc_spec = resources.get(ACCELERATOR_KEY, None)
    if acc_spec is not None:
        acc, count = get_accelerator(acc_spec)

        parsed.gpu_type = acc
        parsed.gpu_count = count

    # in case the node_count is explicitly set as None. If the
    # user sets the node_count to 0, it will also get set to 1.
    parsed.node_count = resources.get(NODE_COUNT_KEY) or 1

    return parsed


def _get_filter_kwargs(
    resources: ParsedTrussResources, workload_type: OracleInstanceType.WorkloadType
) -> dict:
    result = {
        "workload_type": workload_type.value,
        "millicpu_limit__gte": resources.millicpu_limit,
        "memory_limit__gte": resources.memory_limit,
        "gpu_count__gte": resources.gpu_count,
    }
    if resources.gpu_type is not None:
        result["gpu_type"] = resources.gpu_type.value
    else:
        # Instance type with no GPU have "" as value. If we don't filter on this value
        # you can still end up with a GPU instance type when not specifying a GPU
        result["gpu_type"] = ""

    if resources.node_count is not None:
        result["node_count"] = resources.node_count
    return result


def get_least_expensive_instance_type(
    resources: ParsedTrussResources, workload_type: OracleInstanceType.WorkloadType, org=None
) -> OracleInstanceType:
    listed_filter = Q(listed=True)
    if org:
        listed_filter |= Q(organizations_with_additional_listing=org)

        # Exclude instance types the org is not allowed to use
        exclusion_filter = ~Q(organizations_with_excluded_listing=org)
    else:
        exclusion_filter = Q()  # no-op filter

    selected_instance_type = (
        OracleInstanceType.objects.filter(
            listed_filter,
            exclusion_filter,
            deprecated=False,
            **_get_filter_kwargs(resources, workload_type),
        )
        .order_by("price")
        .first()
    )
    return selected_instance_type
