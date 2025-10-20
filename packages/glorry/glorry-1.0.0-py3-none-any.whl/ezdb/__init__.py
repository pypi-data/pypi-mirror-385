"""
EzDB B-Class (Basic) - Free & Open Source Vector Database

Version: 1.0.0
Tier: B-Class (Basic)
Status: STABLE - Production Ready
Stability: No breaking changes in 1.x series

Learn more:
- Documentation: https://ezdb.io/docs
- Professional: https://ezdb.io/professional
- Enterprise: https://ezdb.io/enterprise
"""

from .database import EzDB
from .similarity import SimilarityMetric

__version__ = "1.0.0"
__tier__ = "B-Class"
__stability__ = "STABLE"
__license__ = "MIT"

__all__ = ["EzDB", "SimilarityMetric"]
