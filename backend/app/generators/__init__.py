"""
Vertical-specific LLM response generators — India AI Fellowship Platform.

Primary fellowship generators:
    - GovernanceGenerator : Public policy, welfare schemes, Jan Suvidha summaries.
    - JudgmentGenerator   : Court orders, binding ratio decidendi, bail jurisprudence.
    - RiskGenerator       : Statutory law, criminal code concordance, deed covenants.
"""
from app.generators.governance import GovernanceGenerator
from app.generators.judgment   import JudgmentGenerator
from app.generators.risk       import RiskGenerator

# Backward-compatibility aliases for legacy verticals
ComplianceGenerator = RiskGenerator
FriendlyGenerator   = GovernanceGenerator
AcademicGenerator   = GovernanceGenerator

__all__ = [
    "GovernanceGenerator",
    "JudgmentGenerator",
    "RiskGenerator",
    "ComplianceGenerator",
    "FriendlyGenerator",
    "AcademicGenerator",
]
