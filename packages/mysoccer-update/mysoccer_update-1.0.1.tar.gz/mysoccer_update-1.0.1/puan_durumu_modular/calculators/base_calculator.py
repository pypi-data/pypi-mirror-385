"""
🏗️ BASE CALCULATOR
Tüm hesaplayıcılar için temel sınıf
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseCalculator(ABC):
    """Temel hesaplayıcı sınıfı - Tüm hesaplayıcılar bundan türer"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: Maç verileri DataFrame
        """
        self.df = df.copy()
        self._validate_dataframe()
    
    def _validate_dataframe(self):
        """DataFrame'in gerekli kolonlara sahip olduğunu kontrol et"""
        required_columns = [
            'match_id', 'home_team_id', 'away_team_id',
            'home_team', 'away_team', 'ft_home', 'ft_away'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            raise ValueError(f"❌ DataFrame'de eksik kolonlar: {missing_columns}")
    
    @abstractmethod
    def calculate(self, *args, **kwargs) -> Any:
        """
        Hesaplama yap - Her alt sınıf kendi implementasyonunu yapar
        """
        pass
    
    def get_all_teams(self) -> pd.DataFrame:
        """
        Tüm takımları benzersiz olarak döndür
        
        Returns:
            DataFrame: team_id ve team_name kolonlarıyla takımlar
        """
        home_teams = self.df[['home_team_id', 'home_team']].rename(
            columns={'home_team_id': 'team_id', 'home_team': 'team_name'}
        )
        away_teams = self.df[['away_team_id', 'away_team']].rename(
            columns={'away_team_id': 'team_id', 'away_team': 'team_name'}
        )
        all_teams = pd.concat([home_teams, away_teams]).drop_duplicates('team_id').reset_index(drop=True)
        
        return all_teams
    
    def get_team_matches(self, team_id: int) -> Dict[str, pd.DataFrame]:
        """
        Belirli bir takımın ev ve deplasman maçlarını döndür
        
        Args:
            team_id: Takım ID'si
            
        Returns:
            Dict: {'home': DataFrame, 'away': DataFrame}
        """
        home_matches = self.df[self.df['home_team_id'] == team_id].copy()
        away_matches = self.df[self.df['away_team_id'] == team_id].copy()
        
        return {
            'home': home_matches,
            'away': away_matches
        }
