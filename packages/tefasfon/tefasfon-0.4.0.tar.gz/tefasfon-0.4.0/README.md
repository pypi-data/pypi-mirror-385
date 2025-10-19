# tefasfon v0.4.0

## Türkçe tercih edenler için:

***Those who prefer English can scroll down the page.***

## Açıklama

`tefasfon`, Türkiye Elektronik Fon Alım Satım Platformu (TEFAS) sitesinde yayımlanan yatırım/emeklilik fonu verilerinin çekilmesini ve analiz edilmesini sağlayan bir Python kütüphanesidir.

* Web'den tarih aralığı ve fon türüne göre veri çeker.
* Çekilen fiyat verileri üzerinden kümülatif getiri, yıllık getiri, yıllık volatilite ve Sharpe oranı gibi metrikleri hesaplar.
* Mesajlar Türkçe/İngilizce desteklidir; çıktılar doğrudan `pandas.DataFrame` olarak döner.

## Özellikler

* Seçilen tarih aralığında ve fon türünde veri çekimi
* "Genel Bilgiler" veya "Portföy Dağılımı" sekmesi
* İsteğe bağlı Excel'e kaydetme
* Türkçe/İngilizce bilgi ve hata mesajları
* Basit veya logaritmik getiri ile performans analizi
* Selenium + ChromeDriver ile canlı web verisine erişim

## Kurulum

Kütüphaneyi yüklemek için şu adımları izleyin:

1. Python'ı yükleyin: https://www.python.org/downloads/
2. Terminal veya komut istemcisinde aşağıdaki komutu çalıştırın:

```bash
pip install tefasfon
```

Belirli bir versiyonu yüklemek için:

```bash
pip install tefasfon==0.4.0
```

Yüklü versiyonu görüntülemek için:

```bash
pip show tefasfon
```

## Fonksiyonlar

### `fetch_tefas_data`

TEFAS web sitesinden fon veya portföy verisi çeker.

Parametreler:

* `fund_type_code` (int): Fon tipi kodu
  * 0: Menkul Kıymet Yatırım Fonları
  * 1: Emeklilik Fonları
  * 2: Borsa Yatırım Fonları
  * 3: Gayrimenkul Yatırım Fonları
  * 4: Girişim Sermayesi Yatırım Fonları
* `tab_code` (int): Sekme kodu
  * 0: Genel Bilgiler
  * 1: Portföy Dağılımı
* `start_date` (str): Başlangıç tarihi, 'gg.aa.yyyy' formatında (örn. '17.07.2025')
* `end_date` (str): Bitiş tarihi, 'gg.aa.yyyy' formatında (örn. '18.07.2025')
* `fund_codes` (list | None): "Fon Kodu" sütununda tam eşleşme için kod listesi (opsiyonel)
* `fund_title_contains` (list | None): "Fon Adı" sütununda kısmi arama için terim listesi (opsiyonel)
* `lang` (str): "tr" veya "en" (varsayılan `"tr"`)
* `save_to_excel` (bool): True verilirse, Excel dosyasına kaydeder (varsayılan `False`)
* `wait_seconds` (int): Web işlemleri arası bekleme süresi (varsayılan `3`)

Dönüş:

* `pandas.DataFrame` (veya veri yoksa boş DataFrame)

## Örnek Kullanım

```python
from tefasfon import fetch_tefas_data

df = fetch_tefas_data(
    fund_type_code=0,
    tab_code=0,
    start_date="01.09.2025",
    end_date="30.09.2025",
    save_to_excel=True
)

df_codes = fetch_tefas_data(
    fund_type_code=0,
    tab_code=0,
    start_date="01.09.2025",
    end_date="30.09.2025",
    fund_codes=["ABC", "XYZ"], # Fon kodu değerleri
    save_to_excel=False
)

df_title = fetch_tefas_data(
    fund_type_code=0,
    tab_code=0,
    start_date="01.09.2025",
    end_date="30.09.2025",
    fund_title_contains=["Altın", "Teknoloji"], # Ünvan içinde geçen terimler
    save_to_excel=False
)
```

### `analyze_funds`

`fetch_tefas_data()` ile elde edilen fiyat verisi üzerinden performans metrikleri hesaplar.

Parametreler:

