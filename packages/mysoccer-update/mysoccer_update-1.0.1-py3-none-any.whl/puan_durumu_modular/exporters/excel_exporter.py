"""
📊 EXCEL EXPORTER
Excel dosyası oluşturma ve formatlama
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from openpyxl.utils import get_column_letter


class ExcelExporter:
    """Excel'e veri aktarma sınıfı"""
    
    def __init__(self, filename: str = None):
        """
        Args:
            filename: Excel dosya adı (None ise otomatik oluşturulur)
        """
        self.filename = filename or self._generate_filename()
        self.sheets_data = {}
    
    def _generate_filename(self) -> str:
        """Otomatik dosya adı oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f'puan_durumu_haftalik_{timestamp}.xlsx'
    
    def add_sheet(self, sheet_name: str, df: pd.DataFrame, header_info: Dict[str, str] = None):
        """
        Bir sayfa ekle
        
        Args:
            sheet_name: Sayfa adı
            df: Veri DataFrame'i
            header_info: Üst bilgi (başlıklar)
        """
        self.sheets_data[sheet_name] = {
            'df': df,
            'header_info': header_info or {}
        }
    
    def export(self) -> str:
        """
        Tüm sayfaları Excel'e aktar
        
        Returns:
            str: Oluşturulan dosya adı
        """
        print(f"\n💾 Excel'e yazılıyor: {self.filename}")
        
        with pd.ExcelWriter(self.filename, engine='openpyxl') as writer:
            for sheet_name, data in self.sheets_data.items():
                df = data['df']
                header_info = data['header_info']
                
                # DataFrame'i yaz (başlık için 3 satır boşluk bırak)
                df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=3)
                
                # Worksheet'i al ve formatla
                worksheet = writer.sheets[sheet_name]
                self._format_sheet(worksheet, df, header_info)
        
        print(f"✅ Excel dosyası oluşturuldu: {self.filename}")
        return self.filename
    
    def _format_sheet(self, worksheet, df: pd.DataFrame, header_info: Dict[str, str]):
        """
        Worksheet'i formatla (başlıklar ve sütun genişlikleri)
        
        Args:
            worksheet: Openpyxl worksheet objesi
            df: DataFrame
            header_info: Başlık bilgileri
        """
        # Başlık bilgilerini ekle
        if header_info:
            row = 1
            for key, value in header_info.items():
                worksheet[f'A{row}'] = value
                row += 1
        
        # Sütun genişliklerini ayarla
        column_widths = self._get_column_widths(df)
        for col_idx, width in column_widths.items():
            col_letter = get_column_letter(col_idx)
            worksheet.column_dimensions[col_letter].width = width
    
    def _get_column_widths(self, df: pd.DataFrame) -> Dict[int, int]:
        """
        DataFrame'e göre sütun genişliklerini hesapla
        
        Args:
            df: DataFrame
            
        Returns:
            Dict: {kolon_index: genişlik}
        """
        widths = {}
        
        for idx, col in enumerate(df.columns, start=1):
            col_name = str(col)
            
            # Kolon adına göre genişlik belirle
            if col_name in ['season_id', 'Season ID']:
                widths[idx] = 10
            elif col_name in ['League', 'league', 'Lig']:
                widths[idx] = 20
            elif col_name in ['Country', 'country', 'Ülke']:
                widths[idx] = 15
            elif col_name in ['Takım', 'Ev Sahibi', 'Deplasman', 'team_name', 'home_team', 'away_team']:
                widths[idx] = 25
            elif col_name in ['match_id', 'Match ID', 'Ev Takım ID', 'Deplasman Takım ID']:
                widths[idx] = 12
            elif col_name in ['Tarih', 'match_date']:
                widths[idx] = 12
            elif col_name in ['Hafta', 'hafta']:
                widths[idx] = 8
            elif col_name.startswith('Oran'):
                widths[idx] = 8
            elif col_name.startswith('EV-') or col_name.startswith('DEP-'):
                widths[idx] = 10
            elif col_name.startswith('İY'):
                widths[idx] = 10
            elif col_name in ['Sıra', 'O', 'G', 'B', 'M', 'A', 'Y', 'P', 'MS', 'DS']:
                widths[idx] = 6
            elif col_name in ['AV', 'Saat']:
                widths[idx] = 8
            else:
                widths[idx] = 10
        
        return widths


class WeeklyStandingsExporter(ExcelExporter):
    """Haftalık puan durumu için özelleştirilmiş exporter"""
    
    def __init__(self, season_id: int, league_name: str, country: str):
        """
        Args:
            season_id: Sezon ID'si
            league_name: Lig adı
            country: Ülke
        """
        filename = f'puan_durumu_haftalik_{season_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        super().__init__(filename)
        
        self.season_id = season_id
        self.league_name = league_name
        self.country = country
    
    def add_standings_sheet(self, sheet_name: str, df: pd.DataFrame, is_last_8: bool = False):
        """
        Puan durumu sayfası ekle
        
        Args:
            sheet_name: Sayfa adı
            df: Puan durumu DataFrame
            is_last_8: Son 8 maç formu mu?
        """
        # DataFrame'i hazırla
        df = self._prepare_standings_df(df)
        
        # Başlık bilgileri
        if is_last_8:
            header_info = {
                'title': f"🔥 {self.league_name} - Son 8 Maç Formu",
                'subtitle': f"🌍 {self.country} (Güncel Form Analizi)",
                'timestamp': f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        else:
            header_info = {
                'title': f"🏆 {self.league_name}",
                'subtitle': f"🌍 {self.country}",
                'timestamp': f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        
        self.add_sheet(sheet_name, df, header_info)
    
    def add_matches_sheet(self, sheet_name: str, df: pd.DataFrame, is_last_8: bool = False):
        """
        Haftalık maçlar sayfası ekle
        
        Args:
            sheet_name: Sayfa adı
            df: Maçlar DataFrame
            is_last_8: Son 8 maç verisi mi?
        """
        # DataFrame'i hazırla
        df = self._prepare_matches_df(df)
        
        # Başlık bilgileri
        if is_last_8:
            header_info = {
                'title': f"🔥 {self.league_name} - Son 8 Maç Detayları",
                'subtitle': f"🌍 {self.country}",
                'timestamp': f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        else:
            header_info = {
                'title': f"⚽ {self.league_name} - Haftalık Maçlar",
                'subtitle': f"🌍 {self.country}",
                'timestamp': f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        
        self.add_sheet(sheet_name, df, header_info)
    
    def _prepare_standings_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Puan durumu DataFrame'ini hazırla ve kolon isimlerini düzenle"""
        df = df.copy()
        
        # Kolon isimlerini Türkçeleştir
        rename_map = {
            'over': 'ÜST',
            'under': 'ALT',
            'over_ok': 'ÜST-OK',
            'under_ok': 'ALT-OK',
            'btts': 'KGVAR',
            'btts_no': 'KGYOK',
            'ht_over': 'İY-OVER',
            'ht_under': 'İY-UNDER',
            'ht_btts': 'İY-KGVAR',
            'ht2_over': 'İY2-OVER',
            'scored': 'GAL',
            'conceded': 'GYL',
            'cleansheet': 'CS',
            'home_matches': 'EV-Maç',
            'away_matches': 'DEP-Maç',
            'total_matches': 'Toplam-Maç'
        }
        
        df = df.rename(columns=rename_map)
        
        # Gereksiz kolonları kaldır (eğer varsa)
        cols_to_drop = ['EV-Maç', 'DEP-Maç', 'Toplam-Maç']
        df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')
        
        return df
    
    def _prepare_matches_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Maçlar DataFrame'ini hazırla ve kolon isimlerini düzenle"""
        df = df.copy()
        
        # Kolon isimlerini düzenle (eğer yoksa)
        rename_map = {
            'match_id': 'Match ID',
            'season_id': 'Season ID',
            'league': 'League',
            'country': 'Country',
            'match_date': 'Tarih',
            'match_time': 'Saat',
            'home_team_id': 'Ev Takım ID',
            'home_team': 'Ev Sahibi',
            'away_team_id': 'Deplasman Takım ID',
            'away_team': 'Deplasman',
            'ht_home': 'İY-MS',
            'ht_away': 'İY-DS',
            'ft_home': 'MS',
            'ft_away': 'DS',
            'status': 'Status',
            'home_odd': 'Oran-1',
            'draw_odd': 'Oran-X',
            'away_odd': 'Oran-2',
            'hafta': 'Hafta'
        }
        
        df = df.rename(columns=rename_map)
        
        return df
    
    def export_with_summary(self) -> Dict[str, any]:
        """
        Export yap ve özet bilgi döndür
        
        Returns:
            Dict: Özet bilgiler (dosya adı, sayfa sayısı, vb.)
        """
        filename = self.export()
        
        summary = {
            'filename': filename,
            'sheets': list(self.sheets_data.keys()),
            'total_sheets': len(self.sheets_data),
            'season_id': self.season_id,
            'league': self.league_name,
            'country': self.country,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Her sayfa için satır sayısı
        for sheet_name, data in self.sheets_data.items():
            summary[f'{sheet_name}_rows'] = len(data['df'])
        
        return summary
