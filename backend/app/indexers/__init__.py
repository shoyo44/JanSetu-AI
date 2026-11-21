"""
Vertical-specific document chunkers/indexers — India AI Fellowship Platform.

Primary fellowship indexers:
    - GovernanceIndexer : Gazette notifications, policy circulars, citizen welfare schemes.
    - JudgmentIndexer   : Judicial rulings, bench observations, ratio decidendi clauses.
    - ClauseIndexer     : Statutory clauses, criminal code provisions, contract covenants.
"""
from app.indexers.governance import GovernanceIndexer
from app.indexers.judgment   import JudgmentIndexer
from app.indexers.clause     import ClauseIndexer

# Backward-compatibility aliases for legacy verticals
ArticleIndexer = ClauseIndexer
TermIndexer    = ClauseIndexer
TopicIndexer   = GovernanceIndexer
SectionIndexer = GovernanceIndexer

__all__ = [
    "GovernanceIndexer",
    "JudgmentIndexer",
    "ClauseIndexer",
    "ArticleIndexer",
    "TermIndexer",
    "TopicIndexer",
    "SectionIndexer",
]
