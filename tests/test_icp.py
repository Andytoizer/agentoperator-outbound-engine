"""ICP schema validation tests."""
import pytest

from pipeline.icp import ICP, PersonaTier, load_icp


def test_icp_valid():
    icp = ICP(
        name="Test",
        verticals=["fintech"],
        employee_range=(50, 500),
        regions=["US"],
        personas=[PersonaTier(name="sales", titles=["VP Sales"], seniority=["vp"])],
    )
    icp.validate()  # should not raise


def test_icp_missing_name():
    icp = ICP(
        name="",
        verticals=["fintech"],
        employee_range=(50, 500),
        personas=[PersonaTier(name="s", titles=["VP"], seniority=["vp"])],
    )
    with pytest.raises(ValueError, match="name"):
        icp.validate()


def test_icp_empty_verticals():
    icp = ICP(
        name="Test",
        verticals=[],
        employee_range=(50, 500),
        personas=[PersonaTier(name="s", titles=["VP"], seniority=["vp"])],
    )
    with pytest.raises(ValueError, match="vertical"):
        icp.validate()


def test_icp_bad_range():
    icp = ICP(
        name="Test",
        verticals=["fintech"],
        employee_range=(500, 50),  # inverted
        personas=[PersonaTier(name="s", titles=["VP"], seniority=["vp"])],
    )
    with pytest.raises(ValueError, match="employee_range"):
        icp.validate()


def test_icp_no_personas():
    icp = ICP(
        name="Test",
        verticals=["fintech"],
        employee_range=(50, 500),
        personas=[],
    )
    with pytest.raises(ValueError, match="persona"):
        icp.validate()


def test_example_yaml_loads():
    pytest.importorskip("yaml")
    from pathlib import Path
    example = Path(__file__).resolve().parent.parent / "templates" / "icp.example.yaml"
    icp = load_icp(example)
    assert icp.name
    assert len(icp.personas) >= 1
