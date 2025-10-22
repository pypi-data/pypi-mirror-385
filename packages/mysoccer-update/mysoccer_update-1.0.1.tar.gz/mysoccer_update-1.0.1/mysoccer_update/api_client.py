"""
🌐 API CLIENT
=============

Mackolik API'sine bağlanır ve ham veriyi çeker.
Ortak fonksiyonlar burada - DRY prensibi!
"""

import requests
import pandas as pd
from .config import API_CONFIG


class MackolikAPIClient:
    """Mackolik API ile iletişim"""
    
    def __init__(self):
        self.base_url = API_CONFIG['base_url']
        self.headers = API_CONFIG['headers']
    
    def fetch_raw_data(self, date: str) -> pd.DataFrame:
        """
        Belirli bir tarihteki ham maç verilerini çek
        
        Args:
            date (str): 'DD/MM/YYYY' formatında tarih
            
        Returns:
            DataFrame: Ham API verisi
        """
        response = requests.get(
            f'{self.base_url}?date={date}',
            headers=self.headers
        )
        response.raise_for_status()
        
        data = pd.DataFrame(response.json()['m'])
        
        # Kolon sayısı kontrolü
        base_cols = [c for c in data.columns if isinstance(c, int)]
        if len(base_cols) != 38:
            print(f'⚠️ WARNING: Expected 38 columns, got {len(base_cols)}')
        
        return data
    
    def expand_and_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Ham veriyi genişlet ve dönüştür (column 15 ve 36)
        
        Args:
            data (DataFrame): Ham API verisi
            
        Returns:
            DataFrame: Genişletilmiş ve dönüştürülmüş veri
        """
        # Column 15'i genişlet (dictionary)
        if 15 in data.columns:
            col_15_expanded = pd.json_normalize(data[15])
            col_15_expanded.columns = [f'15_{col}' for col in col_15_expanded.columns]
            data = pd.concat([data, col_15_expanded], axis=1)
        
        # Column 36'yı genişlet (list)
        if 36 in data.columns:
            col_36_list = data[36].apply(lambda x: x if isinstance(x, list) else [])
            max_len = max(col_36_list.apply(len)) if len(col_36_list) > 0 else 0
            for i in range(max_len):
                data[f'36_{i}'] = col_36_list.apply(lambda x: x[i] if i < len(x) else None)
        
        return data
    
    def rename_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Kolonları anlamlı isimlere çevir
        
        Args:
            data (DataFrame): Genişletilmiş veri
            
        Returns:
            DataFrame: İsimlendirilmiş kolonlar
        """
        data.rename(columns={
            0:'match_id', 1:'home_team_id', 2:'home_team', 3:'away_team_id', 4:'away_team',
            5:'status', 6:'extra_1', 7:'extra_2', 8:'live_home', 9:'live_away',
            10:'flag_1', 11:'flag_2', 12:'flag_3', 13:'flag_4',
            14:'stage_id', 15:'match_detail_data', 16:'match_time', 17:'started',
            18:'home_odd', 19:'draw_odd', 20:'away_odd', 21:'under_odd', 22:'over_odd',
            23:'has_odds', 24:'odd_4', 25:'odd_5', 26:'odd_6', 27:'odd_7', 28:'odd_8',
            29:'ft_home', 30:'ft_away', 31:'ht_home', 32:'ht_away',
            33:'empty', 34:'match_type', 35:'match_date', 36:'league_data', 37:'active',
            '15_aeleme':'detail_aeleme', '15_e':'detail_e', '15_goal':'detail_goal',
            '15_h1':'detail_ht_home', '15_h2':'detail_sh_home',
            '15_k1':'detail_ht_away', '15_k2':'detail_sh_away',
            '15_ogd':'detail_ogd', '15_tId':'detail_team_id',
            '15_ba':'detail_ba', '15_ban':'detail_ban', '15_bh':'detail_bh',
            '15_bhn':'detail_bhn', '15_f1':'detail_f1', '15_f2':'detail_f2',
            '36_0':'country_id', '36_1':'country', '36_2':'league_id', '36_3':'league',
            '36_4':'season_id', '36_5':'season', '36_6':'league_extra_1',
            '36_7':'league_extra_2', '36_8':'league_extra_3', '36_9':'league_short',
            '36_10':'league_extra_4', '36_11':'sport_type'
        }, inplace=True)
        
        return data
    
    def calculate_second_half_scores(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        İkinci yarı skorlarını hesapla (FT - HT)
        
        Args:
            data (DataFrame): Veri
            
        Returns:
            DataFrame: İkinci yarı skorları eklenmiş veri
        """
        data['sh_home'] = data.apply(
            lambda r: int(r['ft_home']) - int(r['ht_home']) 
            if pd.notna(r['ft_home']) and pd.notna(r['ht_home']) else None, 
            axis=1
        )
        data['sh_away'] = data.apply(
            lambda r: int(r['ft_away']) - int(r['ht_away']) 
            if pd.notna(r['ft_away']) and pd.notna(r['ht_away']) else None, 
            axis=1
        )
        return data
    
    def apply_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Doğru veri tiplerini uygula (optimizasyon)
        
        Args:
            data (DataFrame): Veri
            
        Returns:
            DataFrame: Tip dönüşümü yapılmış veri
        """
        types = {
            'match_id':'Int64', 'home_team_id':'Int32', 'away_team_id':'Int32',
            'country_id':'Int16', 'league_id':'Int32', 'season_id':'Int32', 'stage_id':'Int32',
            'status':'Int8', 'started':'Int8', 'active':'Int8', 'has_odds':'Int8', 
            'match_type':'Int8', 'sport_type':'Int8',
            'live_home':'Int8', 'live_away':'Int8', 'ht_home':'Int8', 'ht_away':'Int8',
            'sh_home':'Int8', 'sh_away':'Int8', 'ft_home':'Int8', 'ft_away':'Int8',
            'detail_ht_home':'Int8', 'detail_sh_home':'Int8', 
            'detail_ht_away':'Int8', 'detail_sh_away':'Int8',
            'home_odd':'Float32', 'draw_odd':'Float32', 'away_odd':'Float32',
            'under_odd':'Float32', 'over_odd':'Float32',
            'odd_4':'Float32', 'odd_5':'Float32', 'odd_6':'Float32', 
            'odd_7':'Float32', 'odd_8':'Float32'
        }
        
        for col, dtype in types.items():
            if col in data.columns:
                try:
                    data[col] = data[col].astype(dtype)
                except:
                    pass
        
        return data
    
    def clean_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Gereksiz kolonları temizle
        
        Args:
            data (DataFrame): Veri
            
        Returns:
            DataFrame: Temizlenmiş veri
        """
        drop_cols = [
            'extra_2', 'live_home', 'live_away', 'flag_1', 'flag_2', 'flag_3', 'flag_4',
            'match_detail_data', 'started', 'has_odds', 'odd_4', 'odd_5', 'odd_6', 
            'odd_7', 'odd_8', 'empty', 'detail_aeleme', 'detail_ba', 'detail_ban', 
            'detail_bh', 'detail_bhn', 'detail_e', 'detail_goal', 'detail_ht_home', 
            'detail_sh_home', 'detail_ht_away', 'detail_sh_away', 'detail_ogd', 
            'detail_team_id', 'detail_f1', 'detail_f2', 'league_extra_1', 
            'league_extra_2', 'league_extra_3', 'league_extra_4', 'league_data'
        ]
        
        data = data.drop(columns=[c for c in drop_cols if c in data.columns])
        return data
    
    def reorder_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Kolonları profesyonel sıraya koy
        
        Args:
            data (DataFrame): Veri
            
        Returns:
            DataFrame: Sıralanmış veri
        """
        col_order = [
            'match_id', 'match_date', 'match_time', 'status', 'match_type', 'active', 'extra_1',
            'country_id', 'country', 'league_id', 'league', 'league_short', 
            'season_id', 'season', 'stage_id',
            'home_team_id', 'home_team', 'away_team_id', 'away_team',
            'ht_home', 'ht_away', 'sh_home', 'sh_away', 'ft_home', 'ft_away',
            'home_odd', 'draw_odd', 'away_odd', 'under_odd', 'over_odd'
        ]
        
        data = data[[c for c in col_order if c in data.columns]]
        return data
    
    def fetch_and_process(self, date: str, status_filter: int = None) -> pd.DataFrame:
        """
        Tek seferde tüm işlemleri yap: çek, dönüştür, temizle
        
        Args:
            date (str): 'DD/MM/YYYY' formatında tarih
            status_filter (int): Status filtresi (None = filtresiz, 13 = status < 13)
            
        Returns:
            DataFrame: İşlenmiş veri
        """
        # 1. Ham veriyi çek
        data = self.fetch_raw_data(date)
        
        # 2. Genişlet
        data = self.expand_and_transform(data)
        
        # 3. İsimlendir
        data = self.rename_columns(data)
        
        # 4. Sadece futbol (sport_type = 1)
        data = data[data['sport_type'] == 1].reset_index(drop=True)
        
        # 5. Status filtresi (varsa) - küçüktür kontrolü
        if status_filter is not None:
            data = data[data['status'] < status_filter].reset_index(drop=True)
        
        # 6. İkinci yarı skorları
        data = self.calculate_second_half_scores(data)
        
        # 7. Veri tipleri
        data = self.apply_data_types(data)
        
        # 8. Gereksiz kolonları temizle
        data = self.clean_columns(data)
        
        # 9. Sadece futbol sütununu drop et (artık gerekli değil)
        if 'sport_type' in data.columns:
            data = data.drop(columns=['sport_type'])
        
        # 10. Kolonları sırala
        data = self.reorder_columns(data)
        
        return data
