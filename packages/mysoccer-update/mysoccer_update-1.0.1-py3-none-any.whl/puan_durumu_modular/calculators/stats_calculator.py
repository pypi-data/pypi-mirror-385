"""
📊 STATS CALCULATOR
İstatistik hesaplamaları (ÜST/ALT, BTTS, İY istatistikleri)
"""

import pandas as pd
from typing import Dict, Any
from .base_calculator import BaseCalculator


class StatsCalculator(BaseCalculator):
    """Takım istatistiklerini hesaplayan sınıf"""
    
    def calculate(self, team_id: int) -> Dict[str, Any]:
        """
        Bir takımın tüm istatistiklerini hesapla
        
        Args:
            team_id: Takım ID'si
            
        Returns:
            Dict: Tüm istatistikler
        """
        matches = self.get_team_matches(team_id)
        home_matches = matches['home']
        away_matches = matches['away']
        
        # Temel istatistikler
        total_matches = len(home_matches) + len(away_matches)
        
        if total_matches == 0:
            return None
        
        # Her kategori için istatistikleri hesapla
        over_under_stats = self._calculate_over_under(home_matches, away_matches)
        btts_stats = self._calculate_btts(home_matches, away_matches)
        halftime_stats = self._calculate_halftime(home_matches, away_matches)
        goal_stats = self._calculate_goal_stats(home_matches, away_matches)
        
        # Tüm istatistikleri birleştir
        stats = {
            'total_matches': total_matches,
            'home_matches': len(home_matches),
            'away_matches': len(away_matches),
            **over_under_stats,
            **btts_stats,
            **halftime_stats,
            **goal_stats
        }
        
        return stats
    
    def _calculate_over_under(self, home_matches: pd.DataFrame, away_matches: pd.DataFrame) -> Dict[str, int]:
        """2.5 ÜST/ALT istatistiklerini hesapla"""
        
        # Ev sahibi maçları
        home_matches = home_matches.copy()
        home_matches['total_goals'] = home_matches['ft_home'] + home_matches['ft_away']
        home_over = len(home_matches[home_matches['total_goals'] >= 3])
        home_under = len(home_matches[home_matches['total_goals'] <= 2])
        
        # ÜST-OK: Maç üst + takım kendisi en az 2 gol attı
        home_over_ok = len(home_matches[
            (home_matches['total_goals'] >= 3) & (home_matches['ft_home'] >= 2)
        ])
        
        # ALT-OK: Maç alt + takım defansif oynadı
        home_under_ok = len(home_matches[
            (home_matches['total_goals'] <= 2) & 
            ((home_matches['ft_away'] == 0) |  # Hiç yemedi
             (home_matches['ft_away'] == 1) |  # 1 yedi
             ((home_matches['ft_away'] == 2) & (home_matches['ft_home'] == 0)))  # 2 yiyip atmadı
        ])
        
        # Deplasman maçları
        away_matches = away_matches.copy()
        away_matches['total_goals'] = away_matches['ft_home'] + away_matches['ft_away']
        away_over = len(away_matches[away_matches['total_goals'] >= 3])
        away_under = len(away_matches[away_matches['total_goals'] <= 2])
        
        away_over_ok = len(away_matches[
            (away_matches['total_goals'] >= 3) & (away_matches['ft_away'] >= 2)
        ])
        
        away_under_ok = len(away_matches[
            (away_matches['total_goals'] <= 2) & 
            ((away_matches['ft_home'] == 0) |
             (away_matches['ft_home'] == 1) |
             ((away_matches['ft_home'] == 2) & (away_matches['ft_away'] == 0)))
        ])
        
        return {
            'over': home_over + away_over,
            'under': home_under + away_under,
            'over_ok': home_over_ok + away_over_ok,
            'under_ok': home_under_ok + away_under_ok
        }
    
    def _calculate_btts(self, home_matches: pd.DataFrame, away_matches: pd.DataFrame) -> Dict[str, int]:
        """Karşılıklı Gol (BTTS) istatistiklerini hesapla"""
        
        # KGVAR: Her iki takım da gol attı
        home_btts = len(home_matches[(home_matches['ft_home'] > 0) & (home_matches['ft_away'] > 0)])
        away_btts = len(away_matches[(away_matches['ft_home'] > 0) & (away_matches['ft_away'] > 0)])
        
        # KGYOK: En az bir takım gol atmadı
        home_btts_no = len(home_matches[(home_matches['ft_home'] == 0) | (home_matches['ft_away'] == 0)])
        away_btts_no = len(away_matches[(away_matches['ft_home'] == 0) | (away_matches['ft_away'] == 0)])
        
        return {
            'btts': home_btts + away_btts,
            'btts_no': home_btts_no + away_btts_no
        }
    
    def _calculate_halftime(self, home_matches: pd.DataFrame, away_matches: pd.DataFrame) -> Dict[str, int]:
        """İlk yarı istatistiklerini hesapla"""
        
        # Ev sahibi maçları
        home_ht_over_05 = len(home_matches[(home_matches['ht_home'] + home_matches['ht_away']) >= 1])
        home_ht_under_05 = len(home_matches[(home_matches['ht_home'] + home_matches['ht_away']) == 0])
        home_ht_btts = len(home_matches[(home_matches['ht_home'] > 0) & (home_matches['ht_away'] > 0)])
        
        # İkinci yarı gol sayısı
        home_matches = home_matches.copy()
        home_matches['ht2_goals'] = (
            (home_matches['ft_home'] - home_matches['ht_home']) + 
            (home_matches['ft_away'] - home_matches['ht_away'])
        )
        home_ht2_over = len(home_matches[home_matches['ht2_goals'] >= 2])
        
        # Deplasman maçları
        away_ht_over_05 = len(away_matches[(away_matches['ht_home'] + away_matches['ht_away']) >= 1])
        away_ht_under_05 = len(away_matches[(away_matches['ht_home'] + away_matches['ht_away']) == 0])
        away_ht_btts = len(away_matches[(away_matches['ht_home'] > 0) & (away_matches['ht_away'] > 0)])
        
        away_matches = away_matches.copy()
        away_matches['ht2_goals'] = (
            (away_matches['ft_home'] - away_matches['ht_home']) + 
            (away_matches['ft_away'] - away_matches['ht_away'])
        )
        away_ht2_over = len(away_matches[away_matches['ht2_goals'] >= 2])
        
        return {
            'ht_over': home_ht_over_05 + away_ht_over_05,
            'ht_under': home_ht_under_05 + away_ht_under_05,
            'ht_btts': home_ht_btts + away_ht_btts,
            'ht2_over': home_ht2_over + away_ht2_over
        }
    
    def _calculate_goal_stats(self, home_matches: pd.DataFrame, away_matches: pd.DataFrame) -> Dict[str, int]:
        """Gol atma/yeme istatistiklerini hesapla"""
        
        # Ev sahibi
        home_scored = len(home_matches[home_matches['ft_home'] > 0])
        home_conceded = len(home_matches[home_matches['ft_away'] > 0])
        home_cleansheet = len(home_matches[home_matches['ft_away'] == 0])
        
        # Deplasman
        away_scored = len(away_matches[away_matches['ft_away'] > 0])
        away_conceded = len(away_matches[away_matches['ft_home'] > 0])
        away_cleansheet = len(away_matches[away_matches['ft_home'] == 0])
        
        return {
            'scored': home_scored + away_scored,
            'conceded': home_conceded + away_conceded,
            'cleansheet': home_cleansheet + away_cleansheet
        }