* `df` (pd.DataFrame): `fetch_tefas_data()` çıktısı (Genel Bilgiler sekmesi)
* `price_col` (str): Fiyat sütunu (varsayılan `"Fiyat"`)
* `fund_code_col` (str): Fon kodu sütunu (varsayılan `"Fon Kodu"`)
* `fund_title_col` (str): Fon adı sütunu (varsayılan `"Fon Adı"`)
* `date_col` (str): Tarih sütunu (varsayılan `"Tarih"`)
* `freq` (str): Getiri sıklığı. Desteklenen kısaltmalar:
  * `"D"` (günlük), `"B"` (iş günü), `"W"` (haftalık), `"M"` (aylık), `"Q"` (çeyreklik), `"A"`/`"Y"` (yıllık)
* `risk_free_annual` (float): Risksiz yıllık oran (örn. `0.10` = %10)
* `periods_per_year` (int | None): Yıllık dönem sayısı; boş bırakılırsa frekansa göre otomatik hesaplanır.
* `method` (str): "simple" veya "log" (varsayılan `"simple"`)
* `drop_empty` (bool): Hatalı/eksik verili fonları dışarıda bırakır (varsayılan `True`)
* `lang` (str): `"tr"` veya `"en"` (varsayılan `"tr"`)

Dönüş:

* `pandas.DataFrame`

## Örnek Kullanım

```python
from tefasfon import fetch_tefas_data, analyze_funds

df = fetch_tefas_data(
    fund_type_code=0,
    tab_code=0,
    start_date="01.09.2025",
    end_date="30.09.2025"
)

# İş günü frekansı + log getiri + %10 risksiz oran
metrics = analyze_funds(
    df,
    freq="B",
    method="log",
    risk_free_annual=0.10
)
```

## Notlar

