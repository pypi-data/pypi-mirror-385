import pytest

from conftest import generate_multinode_instance_type
from oracles.models import OracleInstanceType
from oracles.truss.resources import (
    ParsedTrussResources,
    get_accelerator,
    get_least_expensive_instance_type,
    parse_resources,
)


@pytest.mark.parametrize(
    "accelerator_str, accelerator_type, accelerator_count",
    [
        ("T4", OracleInstanceType.GpuType.T4, 1),
        ("T4:1", OracleInstanceType.GpuType.T4, 1),
        ("T4:4", OracleInstanceType.GpuType.T4, 4),
        ("T4:8", OracleInstanceType.GpuType.T4, 8),
        ("A10G", OracleInstanceType.GpuType.A10G, 1),
        ("A10G:1", OracleInstanceType.GpuType.A10G, 1),
        ("A10G:2", OracleInstanceType.GpuType.A10G, 2),
        ("A10G:4", OracleInstanceType.GpuType.A10G, 4),
        ("A10G:8", OracleInstanceType.GpuType.A10G, 8),
        ("L4", OracleInstanceType.GpuType.L4, 1),
        ("L4:1", OracleInstanceType.GpuType.L4, 1),
        ("L4:2", OracleInstanceType.GpuType.L4, 2),
        ("L4:4", OracleInstanceType.GpuType.L4, 4),
    ],
)
def test_get_accelerator(
    accelerator_str: str, accelerator_type: OracleInstanceType.GpuType, accelerator_count: int
):
    assert get_accelerator(accelerator_str) == (accelerator_type, accelerator_count)


@pytest.mark.parametrize(
    "truss_resources, parsed_resources",
    [
        ({}, ParsedTrussResources(millicpu_limit=500, memory_limit=512, gpu_count=0, node_count=1)),
        (
            {"accelerator": None},
            ParsedTrussResources(millicpu_limit=500, memory_limit=512, gpu_count=0, node_count=1),
        ),
        (
            {"accelerator": "T4", "memory": "512Mi", "cpu": "4", "use_gpu": True},
            ParsedTrussResources(
                millicpu_limit=4000,
                memory_limit=512,
                gpu_count=1,
                gpu_type=OracleInstanceType.GpuType.T4,
                node_count=1,
            ),
        ),
        (
            {"accelerator": "A10G:4", "memory": "16Gi", "cpu": "16", "use_gpu": True},
            ParsedTrussResources(
                millicpu_limit=16000,
                memory_limit=16 * 1024,
                gpu_count=4,
                gpu_type=OracleInstanceType.GpuType.A10G,
                node_count=1,
            ),
        ),
        (
            {"accelerator": "L4", "memory": "512Mi", "cpu": "4", "use_gpu": True},
            ParsedTrussResources(
                millicpu_limit=4000,
                memory_limit=512,
                gpu_count=1,
                gpu_type=OracleInstanceType.GpuType.L4,
                node_count=1,
            ),
        ),
        (
            {"node_count": 2},
            ParsedTrussResources(node_count=2, millicpu_limit=500, memory_limit=512, gpu_count=0),
        ),
        (
            {"accelerator": "L4", "memory": "512Mi", "cpu": "4", "use_gpu": True, "node_count": 2},
            ParsedTrussResources(
                millicpu_limit=4000,
                memory_limit=512,
                gpu_count=1,
                gpu_type=OracleInstanceType.GpuType.L4,
                node_count=2,
            ),
        ),
        (
            {"node_count": 2},
            ParsedTrussResources(node_count=2, millicpu_limit=500, memory_limit=512, gpu_count=0),
        ),
        (
            {"node_count": None},
            ParsedTrussResources(node_count=1, millicpu_limit=500, memory_limit=512, gpu_count=0),
        ),
        (
            {"accelerator": "L4", "memory": "512Mi", "cpu": "4", "use_gpu": True, "node_count": 2},
            ParsedTrussResources(
                millicpu_limit=4000,
                memory_limit=512,
                gpu_count=1,
                gpu_type=OracleInstanceType.GpuType.L4,
                node_count=2,
            ),
        ),
    ],
)
def test_parse_resources(truss_resources: dict, parsed_resources: ParsedTrussResources):
    assert parse_resources(truss_resources) == parsed_resources


