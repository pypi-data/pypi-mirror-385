"""Code review perspectives module.

Each perspective provides specialized analysis:
- BugHunter: Identifies bugs and logical errors
- ArchitectCritic: Reviews architecture and design patterns
- PerformanceAnalyst: Analyzes performance bottlenecks
- SecurityAuditor: Audits security vulnerabilities
"""

from typing import List

from coffee_maker.code_reviewer.perspectives.base_perspective import BasePerspective
from coffee_maker.code_reviewer.perspectives.bug_hunter import BugHunter
from coffee_maker.code_reviewer.perspectives.architect_critic import ArchitectCritic
from coffee_maker.code_reviewer.perspectives.performance_analyst import PerformanceAnalyst
from coffee_maker.code_reviewer.perspectives.security_auditor import SecurityAuditor

__all__: List[str] = ["BasePerspective", "BugHunter", "ArchitectCritic", "PerformanceAnalyst", "SecurityAuditor"]