* Kütüphane, TEFAS'ın web sitesindeki verilere bağımlıdır. Herhangi bir değişiklikte veya bakımda, veri çekilemeyebilir. Lütfen [TEFAS](https://www.tefas.gov.tr/TarihselVeriler.aspx) adresinden veri durumu ve güncelliğini kontrol edin.
* Selenium ve ChromeDriver kullanılır. Bilgisayarınızda Google Chrome kurulu olmalı ve güncel olmalıdır.
* Kütüphanenin geliştirilmesi ve iyileştirilmesi için geri bildirimlerinizi bekliyorum. GitHub reposuna katkıda bulunun: [GitHub Repo](https://github.com/urazakgul/tefasfon)
* Herhangi bir sorun veya öneride lütfen GitHub reposundaki "Issue" bölümünden yeni bir konu açarak bildirim sağlayın: [GitHub Issues](https://github.com/urazakgul/tefasfon/issues)

## Sürüm Notları

### v0.4.0 - 18/10/2025

* `analyze_funds` fonksiyonu eklendi.
* Minimize edilen tarayıcı penceresi artık gösterilmiyor.

### v0.3.0 - 15/10/2025

* `fund_codes` parametresi ile "Fon Kodu" üzerinden tam eşleşme filtresi eklendi.
* `fund_title_contains` parametresi ile "Fon Adı" içinde kısmi arama filtresi eklendi.

### v0.2.0 - 05/09/2025

* Veri bulunmadığında güvenli dönüş sağlandı.
* WebDriver/TFLite logları kaldırıldı.
* Gün bazında ilerleme panelleri eklendi.
* Açılır menü hata mesajı yerelleştirildi.

### v0.1.0 - 20/07/2025

* İlk sürüm yayınlandı.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.

## For those who prefer English:

## Description

`tefasfon` is a Python library that allows fetching and analyzing investment and pension fund data published on the Turkey Electronic Fund Trading Platform (TEFAS) website.

* Fetches data from the web by date range and fund type.
* Calculates metrics such as cumulative return, annual return, annual volatility, and Sharpe ratio based on the fetched price data.
* Supports Turkish/English messages, with outputs returned directly as a `pandas.DataFrame`.

## Features

* Fetches data for the selected date range and fund type.
* "General Information" or "Portfolio Breakdown" tabs
* Optional export to Excel
* Turkish/English info and error messages
* Performance analysis with simple or logarithmic returns
* Live web data access via Selenium + ChromeDriver

## Installation

To use the package, follow these steps:

1. Install Python: https://www.python.org/downloads/
2. Open your terminal or command prompt and run:

```bash
pip install tefasfon
```

To install a specific version:

```bash
pip install tefasfon==0.4.0
```

To check the installed version:

```bash
pip show tefasfon
```

## Functions

### `fetch_tefas_data`

Fetches fund or portfolio data from the TEFAS website.

Parameters:

* `fund_type_code` (int): Fund type code
  * 0: Securities Mutual Funds
  * 1: Pension Funds
  * 2: Exchange Traded Funds
  * 3: Real Estate Investment Funds
  * 4: Venture Capital Investment Funds
* `tab_code` (int): Tab code
  * 0: General Information
  * 1: Portfolio Breakdown
* `start_date` (str): Start date, in 'dd.mm.yyyy' format (e.g. '17.07.2025')
* `end_date` (str): End date, in 'dd.mm.yyyy' format (e.g. '18.07.2025')
* `fund_codes` (list | None): List of codes for exact matching in the "Fund Code" column (optional)
* `fund_title_contains` (list | None): List of terms for substring matching in the "Fund Title" column (optional)
* `lang` (str): "tr" or "en" (default `"tr"`)
* `save_to_excel` (bool): If True, saves the result to an Excel file (default: `False`)
* `wait_seconds` (int): Wait time between web actions (default: `3`)

Returns:

* `pandas.DataFrame` (or an empty DataFrame if no data)

## Example

```python
from tefasfon import fetch_tefas_data

df = fetch_tefas_data(
    fund_type_code=0,
    tab_code=0,
    start_date="01.09.2025",
    end_date="30.09.2025",
    lang="en",
    save_to_excel=True
)

df_codes = fetch_tefas_data(
    fund_type_code=0,
    tab_code=0,
    start_date="01.09.2025",
    end_date="30.09.2025",
    fund_codes=["ABC", "XYZ"], # Exact fund codes
    lang="en",
    save_to_excel=False
)

df_title = fetch_tefas_data(
    fund_type_code=0,
    tab_code=0,
    start_date="01.09.2025",
    end_date="30.09.2025",
    fund_title_contains=["Gold", "Technology"], # Terms contained in the fund title
    lang="en",
    save_to_excel=False
)
```

### `analyze_funds`

Calculates performance metrics based on the price data fetched using `fetch_tefas_data()`.

Parameters:

* `df` (pd.DataFrame): Output of `fetch_tefas_data()` (General Information tab)
* `price_col` (str): Price column (default `"Fiyat"`)
* `fund_code_col` (str): Fund code column (default `"Fon Kodu"`)
* `fund_title_col` (str): Fund name column (default `"Fon Adı"`)
* `date_col` (str): Date column (default `"Tarih"`)
* `freq` (str): Return frequency. Supported abbreviations:
  * `"D"` (daily), `"B"` (business day), `"W"` (weekly), `"M"` (monthly), `"Q"` (quarterly), `"A"`/`"Y"` (annual / yearly)
* `risk_free_annual` (float): Annual risk-free rate (e.g., `0.10` = %10)
* `periods_per_year` (int | None): Number of periods per year; automatically inferred from frequency if left empty.
* `method` (str): "simple" or "log" (default `"simple"`)
* `drop_empty` (bool): Excludes funds with invalid/missing data (default `True`)
* `lang` (str): "tr" or "en" (default `"tr"`)

Returns:

* `pandas.DataFrame`

## Example

```python
from tefasfon import fetch_tefas_data, analyze_funds

df = fetch_tefas_data(
    fund_type_code=0,
    tab_code=0,
    start_date="01.09.2025",
    end_date="30.09.2025",
    lang="en"
)

# Business-day frequency + log returns + 10% risk-free rate
metrics = analyze_funds(
    df,
    freq="B",
    method="log",
    risk_free_annual=0.10,
    lang="en"
)
```

## Notes

* The library depends on data from the [TEFAS](https://www.tefas.gov.tr/TarihselVeriler.aspx) official website. In case of any changes or maintenance, data fetching may not be possible. Please check the data status and availability on TEFAS.
* Selenium and ChromeDriver are used. Google Chrome must be installed and up-to-date on your system.
* I welcome your feedback to improve and develop the library. You can contribute to the GitHub repository: [GitHub Repo](https://github.com/urazakgul/tefasfon)
* For any issues or suggestions, please open a new topic in the "Issue" section of the GitHub repository: [GitHub Issues](https://github.com/urazakgul/tefasfon/issues)

## Release Notes

### v0.4.0 - 18/10/2025

* Added the `analyze_funds` function.
* The minimized browser window is no longer displayed.

### v0.3.0 - 15/10/2025

* Added exact-match filtering on "Fund Code" via the `fund_codes` parameter.
* Added substring filtering on "Fund Title" via the `fund_title_contains` parameter.

### v0.2.0 - 05/09/2025

* Safe return when no data.
* Suppressed WebDriver/TFLite logs.
* Added per-date progress panels.
* Localized dropdown error message.

### v0.1.0 - 20/07/2025

* First release published.

## License

This project is licensed under the MIT License.