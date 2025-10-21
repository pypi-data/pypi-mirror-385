# 🎯 MACKOLIK VERİ TOPLAMA SİSTEMİ

Modüler, temiz ve her projede kullanılabilir veri toplama sistemi.

---

## 📦 MODÜL YAPISI

```
data_collector/              # Ana modül (her projede kullan)
├── __init__.py             # API'leri dışarı açar
├── config.py               # Tek yapılandırma yeri
├── api_client.py           # Ortak API fonksiyonları
├── results.py              # Biten maçlar API'si
├── fixtures.py             # Gelecek maçlar API'si
└── README.md               # Modül dokümantasyonu
```

---

## 🚀 HIZLI BAŞLANGIÇ

### 1️⃣ Manuel Kullanım (3 satır)

```python
from data_collector import ResultsAPI, FixturesAPI

results = ResultsAPI()
results.auto_update()  # Dün + Bugün + Yarın

fixtures = FixturesAPI()
fixtures.update_fixtures(save_to_db=True)  # 3 günlük fikstür
```

**Çalıştır:**
```bash
python hizli_baslangic.py
```

### 2️⃣ Otomatik Servis (Tavsiye Edilen)

**Windows (En Kolay):**
```bash
python setup_scheduler.py  # Her gün 00:00'da otomatik çalışır
```

**Sunucu (Sürekli Çalışan):**
```bash
pip install apscheduler
python background_service.py  # Arka planda sürekli çalışır
```

**Docker (Profesyonel):**
```bash
docker-compose up -d  # Container olarak çalışır
```

---

## 📚 KULLANIM ÖRNEKLERİ

### Bugünü Güncelle
```python
from data_collector import ResultsAPI

results = ResultsAPI()
results.update_today()
```

### Tarih Aralığı
```python
results.update_date_range('01/08/2024', '20/10/2025')
```

### Sadece Veri Çek (DB'ye kaydetme)
```python
data = results.fetch_results_by_date('15/10/2025')
print(data.head())
```

### 3 Günlük Fikstür
```python
from data_collector import FixturesAPI

fixtures = FixturesAPI()
data = fixtures.get_next_3_days()
```

**Daha fazla örnek:** `ornek_kullanim.py` dosyasına bak!

---

## 📁 DOSYA REHBERİ

| Dosya | Ne İşe Yarar | Ne Zaman Kullan |
|-------|--------------|-----------------|
| `hizli_baslangic.py` | 3 satır hızlı kullanım | İlk test için |
| `ornek_kullanim.py` | 10 farklı kullanım örneği | Referans için |
| `auto_update_service.py` | Task Scheduler servisi | Windows otomatik güncelleme |
| `background_service.py` | Sürekli çalışan servis | Sunucuda sürekli çalıştırmak için |
| `docker_service.py` | Docker container servisi | Cloud/VPS'de çalıştırmak için |
| `setup_scheduler.py` | Task Scheduler kurulum | Windows otomatik görev oluştur |

---

## ⚙️ YAPILANDIRMA

**Tek dosyada:** `data_collector/config.py`

```python
DB_CONFIG = {
    'host': '167.71.74.229',
    'port': 5432,
    'database': 'mackolik_db',
    'user': 'mackolik_user',
    'password': 'GucluSifre123!'
}
```

---

## 🔄 OTOMATİK GÜNCELLEME

3 yöntem var:

### 1️⃣ Windows Task Scheduler (Tavsiye - PC için)
```bash
python setup_scheduler.py
```
✅ Her gün 00:00'da otomatik çalışır  
✅ Bilgisayar kapansa bile kaydedilir  
✅ 1 komutla kurulum  

### 2️⃣ Python Background Service (Tavsiye - Sunucu için)
```bash
pip install apscheduler
python background_service.py
```
✅ Sürekli çalışır (daemon)  
✅ Hata durumunda retry  
✅ Detaylı log tutma  

### 3️⃣ Docker + Cron (Profesyonel - Cloud için)
```bash
docker-compose up -d
```
✅ İzole çalışır  
✅ Restart policy  
✅ Taşınabilir  

**Detaylı kurulum:** `SERVICE_KURULUM.md` dosyasına bak!

---

## 📊 LOG SİSTEMİ

Tüm işlemler `logs/` klasöründe kaydedilir:

```
logs/
├── update_20251020.log      # Günlük loglar
├── service_20251020.log     # Servis logları
└── ...
```

**Log İzle:**
```bash
# Windows
type logs\update_20251020.log

# Linux/Mac
tail -f logs/update_20251020.log
```

---

## 🎯 ÖZELLİKLER

- ✅ **Modüler Yapı** - Her projede kullanılabilir
- ✅ **Temiz Kod** - DRY prensibi uygulandı
- ✅ **Hızlı** - BULK INSERT (1000 maç < 1 saniye)
- ✅ **Güvenilir** - Retry mekanizması (3 deneme)
- ✅ **Otomatik** - 3 farklı servis yöntemi
- ✅ **Dokümanlı** - Her dosya detaylı açıklamalı
- ✅ **Test Edildi** - Çalışır durumda ✓

---

## 🔧 BAKIM

### Veritabanı Ayarlarını Değiştir
→ `data_collector/config.py` düzenle

### Servis Çalışma Saatini Değiştir
→ `SERVICE_KURULUM.md` dosyasına bak

### Yeni Özellik Ekle
1. `data_collector/api_client.py` - ortak fonksiyon ekle
2. `data_collector/results.py` veya `fixtures.py` - özel mantık ekle
3. `data_collector/__init__.py` - dışarı aç

---

## 📞 DESTEK

**Sorun mu var?**
1. Log dosyalarını kontrol et: `logs/`
2. Modül dokümantasyonunu oku: `data_collector/README.md`
3. Servis kurulum kılavuzunu oku: `SERVICE_KURULUM.md`
4. Örnek kullanımları incele: `ornek_kullanim.py`

---

## 🎓 ÖĞRENME KAYNAKLARI

| Dosya | Seviye | İçerik |
|-------|--------|--------|
| `hizli_baslangic.py` | Başlangıç | 3 satırda kullanım |
| `ornek_kullanim.py` | Orta | 10 farklı senaryo |
| `data_collector/README.md` | İleri | API dokümantasyonu |
| `SERVICE_KURULUM.md` | Profesyonel | Servis kurulumu |

---

## 🚀 BAŞLARKEN

1. **İlk Test:**
   ```bash
   python hizli_baslangic.py
   ```

2. **Otomatik Kurulum:**
   ```bash
   python setup_scheduler.py  # Windows
   # veya
   python background_service.py  # Sunucu
   ```

3. **Kendi Projenizde Kullanın:**
   ```python
   from data_collector import ResultsAPI, FixturesAPI
   # Artık her projede kullanabilirsiniz!
   ```

---

## 📦 KURULUM

```bash
# Gereksinimler
pip install -r requirements.txt

# Test
python hizli_baslangic.py

# Otomatik servis kur
python setup_scheduler.py
```

---

## ✅ BAŞARILI KURULUM KONTROLÜ

```python
# Test scripti çalıştır
python test_data_collector.py

# Başarılı ise göreceksiniz:
# ✅ SONUÇLAR: XXX maç eklendi
# ✅ FİKSTÜRLER: XXX maç eklendi
```

---

**🎉 Artık hazırsınız! Her projede bu modülü kullanabilirsiniz!**
