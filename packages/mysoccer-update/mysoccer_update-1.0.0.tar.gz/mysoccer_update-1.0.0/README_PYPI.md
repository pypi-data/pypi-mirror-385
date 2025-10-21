# MySoccer Update

🚀 Mackolik.com API'den futbol maç verilerini çeken profesyonel Python kütüphanesi.

## 📦 Kurulum

```bash
pip install mysoccer-update
```

## 🚀 Hızlı Başlangıç

```python
from mysoccer_update import ResultsAPI, FixturesAPI

# Sonuçları güncelle
results = ResultsAPI()
results.auto_update()  # Dün + Bugün + Yarın

# Fikstürleri çek
fixtures = FixturesAPI()
data = fixtures.get_next_3_days()  # 3 günlük fikstür
```

## ✨ Özellikler

- ✅ **Modüler Yapı** - Temiz ve genişletilebilir
- ✅ **Hızlı** - BULK INSERT ile saniyede 1000+ maç
- ✅ **Güvenilir** - Otomatik retry mekanizması
- ✅ **Kolay Kullanım** - 3 satır kod yeterli
- ✅ **Otomatik Servis** - Background service desteği

## 📚 Dokümantasyon

### Sonuçlar (Biten Maçlar)

```python
from mackolik_data_collector import ResultsAPI

results = ResultsAPI()

# Bugünü güncelle
results.update_today()

# Tarih aralığı
results.update_date_range('01/08/2024', '20/10/2025')

# Tek tarih
results.update_single_date('15/10/2025')

# Otomatik (Dün + Bugün + Yarın)
results.auto_update()
```

### Fikstürler (Gelecek Maçlar)

```python
from mackolik_data_collector import FixturesAPI

fixtures = FixturesAPI()

# 3 günlük fikstür
data = fixtures.get_next_3_days()

# Veritabanına kaydet
fixtures.save_to_database(data)

# Excel'e aktar
fixtures.export_to_excel(data, 'fixtures.xlsx')

# Hepsi bir arada
fixtures.update_fixtures(save_to_db=True, export_excel=True)
```

## ⚙️ Yapılandırma

### 🔒 Güvenli Yöntem: .env Dosyası (Önerilen)

```bash
# .env dosyası oluştur (proje kök dizininde)
DB_HOST=your-host.com
DB_PORT=5432
DB_NAME=mackolik_db
DB_USER=your_user
DB_PASSWORD=your_password
```

```python
from mackolik_data_collector import ResultsAPI

# .env dosyasından otomatik okur!
results = ResultsAPI()
results.update_today()
```

### ⚠️ Alternatif: Manuel Config (Önerilmez)

```python
from mackolik_data_collector.config import DB_CONFIG

# Veritabanı ayarları
DB_CONFIG['host'] = 'your-host'
DB_CONFIG['port'] = 5432
DB_CONFIG['database'] = 'your-db'
DB_CONFIG['user'] = 'your-user'
DB_CONFIG['password'] = 'your-password'
```

> **🔐 Güvenlik Uyarısı**: Şifreleri **asla** kodun içine yazmayın! `.env` dosyası kullanın ve `.gitignore`'a ekleyin.

## 🔄 Otomatik Güncelleme

### Background Service (Opsiyonel)

```bash
pip install mysoccer-update[scheduler]
```

```python
from mysoccer_update.service import DataUpdateService

service = DataUpdateService()
service.start()  # Her gün 00:00, 12:00, 18:00'de otomatik çalışır
```

## 📊 Gereksinimler

- Python 3.9+
- requests
- pandas
- psycopg (PostgreSQL için)
- openpyxl (Excel export için)

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🔗 Bağlantılar

- **GitHub**: https://github.com/ahmety/mysoccer-update
- **PyPI**: https://pypi.org/project/mysoccer-update
- **Dokümantasyon**: https://github.com/ahmety/mysoccer-update#readme

## 💡 Örnek Kullanım

```python
# Günlük rutin güncelleme
from mysoccer_update import ResultsAPI, FixturesAPI

def daily_update():
    # Sonuçları güncelle
    results = ResultsAPI()
    stats = results.auto_update()
    print(f"✅ {stats['total_inserted']} maç eklendi")
    
    # Fikstürleri güncelle
    fixtures = FixturesAPI()
    data = fixtures.update_fixtures(save_to_db=True)
    print(f"✅ {len(data)} fikstür eklendi")

if __name__ == '__main__':
    daily_update()
```

## ⭐ Yıldız Vermeyi Unutmayın!

Eğer bu kütüphaneyi beğendiyseniz, GitHub'da yıldız vermeyi unutmayın! ⭐
