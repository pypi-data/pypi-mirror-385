"""ACE framework configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ACEConfig:
    """ACE framework configuration.

    Attributes:
        trace_dir: Directory for execution traces
        delta_dir: Directory for reflection deltas
        playbook_dir: Directory for playbooks
        enabled: Whether ACE is globally enabled
    """

    trace_dir: Path
    delta_dir: Path
    playbook_dir: Path
    enabled: bool = True


def get_default_config() -> ACEConfig:
    """Get default ACE configuration.

    Returns:
        Default ACEConfig instance
    """
    project_root = Path(__file__).parent.parent.parent.parent
    docs_dir = project_root / "docs"

    return ACEConfig(
        trace_dir=docs_dir / "generator" / "traces",
        delta_dir=docs_dir / "reflector" / "deltas",
        playbook_dir=docs_dir / "curator" / "playbooks",
        enabled=True,
    )
