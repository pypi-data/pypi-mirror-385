"""
🚀 HIZLI BAŞLANGIÇ
==================

3 satır kod ile veri çekmeye başla!
"""

import sys
from pathlib import Path

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Artık hem tıklayınca hem de modül olarak çalışır!
from data_collector import ResultsAPI, FixturesAPI



# ============ SONUÇLAR (Biten Maçlar) ============
print('📊 Sonuçlar güncelleniyor...')
results = ResultsAPI()
results.auto_update()  # Dün + Bugün + Yarın

# ============ FİKSTÜRLER (Gelecek Maçlar) ============
print('\n📅 Fikstürler güncelleniyor...')
fixtures = FixturesAPI()
fixtures.update_fixtures(save_to_db=True)  # 3 günlük fikstür

print('\n✅ BİTTİ! Veriler veritabanında.')
