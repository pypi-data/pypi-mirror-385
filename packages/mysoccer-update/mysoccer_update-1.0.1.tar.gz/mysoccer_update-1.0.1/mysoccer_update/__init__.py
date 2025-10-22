"""
📦 DATA COLLECTOR MODULE
========================

Mackolik API'den veri çeken modüler sistem.
Her projede kullanılabilir, temiz ve güvenilir.

Kullanım:
    from data_collector import ResultsAPI, FixturesAPI
    
    # Sonuçlar
    results = ResultsAPI()
    results.update_today()
    
    # Fikstürler
    fixtures = FixturesAPI()
    data = fixtures.get_next_3_days()
"""

from .results import ResultsAPI
from .fixtures import FixturesAPI
from .config import DB_CONFIG

__all__ = ['ResultsAPI', 'FixturesAPI', 'DB_CONFIG']
__version__ = '1.0.0'
