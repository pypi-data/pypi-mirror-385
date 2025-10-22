"""
🏆 HAFTALIK PUAN DURUMU OLUŞTURUCU - MODÜLER VERSİYON
Futbol liglerinin haftalık puan durumlarını hesaplayan ve Excel'e aktaran modüler sistem

Version: 1.0.0
Author: NMaçKolik
"""

__version__ = '1.0.0'
__author__ = 'NMaçKolik'

# Ana sınıfı export et
from .main import WeeklyStandingsGenerator

__all__ = ['WeeklyStandingsGenerator']