@pytest.mark.django_db(databases=["default"])
@pytest.mark.parametrize(
    "parsed_resources, instance_type",
    [
        (ParsedTrussResources(millicpu_limit=500, memory_limit=512, gpu_count=0), "1x2"),
        (ParsedTrussResources(millicpu_limit=3500, memory_limit=15500, gpu_count=0), "4x16"),
        (ParsedTrussResources(millicpu_limit=300, memory_limit=4300, gpu_count=0), "2x8"),
        (
            ParsedTrussResources(
                millicpu_limit=500,
                memory_limit=512,
                gpu_count=1,
                gpu_type=OracleInstanceType.GpuType.T4,
            ),
            "T4x4x16",
        ),
        (
            ParsedTrussResources(
                millicpu_limit=500,
                memory_limit=512,
                gpu_count=1,
                gpu_type=OracleInstanceType.GpuType.A10G,
            ),
            "A10Gx4x16",
        ),
    ],
)
def test_get_least_expensive_instance_type(
    parsed_resources: ParsedTrussResources, instance_type: OracleInstanceType
):
    # Set up B10 GPU instance type to be very cheap
    b10_gpu_instance = OracleInstanceType.objects.get(name="B10:2x2x8")
    b10_gpu_instance.price = "0.00001"
    b10_gpu_instance.listed = True
    b10_gpu_instance.save()

    assert get_least_expensive_instance_type(
        parsed_resources, workload_type=OracleInstanceType.WorkloadType.MODEL_SERVING
    ) == OracleInstanceType.serving_objects.get(name=instance_type)


@pytest.mark.django_db(databases=["default"])
@pytest.mark.parametrize(
    "parsed_resources,instance_type",
    [
        (ParsedTrussResources(millicpu_limit=500, memory_limit=512, gpu_count=0), "1x2"),
        (
            ParsedTrussResources(node_count=2, millicpu_limit=500, memory_limit=512, gpu_count=0),
            "2*1x2",
        ),
    ],
)
def test_get_least_expensive_instance_type_multinode(parsed_resources, instance_type):
    # set the price to 0 to verify that we don't select multinode instance types
    # even if they're the cheapest
    generate_multinode_instance_type(price=0)
    expected = OracleInstanceType.serving_objects.get(name=instance_type)
    actual = get_least_expensive_instance_type(
        parsed_resources, workload_type=OracleInstanceType.WorkloadType.MODEL_SERVING
    )
    assert expected == actual


@pytest.mark.django_db(databases=["default"])
def test_get_least_expensive_instance_type_from_additional_listing(organization):
    parsed_resources = ParsedTrussResources(millicpu_limit=500, memory_limit=3000, gpu_count=0)

    oracle_instance_type = OracleInstanceType.objects.create(
        name="test_instance_type",
        display_name="Test Instance Type",
        millicpu_limit=500,
        memory_limit=3000,
        gpu_count=0,
        price="0.00001",
    )

    organization.additional_listed_instance_types.add(oracle_instance_type)

    assert (
        get_least_expensive_instance_type(
            parsed_resources,
            workload_type=OracleInstanceType.WorkloadType.MODEL_SERVING,
            org=organization,
        )
        == oracle_instance_type
    )


@pytest.mark.django_db(databases=["default"])
def test_get_least_expensive_instance_type_check_excluded(organization):
    parsed_resources = ParsedTrussResources(
        millicpu_limit=500, memory_limit=3000, gpu_count=1, gpu_type=OracleInstanceType.GpuType.B10
    )

    # Set up B10 GPU instance type to be very cheap
    b10_gpu_instance = OracleInstanceType.objects.get(name="B10:2x2x8")
    b10_gpu_instance.price = "0.1"
    b10_gpu_instance.listed = True
    b10_gpu_instance.save()

    # Set up B10:4x4x16 to be even cheaper but will be excluded
    excluded_gpu_instance = OracleInstanceType.objects.get(name="B10:4x4x16")
    excluded_gpu_instance.price = "0.00001"
    excluded_gpu_instance.listed = True
    excluded_gpu_instance.save()

    organization.excluded_instance_types.add(excluded_gpu_instance)

    # Excluded instance types must not be picked even if they are cheaper
    assert get_least_expensive_instance_type(
        parsed_resources,
        workload_type=OracleInstanceType.WorkloadType.MODEL_SERVING,
        org=organization,
    ) == OracleInstanceType.serving_objects.get(name="B10:2x2x8")


@pytest.mark.django_db(databases=["default"])
def test_get_least_expensive_instance_type_from_additional_listing_check_excluded(organization):
    parsed_resources = ParsedTrussResources(millicpu_limit=500, memory_limit=3000, gpu_count=0)

    oracle_instance_type = OracleInstanceType.objects.create(
        name="test_instance_type",
        display_name="Test Instance Type",
        millicpu_limit=500,
        memory_limit=3000,
        gpu_count=0,
        price="0.00005",
    )

    excluded_instance_type = OracleInstanceType.objects.create(
        name="excluded_instance_type",
        display_name="Excluded Instance Type",
        millicpu_limit=500,
        memory_limit=3000,
        gpu_count=0,
        price="0.00001",
    )

    organization.additional_listed_instance_types.add(oracle_instance_type)
    organization.excluded_instance_types.add(excluded_instance_type)

    # Excluded instance types must not be picked even if they are cheaper
    assert (
        get_least_expensive_instance_type(
            parsed_resources,
            workload_type=OracleInstanceType.WorkloadType.MODEL_SERVING,
            org=organization,
        )
        == oracle_instance_type
    )
