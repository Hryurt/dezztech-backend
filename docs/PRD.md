# DEZZTECH

### Devlet Teşvik ve Destek Başvuru Otomasyon Platformu

**Product Requirements Document**

| | |
|---|---|
| **Versiyon** | 1.1 |
| **Tarih** | Mart 2026 |
| **Durum** | Taslak |
| **Sınıflandırma** | Gizli |

---

## İçindekiler

1. [Genel Bakış](#1-genel-bakış)
2. [Temel Kavramlar ve Varlıklar](#2-temel-kavramlar-ve-varlıklar)
3. [Kullanıcı Rolleri ve Yetki Matrisi](#3-kullanıcı-rolleri-ve-yetki-matrisi)
4. [Abonelik Modeli](#4-abonelik-modeli)
5. [Fonksiyonel Gereksinimler](#5-fonksiyonel-gereksinimler)
6. [Veri Modeli — Teşvik Alanları](#6-veri-modeli--teşvik-alanları)
7. [Veri Modeli — Destek Alanları](#7-veri-modeli--destek-alanları)
8. [Veri Modeli — Firma Alanları](#8-veri-modeli--firma-alanları)
9. [Veri Modeli — Ürün Alanları](#9-veri-modeli--ürün-alanları)
10. [Dezzcovery Statik Soru Seti](#10-dezzcovery-statik-soru-seti)
11. [Bildirim Sistemi](#11-bildirim-sistemi)
12. [Dashboard](#12-dashboard)
13. [Fonksiyonel Olmayan Gereksinimler](#13-fonksiyonel-olmayan-gereksinimler)
14. [MVP Kapsamı ve Yol Haritası](#14-mvp-kapsamı-ve-yol-haritası)
15. [Açık Kalemler (Bekleyen Kararlar)](#15-açık-kalemler-bekleyen-kararlar)

---

## 1. Genel Bakış

### 1.1 Ürün Vizyonu

Dezztech, Türkiye'de devlet teşvik ve desteklerine başvuru sürecini baştan sona otomatize eden bir SaaS platformdur. Platform, firmaların kendilerine en uygun destekleri keşfetmelerini, başvurularını uçtan uca tamamlamalarını, yapay zekâ ve insan desteğiyle başvurularını kontrol ettirmelerini ve tüm süreci tek bir yerden yönetmelerini sağlar.

Aynı zamanda destek danışmanları (Admin kullanıcılar) platform üzerinden kendi desteklerini oluşturabilir, danışanlarının başvurularını görüntüleyebilir ve review süreci yürütebilir.

### 1.2 Kapsam

Bu doküman Dezztech platformunun MVP (Minimum Viable Product) aşamasını tanımlar. Aşağıdaki özellikler MVP kapsamı dışındadır ve sonraki sürümlerde ele alınacaktır:

- Raporlama modülü (tüm kullanıcı tipleri için)
- Dezzviser (başvuru sırasında stratejik öneri yapay zekâsı)
- Devlete otomatik başvuru iletimi ve süreç takibi

### 1.3 Hedef Kitle

- Türkiye'de devlet teşviklerinden yararlanmak isteyen firmalar ve girişimciler
- Destek danışmanları ve danışmanlık firmaları
- Teşvik ekosistemini yöneten kurum yetkilileri

---

## 2. Temel Kavramlar ve Varlıklar

Sistemdeki temel yapı taşları ve aralarındaki ilişkiler aşağıda tanımlanmıştır.

| Kavram | Tanım | İlişkiler |
|---|---|---|
| **Teşvik** | Devlet veya bir kurumun ihracatı artırmak, firmaları uluslararası pazarlarda güçlendirmek ve belirli sektörleri özendirmek amacıyla oluşturduğu üst çerçeve programıdır. | 1 Teşvik → N Destek |
| **Destek** | Teşvik programının altında yer alan, firmanın fiilen yararlandığı somut ve ölçülebilir kalemdir (kira, fuar, reklam, personel vb.). | N Destek → 1 Teşvik |
| **Firma** | Kullanıcının sisteme kayıt ettiği resmi şirkete karşılık gelen varlıktır. | 1 Firma → N Ürün, N Kullanıcı |
| **Ürün** | Firmanın ürettiği ürün, hizmet veya uygulamadır. Destek başvurularında kullanılabilir. | N Ürün → 1 Firma |
| **Kullanıcı** | Sisteme kayıtlı, destek başvurusu yapabilen ve yönetebilen kişidir. | 1 Kullanıcı → N Firma (farklı rollerle) |
| **Başvuru** | Bir firma ve opsiyonel olarak bir ürün ile yapılan destek başvurusudur. | 1 Başvuru → 1 Firma + 1 Destek + 0..1 Ürün |
| **Admin** | Destek oluşturabilen, danışman olarak atandığı firmaların başvurularını görüntüleyen kullanıcıdır. | N Firma (danışman rolüyle) |
| **Süper Admin** | Sistemin en üst düzey yöneticisi. Onay, red, review ve tüm veri görüntüleme yetkisine sahiptir. | Tüm veriye erişim |

### 2.1 Varlık İlişki Diyagramı

```
Teşvik (1) → (N) Destek → (N) Başvuru ← Firma (1) + Ürün (0..1)
Kullanıcı (1) ↔ (N) Firma [Rol bazlı ilişki: Owner, Firma Admin, Üye, Danışman]
```

**Not:** Bir kullanıcı farklı firmalarda farklı rollere sahip olabilir. Firma bazlı izin yapısı o firmanın tüm varlıklarına (ürünler, başvurular) geçerlidir.

---

## 3. Kullanıcı Rolleri ve Yetki Matrisi

### 3.1 Sistem Rolleri

| Rol | Tanım | Kapsam |
|---|---|---|
| **Süper Admin** | Sistemin en üst düzey yöneticisi. Tüm verilere erişim, teşvik/destek onayı, human review yetkisi. | Sistem geneli |
| **Admin** | Destek danışmanı. Teşvik/destek oluşturur, danışman olarak atandığı firmaları görüntüler. | Sistem + Atanmış firmalar |
| **Kullanıcı** | Standart kullanıcı. Firma oluşturur, başvuru yapar, ürün yönetir. | Kendi firmaları |

### 3.2 Firma İçi Roller

Her kullanıcı-firma ilişkisi bir rol içerir. İzinler firma bazlıdır ve o firmanın tüm varlıklarına (ürünler, başvurular) geçerlidir.

| Firma Rolü | Firma Yönetimi | Ürün Yönetimi | Başvuru Yönetimi | Kullanıcı Davet | Görüntüleme |
|---|---|---|---|---|---|
| **Owner** | Tam yetki | Tam yetki | Tam yetki | Evet (tüm roller) | Tam |
| **Firma Admin** | Düzenleme | Tam yetki | Tam yetki | Evet (tüm roller) | Tam |
| **Üye** | Hayır | Hayır | Oluşturma/Düzenleme | Hayır | Tam |
| **Danışman** | Hayır | Hayır | Hayır | Hayır | Sadece görüntüleme |

**Not:** Danışman rolü yalnızca Admin sistem rolüne sahip kullanıcılara verilebilir. Danışman firmada herhangi bir değişiklik yapamaz, yalnızca görüntüleme ve başvuru review hakkına sahiptir.

---

## 4. Abonelik Modeli

### 4.1 Paketler

Abonelik kullanıcı bazlıdır. Limitler hem kullanıcı hem firma düzeyinde uygulanır. Ödeme aylık veya yıllık yapılabilir. Ödeme altyapısı: iyzico.

| Özellik | Freemium | Basic | Pro | Premium |
|---|---|---|---|---|
| Dezzcovery | ✓ | ✓ | ✓ | ✓ |
| Dezzviewer (AI Review) | ✗ | ✗ | ✓ | ✓ |
| Human Review | ✗ | ✗ | ✗ | ✓ |
| Başvuru Yapma | ✗ | ✓ | ✓ | ✓ |
| Firma Oluşturma | ✗ | ✓ | ✓ | ✓ |
| Maks. Firma Sayısı | - | 1 | 2 | 2 |
| Firma Başına Maks. Ürün | - | 3 | 3 | 3 |
| Firma Başına Maks. Kullanıcı | - | 3 | 3 | 3 |
| Okuma Modu | Tam | Tam | Tam | Tam |

Freemium kullanıcı yalnızca Dezzcovery'den yararlanabilir ve sistemi okuma modunda kullanabilir. Başvuru yapamaz, firma ve ürün oluşturamaz.

### 4.2 Ek Hak Satın Alımı (À La Carte)

Kullanıcılar paket limitlerinin üzerine ek haklar satın alabilir. Ek haklar tek seferlik değil, aylık abonelik tutarına eklenir.

- Ek firma hakkı (kullanıcı bazlı)
- Ek ürün hakkı (firma bazlı)
- Ek kullanıcı hakkı (firma bazlı)

---

## 5. Fonksiyonel Gereksinimler

### 5.1 Kimlik Doğrulama ve Hesap Yönetimi

#### 5.1.1 Kayıt

1. Kullanıcı yalnızca iş e-postası ile kayıt olabilir (genel e-posta sağlayıcıları kabul edilmez).
2. Kayıt sonrası OTP (tek kullanımlık şifre) ile e-posta doğrulaması yapılır.
3. Google ve Microsoft Outlook ile sosyal giriş (OAuth 2.0) desteklenir. Sosyal girişte de iş e-postası kuralı geçerlidir.
4. Kayıt sırasında alınacak alanlar ayrıca belirlenecektir.

#### 5.1.2 Giriş

1. E-posta ve parola ile giriş.
2. Google ve Outlook ile giriş.

#### 5.1.3 Parola Yönetimi

1. Kullanıcı mevcut şifresini değiştirebilir.
2. Şifremi Unuttum akışı: e-postaya gönderilen link ile şifre sıfırlama.

#### 5.1.4 Profil Yönetimi

1. Kullanıcı profil bilgilerini görüntüleyebilir ve güncelleyebilir.
2. E-posta adresi güncellenebilir (yeniden doğrulama gerekir).

### 5.2 Firma Yönetimi

1. Kullanıcı yeni firma oluşturabilir. Firma veri alanları için bkz. [Bölüm 8](#8-veri-modeli--firma-alanları).
2. Kullanıcı oluşturduğu veya davet edildiği tüm firmaları listeleyebilir.
3. Yetki dahilinde firma bilgilerini güncelleyebilir.
4. Firmayı pasife alabilir, tekrar aktif edebilir veya tamamen silebilir (yalnızca Owner).
5. Firma Owner veya Firma Admin, firmaya yeni kullanıcı davet edebilir. Davet sırasında rol seçilir.
6. Danışman rolündeki kullanıcı başka kullanıcı davet edemez.
7. Firma oluşturma ve üyelik limitleri abonelik paketine göre uygulanır.

### 5.3 Ürün Yönetimi

1. Yetkili kullanıcı firma adına ürün oluşturabilir. Ürün veri alanları için bkz. [Bölüm 9](#9-veri-modeli--ürün-alanları).
2. Ürünler firma bazlıdır; bir ürün yalnızca bir firmaya aittir.
3. Ürün güncellenebilir, pasife alınabilir, aktif edilebilir veya silinebilir.
4. Ürün sayısı abonelik paketine ve ek haklara göre sınırlandırılır.

### 5.4 Teşvik ve Destek Yönetimi

#### 5.4.1 Teşvik Yönetimi

- Admin yeni teşvik oluşturabilir. Teşvik veri alanları için bkz. [Bölüm 6](#6-veri-modeli--teşvik-alanları).
- Oluşturulan teşvikler Süper Admin onayına gider. Onaylanmadan aktif olmaz.
- Süper Admin teşviki onaylayabilir, reddedebilir veya yorum yazabilir.
- Kullanıcılar aktif teşvikleri listeleyebilir ve detaylarını görüntüleyebilir.

#### 5.4.2 Destek Oluşturma (Admin)

Destek oluşturma çok aşamalı bir süreçtir. Her destek aşağıdaki beş bölümden oluşur:

| Bölüm | Açıklama |
|---|---|
| **1. Temel Bilgiler** | Desteğin adı, açıklaması, bağlı olduğu teşvik, hedef sektör, ürün gereksinimi (evet/hayır) ve diğer genel bilgiler. Detaylar için bkz. [Bölüm 7](#7-veri-modeli--destek-alanları). |
| **2. Ön Koşul Uygunluk Cevapları** | Sistemde tanımlı statik ön koşul soru setine karşılık Admin'in belirlediği kabul kriterleri. Örneğin: şirket yılı ≥ 2 seçilirse, 1 yıllık firmalar otomatik elenir. |
| **3. Form Şablonu** | Başvuru formu yapısı. Sayfa → Grup → Alan hiyerarşisiyle oluşturulur. Detaylar bölüm 5.4.3'te. |
| **4. İnceleme Notları** | Review yapacak kişinin (AI veya Süper Admin) dikkat etmesi gereken konuları içeren serbest metin alanı. |
| **5. Limitler** | Desteğe özgü birden fazla limit tanımı (oran, tutar, süre vb.). |

Oluşturulan destek Süper Admin onay akışına girer. Onaylanmadan aktif olmaz.

Ön koşul cevapları destek bilgisi olarak kullanıcılara görüntülenebilir.

#### 5.4.3 Form Builder (Destek Formu Şablonu)

Her destek farklı bir başvuru mekanığı gerektirdiğinden, form builder yapısıyla özelleştirilebilir form şablonları oluşturulur.

**Form Hiyerarşisi:**

- **Sayfa (Page):** Formun en üst düzey bölümü. Birden fazla sayfa olabilir.
- **Grup (Group):** Sayfa içindeki tematik gruplandırma. Her sayfada birden fazla grup olabilir.
- **Alan (Field):** Grubun içindeki veri giriş alanı. Her grupta birden fazla alan olabilir.

**Alan Türleri:**

| Alan Türü | Açıklama | Başvuruda Davranış |
|---|---|---|
| **Firma Bazlı Alan** | Firma profilinden çekilen alan (firma adı, vergi no, NACE kodu vb.) | Firma seçildiğinde otomatik dolar, kullanıcı değiştiremez. |
| **Ürün Bazlı Alan** | Ürün profilinden çekilen alan | Ürün seçildiğinde otomatik dolar, kullanıcı değiştiremez. |
| **Mevcut Alan** | Başka bir destek şablonunda daha önce oluşturulmuş alanın yeniden kullanımı | Manuel doldurulur. |
| **Yeni Alan** | Sıfırdan oluşturulan özel alan | Manuel doldurulur. |

### 5.5 Başvuru Yönetimi

#### 5.5.1 Başvuru Oluşturma

1. Kullanıcı bir destek seçer.
2. Firma seçimi yapar (zorunlu).
3. Destek ürün gerektiriyorsa ürün seçimi yapar.
4. Sistem, desteğin form şablonunu yükler. Firma bazlı ve ürün bazlı alanlar otomatik doldurulur.
5. Kullanıcı kalan alanları manuel doldurur.
6. Başvuru taslak olarak kaydedilir.

#### 5.5.2 Başvuru Durumları (Status Akışı)

| Durum | Açıklama | Geçiş |
|---|---|---|
| **Draft (Taslak)** | Başvuru henüz tamamlanmamış veya onaya gönderilmemiş. | Kullanıcı düzenleyebilir. Review'e gönderebilir. |
| **In Review** | Başvuru AI veya Human review sürecinde. | Kullanıcı bekler. |
| **Reviewed** | Review tamamlanmış, feedback dönmüş. | Kullanıcı feedback'e göre düzenleyip tekrar gönderebilir. |
| **Approved** | Süper Admin tarafından onaylandı. | Gelecekte: devlete otomatik iletim. |
| **Rejected** | Süper Admin tarafından reddedildi. | Kullanıcıya red gerekçesi iletilir. |

#### 5.5.3 Başvuru Review Süreci

**AI Review (Dezzviewer) — Pro ve Premium:**

- Tamamlanmış başvuruyu otomatik denetler.
- Belge-form tutarlılığını kontrol eder.
- Feedback/yorum listesi döner.
- Kullanıcı feedback'e göre düzeltip tekrar gönderebilir.

**Human Review — Yalnızca Premium:**

- Kullanıcı başvurusunu Human Review'e gönderir.
- Süper Admin başvuruyu inceler.
- Feedback/yorum listesi döner.
- Kullanıcı feedback'e göre düzeltip tekrar gönderebilir.

#### 5.5.4 Başvuru Yönetimi

- Kullanıcı başvurularını listeleyebilir.
- Başvuru detayını görüntüleyebilir.
- Taslak başvuruları güncelleyebilir.
- Başvuruları silebilir.
- Başvuru durumunu takip edebilir.

### 5.6 Yapay Zekâ Modülleri

#### 5.6.1 Dezzcovery (Destek Keşif Motoru)

Tüm paketlerdeki kullanıcılar için kullanılabilir. Kullanıcının profiline en uygun destekleri keşfetmesini sağlar.

**Akış:**

1. Kullanıcı ilk girişte (veya tekrar başlatma seçeneğiyle) onboarding sürecine yönlendirilir.
2. Statik soru seti sorulur (her kullanıcıya aynı sorular). Soru seti detayları için bkz. [Bölüm 10](#10-dezzcovery-statik-soru-seti).
3. Yanıtlara göre destekler ön koşul kriterlerine göre elenir.
4. Kalan destekler ve kullanıcı yanıtları yapay zekâya verilir.
5. Yapay zekâ ek dinamik sorular türetir.
6. Kullanıcı dinamik soruları yanıtlar.
7. Yapay zekâ uygun destekleri sıralar ve sonuç kaydedilir.

Kullanıcı Dezzcovery'yi istediği zaman sıfırdan tekrar çalıştırabilir.

**Teknik:** agno framework'ü ile implemente edilecektir. Başlangıçta basit tutulup zamanla güçlendirilecektir.

#### 5.6.2 Dezzviewer (Başvuru Denetim Motoru)

Pro ve Premium paket kullanıcıları için kullanılabilir.

- Tamamlanmış başvuruyu otomatik denetler.
- Belge-form tutarlılığını kontrol eder.
- Feedback/yorum listesi döner.
- Teknik: agno framework'ü ile implemente edilecektir.

#### 5.6.3 Dezzviser (Stratejik Öneri Motoru) — MVP Sonrası

Başvuru sırasında formdaki bilgileri kontrol ederek stratejik öneriler sunar. MVP kapsamı dışındadır.

### 5.7 Admin Senaryoları

1. Danışman olarak atandığı firmaları listeleyebilir.
2. Bu firmaların ürünlerini ve başvurularını görüntüleyebilir (salt okunur).
3. Teşvik ve destek oluşturabilir (Süper Admin onayı gerekir).
4. Kendi dashboard'unda rolü olduğu firmaların başvuru ve işlemlerini görüntüleyebilir.

### 5.8 Süper Admin Senaryoları

1. Tüm kullanıcıları, firmaları, ürünleri, başvuruları, teşvikleri ve destekleri görüntüleyebilir.
2. Tüm varlıkları aktife/pasife alabilir.
3. Kullanıcıları, başvuruları ve teşvikleri güncelleyebilir ve silebilir.
4. Yeni oluşturulan teşvik ve destekleri inceleyebilir, onaylayabilir, reddedebilir ve yorum yazabilir.
5. Human Review taleplerini yönetir: başvuruları inceler, feedback/yorum listesi döner.
6. Sistemdeki abonelikleri görüntüleyebilir.

---

## 6. Veri Modeli — Teşvik Alanları

Bu bölüm, teşvik programlarının kart ve detay sayfalarında gösterilecek/girilecek veri alanlarını tanımlar.

### 6.1 Teşvik Kartı (Liste Görünümü)

Katalog sayfasında her teşvik programı için gösterilecek özet kart bilgileri:

| Alan | Açıklama |
|---|---|
| Program Adı | Hizmet Sektörleri Atılım Programı / Markalaşma Programı / Sürdürülebilirlik vb. |
| Kısa Açıklama | 1–2 cümlelik program özeti |
| Kapsam Sektörleri | Etiketler halinde (Bilişim, Sağlık Turizmi, Eğitim...) |
| Destek Oranı | %50 / %75 gibi ana oran bilgisi |
| Destek Süresi | 5 yıl / Proje süresi gibi genel süre |
| Program Durumu | Aktif / Başvuruya Açık rozeti |
| Destek Sayısı | Bu program altında kaç destek unsuru var |
| Başvur Butonu | Detay sayfasına yönlendirme CTA |

**Davranış kuralları:**
- Kartlar sektörel filtre ve arama ile daraltılabilir olmalı.
- Kullanıcının sektörüne uygun teşvik kartları önde gösterilmeli (Dezzcovery entegrasyonu).

### 6.2 Teşvik Detay Sayfası

Kullanıcı bir teşvik kartına tıkladığında görüntülenen tam bilgi sayfası:

| Alan | Açıklama |
|---|---|
| Program Adı | Tam program adı |
| Dayanak Mevzuat | İlgili kanun/karar/genelge referansı |
| Açıklama | Programın amacı ve kapsamının detaylı anlatımı |
| Kapsam Sektörleri | Tam sektör listesi (işaretli/etiketli) |
| Alt Programlar | Marka / TURQUALITY / E-TURQUALITY (varsa) |
| Genel Destek Oranı | % oranı + hedef ülkeler için ilave oran bilgisi |
| Genel Destek Süresi | Yıl bazında süre bilgisi |
| Yıllık Üst Limit | TL bazında yıllık üst limit |
| Hedef Ülkeler Listesi | İlave destek oranı uygulanan ülkeler |
| Ön Onay Gerekliliği | Genel bilgi — hangi destekler ön onay gerektirir |
| Başvuru Süresi Kuralı | Faaliyetten itibaren geçerli süre kuralı açıklaması |
| İzleme ve Değerlendirme | Yıllık izleme süreci açıklaması |
| Destek Unsurları Listesi | Bu programa ait tüm desteklerin listesi (kart olarak, Bölüm 7'ye yönlendirir) |

**Davranış kuralları:**
- Destek unsurları alt bölümünde her destek için mini kart gösterilir.
- Kullanıcının firmasına göre uygun/uyumsuz destekler renk kodlu gösterilir.

### 6.3 Markalaşma Programı Özel Gösterimleri

Markalaşma Programı kapsamındaki teşvik detay sayfasında ek olarak gösterilecek bilgiler:

| Alan | Açıklama |
|---|---|
| Alt Program Tipi | Marka / TURQUALITY / E-TURQUALITY rozeti |
| Hedef Pazar Gerekliliği | Hedef pazar ekleme zorunluluğu açıklaması |
| Yıllık Toplam Limit | Marka: 250M TL, TURQUALITY: 500M TL |
| Marka Bazlı Destek Süresi | Marka: 4 yıl, TURQUALITY: hedef pazar bazında 5 yıl |
| SİP Zorunluluğu | Stratejik İş Planı sunulmadan ödeme yapılmaz uyarısı |
| Performans Değerlendirmesi | Yıllık performans puanı ve destek oranı değişim tablosu |
| Harcama Yetkilisi | Organik bağlı şirketlerin harcama yapabilmesi açıklaması |

---

## 7. Veri Modeli — Destek Alanları

Bu bölüm, destek unsurlarının kart ve detay sayfalarında gösterilecek/girilecek veri alanlarını tanımlar.

### 7.1 Destek Kartı (Liste/Grid Görünümü)

Teşvik detay sayfasında veya destek katalogu sayfasında gösterilecek destek özet kartı:

| Alan | Açıklama |
|---|---|
| Destek Adı | Örnek: Reklam, Tanıtım ve Pazarlama Desteği |
| Kısa Açıklama | 1 cümlelik destek özeti |
| Destek Oranı (%) | %50 veya sektöre göre değişken oran |
| Yıllık Limit | 25.000.000 TL/yıl gibi limit bilgisi |
| Geçerli Sektörler | Etiket şeklinde (Tüm Sektörler veya spesifik) |
| Ön Onay Durumu | Gerekli / Gerekli Değil rozeti |
| Destek Süresi | 5 yıl / Sınırlaması yok gibi bilgi |
| Durum Rozeti | Sizin İçin Uygun / Kontrol Edin / Uyumsuz |
| Başvuru Başlat Butonu | Destek başvuru formuna yönlendirme |

**Davranış kuralları:**
- Ortak destekler ve Sektörel destekler sekmeler veya kategori filtresi ile ayrılır.
- Kullanıcının sektörü ile uyumsuz destekler soluk/pasif görünür.

### 7.2 Destek Detay Sayfası — Standart Bilgi Alanları (Tüm Destekler İçin Ortak)

| Alan | Açıklama |
|---|---|
| Destek Adı | Tam destek adı |
| Bağlı Program | Hizmet Sektörleri Atılım / Markalaşma / Sürdürülebilirlik |
| Destek Açıklaması | Neyin desteklendiği, amacı, kapsamının detaylı anlatımı |
| Destek Oranı | % bilgisi + hedef ülke ilavesi açıklaması |
| Yıllık Üst Limit (TL) | Takvim yılı bazında limit |
| Toplam / Proje Limiti | Varsa toplam proje bazlı limit |
| Destek Süresi | Kaç yıl, başlangıç tarihi hesaplama kuralı |
| Geçerli Sektör(ler) | Hangi sektörler faydalanabilir — detaylı liste |
| Ön Onay Gerekliliği | Gerekiyorsa ne zaman, kaç gün/ay önce yapılmalı |
| Başvuru Koşulları | Madde madde listelenmiş özel koşullar |
| Desteklenen Gider Kalemleri | Hangi harcamalar destek kapsamında |
| Desteklenmeyen Giderler | Kapsam dışı harcamalar (uyarı olarak) |
| Başvuru Süresi | Faaliyet/ödeme tarihinden itibaren geçerli süre |
| Gerekli Belgeler | Belge listesi + şablon indirme linkleri |
| İlgili EK/Form Referansı | EK-4, EK-14, EK-YBF gibi mevzuat referansları |
| Başvuru Başlat Butonu | Form wizard başlatma CTA |

### 7.3 Destek Detay Sayfası — Sektöre Göre Değişen Bilgiler

Aşağıdaki sektörlerde destek detay sayfasında ek olarak gösterilecek bilgiler/koşullar:

| Sektör | Ek Gösterilecek Bilgi / Koşul | Etkilenen Destekler |
|---|---|---|
| **Bilişim** | Dijital ürün türü (Yazılım/Oyun/Mobil Uygulama) seçimi gerekliliği, Türkçe sürüm varsa %50 hesaplama uyarısı | Dijital Ürün Tanıtım, Platform Komisyon, Barındırma, Yazılım Lisans |
| **Sağlık Turizmi** | Sağlık kuruluşu / Aracı kuruluşu ayrımı, UST Yetki Belgesi gerekliliği, Komplikasyon sigortası Türkiye'de olmalı uyarısı | Uluslararası Sağlık Turisti Ulaşım, Komplikasyon Sigortası, Yabancı Dil Eğitimi |
| **Eğitim** | Yükseköğretim kurumu gerekliliği, uluslararası öğrenci ofisi istihdamı koşulu | Uluslararası Sıralama, Acente Komisyon, İş Gücü Geliştirme |
| **Film** | Film yapımcısı/dağıtımcısı gerekliliği, yurt dışı satış şartı, her dilde 1 kez kuralı | Dublaj ve Alt Yazı, Tescil/Koruma, Reklam/Tanıtım |
| **Teknik Müşavirlik** | İhale ile proje, sözleşme bedeli %10 hesaplama, proje bazlı limit | Teknik Müşavirlik Proje, Mesleki Sorumluluk Sigortası |
| **Lojistik** | Ulaştırma Bakanlığı izni, taşıma modları, aktarma merkezi birim sayılır | Birim (Aktarma Merkezi), Rapor ve Veri Tabanı |
| **Fuarcılık/Kongre** | TOBB/TÜRSAB belgesi, organizatör yetkisi, yurt içi etkinlik özel koşulları | Etkinlik Organizasyon, Etkinlik Katılım |
| **Danışmanlık** | Danışmanlık türü seçimi, %51 gelir oranı şartı | Rapor ve Veri Tabanı (sadece VT üyeliği) |
| **Dijital Aracılık** | Yabancı dil platform zorunluluğu, aracılık edilen sektörler | Barındırma |
| **Spor Turizmi** | A Grubu seyahat acentesi veya konaklama tesisi olmalı | Acente Komisyon |
| **Uygunluk Değerlendirme** | Faaliyet türü seçimi, akreditasyon belgesi | Belgelendirme |
| **Finansal Teknolojiler** | TCMB yetkisi zorunlu | Ortak desteklerden faydalanır |

---

## 8. Veri Modeli — Firma Alanları

Bu bölüm, firma profilinde gösterilecek/girilecek tüm veri alanlarını tanımlar.

### 8.1 Firma Özet Kartı (Dashboard / Sidebar)

Kullanıcının dashboard ekranında veya yan panelde gördüğü firma özet bilgisi:

| Alan | Örnek Değer |
|---|---|
| Firma Unvanı | XYZ Teknoloji A.Ş. |
| Sektör | Bilişim – Yapay Zeka |
| Kuruluş Tarihi | 2019 |
| Personel Sayısı | 45 |
| HİB Üyelik Durumu | Aktif / Pasif rozeti |
| SGK/Vergi Borcu | Yok (yeşil) / Var (kırmızı) rozeti |
| Profil Tamamlanma | % ilerleme çubuğu |
| Uygun Destek Sayısı | 12 Destek Uygun (Dezzcovery çıktısı) |
| Profili Düzenle Butonu | Detay sayfasına yönlendirme |

**Davranış kuralları:**
- Profil tamamlanma oranı eksik alanlara tıklanarak tamamlanabilir olmalı.
- SGK/Vergi borcu varsa başvuru engelleneceğine dair uyarı gösterilmeli.

### 8.2 Firma Bilgi Giriş Alanları — Ortak (Tüm Sektörler)

Kaynak: EK-YBF (Yararlanıcı Bilgi Formu). Tüm sektörler için zorunlu alanlar:

| Alan Adı | Giriş Tipi | Açıklama / Uyarı |
|---|---|---|
| MERSIS No | Metin Kutusu | MERSIS ile uyumsuzluk halinde başvuru işleme alınmaz |
| Yararlanıcı / Firma Unvanı | Metin Kutusu | Ticaret sicilindeki resmi unvan |
| Vergi No | Sayısal Giriş (10/11 hane) | TC Kimlik No veya Vergi Kimlik No |
| Vergi Dairesi | Metin / Arama | Otomatik tamamlama ile |
| Kuruluş Tarihi | Tarih Seçici | Markalaşma için min 3 yıl kontrolü yapılır |
| Personel Sayısı | Sayısal Giriş | KOBİ sınıfı tespitinde kullanılır |
| IBAN No (TL) | Metin (TR formatında) | Destek ödemelerinin yapılacağı hesap |
| KEP Adresi | Metin | Resmi KEP adresi (gönderim için zorunlu) |
| E-Posta Adresi | E-posta | Bildirimler için |
| İnternet Adresi (Web) | URL | Firma web sitesi |
| Telefon No | Telefon | İletişim için |
| Merkez Adresi | Metin Alanı (çoklu satır) | Resmi merkez adresi |
| Üyesi Olunan İhracatçı Birlikleri | Çoklu Seçim / Metin | HİB üyeliği zorunlu (bazı istisnalar hariç) |
| HİB Üye No | Metin | Hizmet İhracatçıları Birliği üye numarası |
| İrtibat Kurulacak Kişi | Metin | Ad Soyad |
| İrtibat İletişim Bilgileri | Telefon + E-posta | İrtibat kişiye ait |
| NACE Kodu (4'lü) | Arama / Seçim | Ticaret sicilindeki faaliyet kodları |
| NACE Adı | Otomatik | Seçilen koda göre otomatik gelir |
| Faaliyet Gösterilen Sektör | Çoklu Seçim (Checkbox) | Bilişim, Danışmanlık, Eğitim, Sağlık Turizmi vb. |
| Marka (Varsa) | Metin + Tekrarlanabilir | Tescilli marka adı, birden fazla eklenebilir |
| SGK Borcu Durumu | Evet / Hayır | Varsa destek başvurusu engellenebilir |
| Vergi Borcu Durumu | Evet / Hayır | Varsa destek başvurusu engellenebilir |
| Hizmet İhracatı (Son Yıl, USD) | Sayısal | İzleme ve değerlendirme limiti için |
| Yurt Dışı Kaynaklı Gelir (Son Yıl, USD) | Sayısal | İzleme limiti: ihracat+gelirin 1/3'ü |

### 8.3 Firma Bilgi Giriş Alanları — Sektöre Özel

Kullanıcı sektör seçimini yaptıktan sonra dinamik olarak gösterilecek ek alanlar:

#### Bilişim Sektörü

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Bilişim Alt Sektörü | Tekli Seçim | Blok Zincir / Yapay Zeka / Siber Güvenlik / Büyük Veri / Akıllı Şehir / Ticari Yazılım / Gömülü Yazılım / Dijital Oyun / Mobil Uygulama / İletişim / Bilişim Hizmetleri |

#### Danışmanlık Sektörü

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Danışmanlık Türü | Tekli Seçim | Yönetim Danışmanlığı / Çevresel Sürdürülebilirlik / Patent ve Marka |
| Son 2 Yıl Gelir Oranı | Sayısal (%) | İlgili hizmetten elde edilen gelirin toplama oranı – min %51 |

#### Dijital Aracılık Sektörü

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Dijital Aracılık Platformu URL | URL | Yabancı dilde, uluslararası tüketiciye yönelik platform adresi |
| Aracılık Edilen Sektörler | Çoklu Seçim | Hizmet sektörlerinden hangileri |
| Son 2 Yıl Gelir Oranı | Sayısal (%) | Dijital aracılık gelirinin toplama oranı – min %51 |

#### Eğitim Sektörü

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Kurum Türü | Tekli Seçim | Özel Öğretim Kurumu / Üniversite / YTE / Vakıf MYO |
| YÖK Onay Bilgisi | Belge Yükleme | 2809 sayılı Kanun kapsamında onay |

#### Sağlık Turizmi Sektörü

Sağlık Kuruluşu (EK-E) veya Aracı Kuruluş (EK-F) seçimi yapılır, buna göre farklı alanlar gösterilir:

| Alan | Giriş Tipi | Gösterildiği Profil |
|---|---|---|
| Kuruluş Tipi Seçimi | Tekli Seçim | Her İkisi — Sağlık Kuruluşu / Sağlık Turizmi Aracı Kuruluşu |
| Sağlık Kuruluşu Türü | Tekli Seçim | Kuruluş — Özel / Kamu / Üniversite Hastanesi |
| Tıbbi Bölümler | Çoklu Seçim | Kuruluş — Medikal, Termal, Yaşlı/Engelli Bakım |
| Uzman Hekim Sayısı | Sayısal | Kuruluş |
| Yatak Sayısı | Sayısal | Kuruluş |
| UL. Sağlık Turizmi Birimi Personel Sayısı | Sayısal | Kuruluş |
| UST Yetki Belgesi | Belge Yükleme | Aracı Kuruluş |
| Anlaşmalı Sağlık Kuruluşları | Liste (Ad + Adres) | Aracı Kuruluş — min 3 adet tanıtım için |
| Son 3 Yıl Sağlık Turisti Sayısı | Sayısal (yıllık x3) | Her İkisi |
| En Fazla Hasta Gelen İlk 3 Ülke | Ülke Seçimi (x3) | Her İkisi |

#### Diğer Sektörler (Özet)

| Sektör | Ek Alan | Giriş Tipi |
|---|---|---|
| Finansal Teknolojiler | TCMB Yetki Belgesi | Belge Yükleme |
| Fuarcılık | TOBB Yetki Belgesi No | Metin |
| Kongre Turizmi | TÜRSAB Üyelik No | Metin |
| Kültürel ve Kreatif | Alt Sektör Seçimi (Film/Reklamcılık/Yayıncılık/Dijital Sanat/Çekim Sonrası) | Tekli Seçim |
| Lojistik ve Taşımacılık | Ulaştırma Bakanlığı İzin/Ruhsat + Taşıma Modları | Belge + Çoklu Seçim |
| Spor Turizmi | A Grubu Seyahat Acentesi Belgesi veya Konaklama Tesisi Belgesi | Belge Yükleme |
| Teknik Müşavirlik | Hizmet Türü (Mühendislik/Mimarlık) + Son 2 Yıl %51 Gelir Oranı | Seçim + Sayısal |
| Uygunluk Değerlendirme | Faaliyet Türü + Akreditasyon Belgesi + Son 2 Yıl %51 Gelir | Seçim + Belge + Sayısal |

### 8.4 Markalaşma Programı Ek Firma Bilgileri

Markalaşma Programı kapsamında firma profilinde ek olarak girilmesi gereken alanlar:

| Alan | Giriş Tipi | Koşul / Açıklama |
|---|---|---|
| Yurt İçi Marka Tescil Belgesi | Belge Yükleme | Yararlanıcı adına tescilli olmalı |
| Yurt Dışı Marka Tescil Belgesi | Belge Yükleme | Madrid Protokolü ülkelerinden en az birinde |
| Son 3 Yıl Hizmet İhracatı / Yurt Dışı Gelir | Sayısal (yıllık x3, USD) | Ortalama min 1.500.000 USD |
| Ana Yönetim Merkezi | Adres | Türkiye'de yerleşik olmalı |
| İhraca Hazır Ürün/Hizmet | Metin (beyan) | Yurt dışı yerleşiklere sunulabilecek |
| Hedef Pazarlar (Ülkeler) | Çoklu Seçim | TURQUALITY/E-TURQUALITY için zorunlu |
| Harcama Yetkilisi Şirket | Firma Kartı Ekleme | Organik bağ %51+ ortaklık |
| Gastronomi: Yurt İçi Lokanta Sayısı | Sayısal | Min 5 (sadece Gastronomi) |
| Gastronomi: Yurt Dışı Lokanta Sayısı | Sayısal | Min 1 (sadece Gastronomi) |
| Konaklama: Yurt Dışından Gelen Ziyaretçi Hasılatı | Sayısal (USD) | Min 4M USD veya 10+15 otel (sadece Konaklama) |

---

## 9. Veri Modeli — Ürün Alanları

Bu bölüm, ürün/hizmet tanımı için gösterilecek/girilecek tüm veri alanlarını tanımlar.

### 9.1 Ürün Özet Kartı (Ürünlerim Listesi)

Ürünlerim sayfasında her ürün/hizmet için gösterilen özet kart:

| Alan | Örnek Değer |
|---|---|
| Ürün / Hizmet Adı | CyberShield Pro |
| Ürün Türü | Yazılım / Film / Eğitim Programı / Sağlık Hizmeti vb. |
| Bağlı Sektör | Bilişim / Film / Eğitim / Sağlık Turizmi rozeti |
| Bağlı Marka | Varsa tescilli marka adı |
| Hedef Pazarlar | Etiketler halinde (ABD, Almanya, BAE...) |
| Dil Desteği | EN, DE, AR gibi etiketler |
| Desteğe Konu Edilme Durumu | Aktif / Beklemede / Tamamlandı |
| Düzenle Butonu | Detay sayfasına yönlendirme |

**Davranış kuralları:**
- Ürün ekleme butonu ile yeni ürün/hizmet tanımlanabilir.
- Bir ürün birden fazla destek başvurusunda kullanılabilir.

### 9.2 Ürün Bilgi Giriş Alanları — Ortak

Tüm sektörler için her ürün/hizmet tanımında girilecek temel alanlar:

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Ürün / Hizmet Adı | Metin | Desteğe konu edilecek ürün veya hizmetin adı |
| Ürün Türü | Tekli Seçim (Sektöre Göre) | Yazılım, Dijital Oyun, Mobil Uygulama, Film, Eğitim Programı, Sağlık Hizmeti, Müşavirlik Projesi vb. |
| Sunulduğu Satış Kanalı / Platform | URL | Web sitesi, dijital platform, uygulama mağazası linki |
| Hedef Pazar / Ülkeler | Çoklu Seçim | Yurt dışı hedef pazarlar |
| Yabancı Dil Desteği | Çoklu Seçim | Ürünün sunulduğu diller |
| Bağlı Marka | Seçim (firma markalarından) | Tescilli marka bağlantısı |
| Ürün Açıklaması | Metin Alanı | Kısa tanıtım metni |

### 9.3 Ürün Bilgi Giriş Alanları — Sektöre Özel

#### Bilişim Sektörü

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Dijital Ürün Türü | Tekli Seçim | Yazılım / Mobil Uygulama / Dijital Oyun |
| Platform Hesap Bilgisi | URL + Metin | Dijital platformda kendi hesabıyla pazarlama (Platform Komisyon için) |
| Türkçe Sürüm Var mı? | Evet / Hayır | Varsa barındırma desteği %50 üzerinden hesaplanır |
| Yazılım Lisans Bilgisi | Seçim | Satın Alma / Kiralama (Yazılım Lisans desteği için) |
| Barındırma Sağlayıcı Bilgisi | Metin / URL | Sunucu ve barındırma detayları |

#### Film Sektörü (Kültürel ve Kreatif)

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Film Adı | Metin | Desteğe konu film |
| Film Türü | Tekli Seçim | Sinema Filmi / Belgesel / Dizi / Animasyon / Program Formatı |
| Yapım/Dağıtım Belgesi | Belge Yükleme | Film yapımcısı veya dağıtımcısı statüsü kanıtlayan belge |
| Dublaj / Alt Yazı Dili | Çoklu Seçim | Hedef diller (her dilde 1 kez desteklenir) |
| Yurt Dışı Satış Belgesi | Belge Yükleme | Filmin yurt dışına satıldığını kanıtlayan belge |

#### Sağlık Turizmi

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Tedavi Türü | Tekli Seçim | Medikal / Termal / Yaşlı-Engelli Bakım |
| Uluslararası Sağlık Turisti Bilgileri | Tablo (Tekrarlanabilir) | Ad, Pasaport No, Ülke, Türkiye Giriş Tarihi |
| Sağlık Hizmeti Bedeli | Sayısal | Ulaşım desteği hesaplamasında 1/3 kuralı için |
| Komplikasyon Sigortası Poliçesi | Belge Yükleme | Türkiye'deki tedavi dönemini kapsamalı |
| Sağlık Kuruluşuna Giriş Kaydı | Belge / Tarih | Giriş tarihinden itibaren 7 gün içinde olmalı |

#### Teknik Müşavirlik (Proje)

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Proje Adı | Metin | Yurt dışı teknik müşavirlik projesi |
| İşveren İdare Bilgisi | Metin | Projeyi açan kurum/kuruluş |
| Proje Ülkesi | Seçim | Projenin yürütüldüğü ülke |
| İhale Tarihi | Tarih | Ön onay ihale tarihinden 5 iş günü önce yapılmalı |
| Sözleşme Bedeli | Sayısal | EK-20 Proje Desteği Teknik Bilgi Formu ile uyumlu olmalı |
| Projedeki Ortaklık Oranı (%) | Sayısal | Konsorsiyum durumunda |
| Mesleki Sorumluluk Sigortası | Belge Yükleme | Yurt dışı projelere yönelik poliçe |

#### Eğitim Sektörü

| Alan | Giriş Tipi | Açıklama |
|---|---|---|
| Eğitim Programı Adı | Metin | Uluslararası öğrenciye yönelik program |
| Uluslararası Öğrenci Sayısı | Sayısal | Acente komisyon desteği için |
| Öğretim Yılı | Tarih Aralığı | Eylül – Ağustos dönemi (her öğrenci 1 kez) |

#### Diğer Sektörler

| Sektör | Ek Ürün Alanı | Açıklama |
|---|---|---|
| Spor Turizmi | Lisanslı Sporcu/Takım/Kafile Bilgisi | Getirilen sporcuların adı, spor dalı, lisans bilgisi |
| Lojistik | Aktarma Merkezi Bilgisi | Yurt dışında açılan aktarma merkezi adres ve belgeleri |
| Dijital Aracılık | Platform Bilgileri | Aracılık platformunun detayları ve erişim bilgileri |
| Gastronomi (Markalaşma) | Lokanta/Kafe Listesi + Menü İçeriği | Ad, adres, Türk mutfağı unsurları, menü belgesi |

### 9.4 Ürün Bazında Yüklenecek Belgeler

Ürün tanımına bağlı olarak yüklenebilecek belgeler (destek başvurusunda da kullanılır):

| Belge Türü | Yükleneceği Sektör/Durum | Format |
|---|---|---|
| Marka Tescil Belgesi (Yurt İçi) | Tescilli marka varsa – Tüm Sektörler | PDF |
| Marka Tescil Belgesi (Yurt Dışı) | Markalaşma Programı | PDF |
| Film Yapım/Dağıtım Belgesi | Film Sektörü | PDF |
| Film Yurt Dışı Satış Belgesi | Film – Dublaj Desteği için | PDF |
| UST Yetki Belgesi | Sağlık Turizmi Aracı Kuruluş | PDF |
| TCMB Yetki Belgesi | Finansal Teknolojiler | PDF |
| TOBB / TÜRSAB Yetki Belgesi | Fuarcılık / Kongre Turizmi | PDF |
| Ulaştırma Bakanlığı İzin/Ruhsat | Lojistik ve Taşımacılık | PDF |
| A Grubu Seyahat Acentesi Belgesi | Spor Turizmi | PDF |
| Konaklama Tesisi İşletme Belgesi | Spor Turizmi (konaklama tesisi) | PDF |
| Akreditasyon Belgesi | Uygunluk Değerlendirme | PDF |
| YÖK Onay Belgesi | Eğitim – Yükseköğretim | PDF |
| Komplikasyon Sigortası Poliçesi | Sağlık Turizmi | PDF |
| Mesleki Sorumluluk Sigortası Poliçesi | Teknik Müşavirlik | PDF |
| Yazılım Lisans Belgesi | Bilişim / Teknik Müşavirlik | PDF |
| Sözleşme (Proje/İhale) | Teknik Müşavirlik Proje Desteği | PDF |
| EK-20 Proje Desteği Teknik Bilgi Formu | Teknik Müşavirlik | PDF |

**Davranış kuralları:**
- Belgeler bir kez yüklendiğinde tüm ilgili destek başvurularında otomatik kullanılabilir.
- Süresi geçmiş belgeler için yenileme uyarısı gösterilmeli.

---

## 10. Dezzcovery Statik Soru Seti

Bu bölüm, Dezzcovery AI onboarding sürecinde her firmaya sorulan 30 sabit soruyu (Katman A) tanımlar. Her soru; tipi, seçenekleri ve zorunluluk durumu ile birlikte belgelenmiştir.

**Soru İşaretleri:**
- ⬛ **ZORUNLU** — Her firma için sorulur, atlanamaz.
- ⬜ **Koşullu** — Önceki cevaplara göre tetiklenir.

### BLOK A1: Firma Kimlik & Hukuki Yapı

**S01 — Firmanızın şirket türü nedir?** ⬛ ZORUNLU

- Tip: Tek Seçim
- Seçenekler: Şahıs İşletmesi | Limited Şirketi (Ltd. Şti.) | Anonim Şirketi (A.Ş.) | Kooperatif | Adi Ortaklık | Kollektif/Komandit Şirket | Serbest Meslek (Gerçek Kişi) | Kamu Kurumu / Kamu İktisadi Teşebbüsü | Diğer

**S02 — Firmanız ne zaman kuruldu? (Yıl / Ay)** ⬛ ZORUNLU

- Tip: Tarih Girdi
- Seçenekler: Yıl seçimi (1970–2026) | Ay seçimi

### BLOK A2: Sektör & Faaliyet Alanı

**S03 — Firmanızın kayıtlı ana faaliyet kodu (NACE Rev.2) nedir?** ⬛ ZORUNLU

- Tip: Arama + Seçim (NACE kodu listesi / sektör adı ile arama)
- Seçenekler: A – Tarım, Ormancılık, Balıkçılık | B – Madencilik ve Taş Ocakçılığı | C – İmalat | D – Elektrik, Gaz, Buhar ve İklimlendirme | E – Su, Kanalizasyon, Atık | F – İnşaat | G – Toptan ve Perakende Ticaret | H – Ulaştırma ve Depolama | I – Konaklama ve Yiyecek-İçecek | J – Bilgi ve İletişim | K – Finans ve Sigorta | L – Gayrimenkul | M – Profesyonel, Bilimsel ve Teknik Faaliyetler | N – İdari ve Destek Hizmetleri | O – Kamu Yönetimi ve Savunma | P – Eğitim | Q – Sağlık ve Sosyal Hizmetler | R – Kültür, Sanat, Eğlence ve Dinlence | S – Diğer Hizmetler | T – Hane Halkı İşveren Faaliyetleri
- Not: Birden fazla NACE kodu seçilebilir.

**S04 — Firmanızın fiili faaliyet sektörü ve ana ürün/hizmet kategorisi nedir?** ⬛ ZORUNLU

- Tip: Çoklu Seçim – detaylandırılmış alt kategoriler
- Seçenekler:
  - **İMALAT:** Gıda/İçecek | Tekstil/Hazır Giyim | Deri/Ayakkabı | Orman Ürünleri/Mobilya | Kağıt/Baskı | Kimya/İlaç/Gübre | Plastik/Kauçuk | Cam/Seramik/Çimento | Metal/Demir-Çelik | Makine/Ekipman | Elektronik/Elektrik | Otomotiv/Savunma/Havacılık | Medikal Cihaz | Diğer İmalat
  - **TARIM:** Bitkisel Üretim | Hayvancılık (Büyükbaş/Küçükbaş) | Kümes Hayvancılığı | Su Ürünleri | Arıcılık | Seracılık | Organik Tarım | Tarımsal İşleme | Diğer Tarım
  - **BİLİŞİM/YAZILIM:** Kurumsal Yazılım (ERP/CRM) | Mobil Uygulama | Oyun Geliştirme | Siber Güvenlik | Veri Analitiği/Yapay Zeka | SaaS/Bulut Hizmetleri | E-ticaret Altyapısı | Sistem Entegrasyon | BPO/Teknik Destek
  - **HİZMET:** Eğitim/Dil Okulu | Sağlık/Tıp Turizmi | Lojistik/Nakliyat | Gayrimenkul Danışmanlığı | Turizm/Otelcilik | Finans/Sigorta | Danışmanlık/Yönetim | Film/Dizi/Medya | Fuarcılık/Organizasyon | Çevre/ESG Danışmanlığı | Diğer Hizmet
  - **ENERJİ:** Güneş Enerjisi (GES) | Rüzgar Enerjisi (RES) | Jeotermal | Doğal Gaz/Petrol | Enerji Verimliliği | Diğer Enerji
  - **İNŞAAT:** Konut İnşaatı | Ticari/Sınai İnşaat | Altyapı | Taahhüt/Müteahhitlik | Diğer İnşaat

### BLOK A3: Coğrafya & Fiziksel Konum

**S05 — Firmanız hangi ilde/illerde faaliyet göstermektedir?** ⬛ ZORUNLU

- Tip: Çoklu Seçim (81 il listesi)
- Seçenekler: Tüm 81 il (çoklu seçim) | Yurt Dışı (ayrıca belirtiniz)

**S06 — Firmanızın bulunduğu fiziksel konumu hangisidir?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: Organize Sanayi Bölgesi (OSB) | Teknoloji Geliştirme Bölgesi / Teknokent / Teknopark | Serbest Bölge | Endüstri Bölgesi | Küçük Sanayi Sitesi (KSS) | Tarım/Hayvancılık İşletmesi (Kırsal Alan) | İlçe Merkezi | Şehir Merkezi / Normal İş Yeri | Kuluçka Merkezi / TEKMER | Bilim ve Teknoloji Parkı | Diğer

### BLOK A4: Firma Büyüklüğü & KOBİ Statüsü

**S07 — Firmanızın toplam çalışan sayısı kaçtır?** ⬛ ZORUNLU

- Tip: Sayısal Girdi (veya aralık seçimi)
- Seçenekler: 1–9 (Mikro) | 10–49 (Küçük) | 50–249 (Orta) | 250+ (Büyük) | Çalışan Yok (Kuruluş Aşamasında)

**S08 — Firmanızın yıllık net cirosu (satış hasılatı) yaklaşık ne kadardır?** ⬛ ZORUNLU

- Tip: Aralık Seçimi
- Seçenekler: Henüz gelir yok (Kuruluş/Ön-Gelir aşaması) | < 3 Milyon TL | 3M – 10M TL | 10M – 25M TL | 25M – 125M TL | 125M – 500M TL | 500M – 1 Milyar TL | > 1 Milyar TL

**S09 — Firmanızın bilanço büyüklüğü (toplam aktifleri) ne kadardır?** ⬜ Koşullu

- Tip: Aralık Seçimi
- Tetikleme: S08 > 0 ise tetiklenir
- Seçenekler: < 5 Milyon TL | 5M – 25M TL | 25M – 125M TL | 125M – 500M TL | 500M – 1 Milyar TL | > 1 Milyar TL | Bilmiyorum / Uygulanamaz

### BLOK A5: Finansal Durum & Eliminasyon Kriterleri

**S10 — Firmanızın vadesi geçmiş SGK (Sosyal Güvenlik Kurumu) borcu var mı?** ⬛ ZORUNLU

- Tip: Tek Seçim
- Seçenekler: Hayır, vadesi geçmiş borç yok | Evet, borç var ancak yapılandırma altında | Evet, aktif borç var | Bilmiyorum

**S11 — Firmanızın vadesi geçmiş vergi borcu var mı?** ⬛ ZORUNLU

- Tip: Tek Seçim
- Seçenekler: Hayır, vadesi geçmiş vergi borcu yok | Evet, borç var ancak yapılandırma altında | Evet, aktif borç var | Bilmiyorum

**S12 — Firmanız KOSGEB'e kayıtlı mı?** ⬛ ZORUNLU

- Tip: Tek Seçim
- Seçenekler: Evet, kayıtlıyız | Hayır, kayıtlı değiliz | Başvuru sürecindeyiz | KOSGEB'e tabi değiliz (kamu, büyük firma vb.)

### BLOK A6: İhracat & Uluslararası Faaliyet

**S13 — Firmanız şu anda ihracat yapıyor mu veya ihracata yönelik faaliyet planlıyor mu?** ⬛ ZORUNLU

- Tip: Tek Seçim
- Seçenekler: Hayır, yalnızca yurt içi pazar | İhracata hazırlık aşamasındayız (henüz ihracat yok) | Evet, düzenli mal ihracatı yapıyoruz | Evet, hizmet ihracatı yapıyoruz | Evet, hem mal hem hizmet ihracatı yapıyoruz | İhracat ciromuzu artırmayı planlıyoruz

**S14 — İhracat yapıyorsanız, ihracat geliriniz toplam cironuzun yaklaşık yüzde kaçını oluşturmaktadır?** ⬜ Koşullu

- Tip: Tek Seçim
- Tetikleme: S13 ≠ 'Hayır, yalnızca yurt içi pazar' ise tetiklenir
- Seçenekler: %1–%25 | %26–%50 | %51–%75 | %76–%100 | İlk ihracat henüz gerçekleşmedi (Planlama aşamasında)

**S15 — Hangi ülkelere ihracat yapıyorsunuz veya yapmayı planlıyorsunuz?** ⬜ Koşullu

- Tip: Ülke Çoklu Seçim (Bölge/Ülke bazlı arama)
- Tetikleme: S13 ≠ 'Hayır' ise tetiklenir
- Seçenekler: Avrupa (AB) | Ortadoğu (GCC, Körfez) | Kuzey Afrika | Orta Asya | Doğu Avrupa / Balkanlar | Kuzey Amerika (ABD, Kanada) | Güney/Güneydoğu Asya | Sahra Altı Afrika | Latin Amerika | Diğer (ülke belirtiniz)

### BLOK A7: Ar-Ge & İnovasyon Kapasitesi

**S16 — Firmanız araştırma-geliştirme (Ar-Ge) veya tasarım/inovasyon faaliyeti yürütüyor mu?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: Hayır, Ar-Ge faaliyetimiz yok | Evet, proje bazlı Ar-Ge yapıyoruz (Ar-Ge Merkezi statüsü yok) | Evet, Ar-Ge Merkezi statümüz var (5746 sayılı Kanun) | Evet, Teknokent'te Ar-Ge yapıyoruz | Evet, Tasarım Merkezi statümüz var | Evet, üniversiteyle ortak Ar-Ge yapıyoruz | Evet, savunma/uzay alanında Ar-Ge yapıyoruz

**S17 — Firmanızda kaç kişi Ar-Ge, yazılım geliştirme veya tasarım faaliyetlerinde tam zamanlı çalışmaktadır?** ⬜ Koşullu

- Tip: Sayısal Girdi
- Tetikleme: S16 ≠ 'Hayır' ise tetiklenir
- Seçenekler: 0 | 1–5 | 6–10 | 11–15 | 16–30 | 30+

### BLOK A8: Yatırım Planları

**S18 — Firmanız önümüzdeki 24 ayda sabit yatırım yapmayı planlıyor mu?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: Hayır, yatırım planımız yok | Makine-Teçhizat Alımı | Yazılım/Teknoloji Alımı | Fabrika/Tesis/Depo İnşaatı veya Satın Alımı | Üretim Kapasitesi Artışı | Enerji Yatırımı (GES/RES/Jeotermal) | Tarımsal Altyapı (Sera, Depo, Sulama, Damızlık Ahır) | Turizm Tesisi (Otel, Tatil Köyü) | Yurt Dışı Ofis/Veri Merkezi/Şube | Dijital Dönüşüm (ERP, MES, Otomasyon) | Yeşil/Sürdürülebilirlik Dönüşümü

**S19 — Planladığınız yatırımın toplam tahmini bütçesi ne kadardır?** ⬜ Koşullu

- Tip: Aralık Seçimi
- Tetikleme: S18 ≠ 'Hayır' ise tetiklenir
- Seçenekler: < 500.000 TL | 500K – 2M TL | 2M – 10M TL | 10M – 50M TL | 50M – 500M TL | 500M TL – 1 Milyar TL | > 1 Milyar TL

### BLOK A9: İstihdam & Girişimci Profili

**S20 — Firmanız önümüzdeki 12 ayda yeni personel istihdam etmeyi planlıyor mu?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: Hayır, yeni istihdam planı yok | Evet, genel işgücü | Evet, genç çalışan (18–29 yaş) | Evet, kadın çalışan | Evet, engelli çalışan | Evet, Ar-Ge / Mühendis | Evet, nitelikli teknik personel | Evet, tarım/hayvancılık işçisi | Evet, eski hükümlü | Evet, uzun süreli işsiz (1 yılı aşkın) | Evet, 50 yaş üstü

**S21 — Firmanızın sahibi, kurucusu veya yönetim kurulu üyelerinin profili nasıldır?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: 30 yaş altı genç girişimci | Kadın girişimci/kadın yönetim ağırlıklı | Engelli girişimci | Gazi veya şehit yakını | 50 yaş üstü girişimci | Hiçbiri / Standart profil

### BLOK A10: Özel Statüler & Resmi Kayıtlar

**S22 — Firmanız aşağıdaki özel statü veya kayıtlardan herhangi birine sahip mi?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: Teknokent (TGB) kiracısı/lisansiyesi | OSB (Organize Sanayi Bölgesi) üyesi | Ar-Ge Merkezi statüsü (5746) | Tasarım Merkezi statüsü (5746) | Serbest Bölge faaliyet ruhsatı | SSB (Savunma Sanayii Başkanlığı) onaylı tedarikçi | TÜRKAK akreditasyonu | İhracatçı Birliği üyeliği | KOSGEB'e kayıtlı | DYS (Destek Yönetim Sistemi) kaydı | KEP (Kayıtlı Elektronik Posta) adresi | 5070 sayılı Kanun kapsamında elektronik imza | Hiçbiri

### BLOK A11: Sektörel Özel Sorular

**S23 — Firmanızın tarımsal faaliyetleri var mı ve resmi kayıtlarınız mevcut mu?** ⬜ Koşullu

- Tip: Çoklu Seçim
- Tetikleme: S03 = A (Tarım) veya S04 = Tarım kategorisi ise tetiklenir
- Seçenekler: Tarımsal faaliyetimiz yok | Çiftçi Kayıt Sistemi (ÇKS) kaydımız var | TÜRKVET (Hayvancılık Kayıt Sistemi) kaydımız var | Özel Kesimhane/Su Ürünleri Sicil kaydı var | Organik Tarım sertifikamız var (Bakanlık onaylı) | İyi Tarım Uygulamaları (İTU) sertifikamız var | Tarımsal işleme tesisi ruhsatımız var | Arazi/bağ/bahçe tapumuz/kira sözleşmemiz var

**S24 — Firmanızın enerji üretimi veya enerji verimliliğine yönelik yatırım planı var mı?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: Hayır | Güneş Enerjisi Santrali (GES) kurmayı/kurdu | Rüzgar Enerjisi (RES) yatırımı | Jeotermal enerji yatırımı | Enerji Verimliliği Projesi (ISO 50001 vb.) | Biyogaz/Biyokütle tesisi | Elektrifikasyon / Depolama sistemi | Hidroelektrik santral | Doğalgaz / LNG altyapısı | Diğer Yenilenebilir Enerji

**S25 — Firmanızın sürdürülebilirlik, ESG (Çevre-Sosyal-Yönetişim) veya yeşil dönüşüm çalışmaları var mı?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: Hayır, bu alanda çalışmamız yok | ISO 14001 (Çevre Yönetimi) sertifikamız var/planlıyoruz | ISO 50001 (Enerji Yönetimi) sertifikamız var/planlıyoruz | LEED / BREEAM sertifikası (yeşil bina) | Karbon ayak izi hesaplaması yapıyoruz | Sürdürülebilirlik raporu yayınlıyoruz | Türkiye Sürdürülebilirlik Raporlaması Standartları (TSRS) hazırlığındayız | AB Taksonomisi/CBAM (Karbon Sınır Düzenleme) çalışmaları yapıyoruz | Sosyal etki ölçümleri / Üçüncü taraf ESG denetimi

**S26 — Firmanızın savunma sanayii, uzay veya çift kullanımlı teknoloji alanında faaliyet veya planı var mı?** ⬜ Koşullu

- Tip: Çoklu Seçim
- Tetikleme: S04 = Savunma/Havacılık veya S16 = Savunma Ar-Ge ise tetiklenir
- Seçenekler: Hayır | SSB (Savunma Sanayii Başkanlığı) onaylı tedarikçiyiz | NATO/Müttefik ülkeler için savunma projesi üretiyoruz | Uzay teknolojileri (TUA, Türksat vb.) | İnsansız sistemler (İHA, SİHA, İnsansız Deniz Aracı) | Siber güvenlik / elektronik harp sistemleri | Medikal/çift kullanımlı teknoloji | Yerli yazılım/yapay zeka savunma uygulamaları

**S27 — Firmanızın inşaat veya gayrimenkul geliştirme faaliyeti var mı?** ⬜ Koşullu

- Tip: Çoklu Seçim
- Tetikleme: S03 = F (İnşaat) veya S04 = İnşaat kategorisi ise tetiklenir
- Seçenekler: Hayır | Konut projesi geliştiriyoruz (TOKİ işbirliği dahil) | Ticari/sınai tesis inşaatı | Altyapı/yol/su projesi taahhütü | Kentsel dönüşüm projesi | Yurt dışı müteahhitlik/yapım projesi | Turizm tesisi geliştirme | Endüstriyel alan/OSB inşaatı

**S28 — Firmanız turizm, konaklama veya yiyecek-içecek sektöründe midir?** ⬜ Koşullu

- Tip: Çoklu Seçim
- Tetikleme: S03 = I (Konaklama/Yiyecek-İçecek) veya S04 = Turizm ise tetiklenir
- Seçenekler: Hayır | Otel/Pansiyon/Butik Otel işletiyoruz | Tatil Köyü/Kamp alanı | Restoran/Kafe zinciri | Gastronomi/Yemek Turizmi | Sağlık/Termal Turizm tesisi | Golf/Spor Turizmi tesisi | Kültür/Eko Turizm | Seyahat Acentesi (A/B/C grubu) | MICE (Kongre/Fuar/Etkinlik) tesisi

**S29 — Firmanız finans, sigorta veya finansal teknoloji (FinTech) alanında faaliyet gösteriyor mu?** ⬜ Koşullu

- Tip: Çoklu Seçim
- Tetikleme: S03 = K (Finans) ise tetiklenir
- Seçenekler: Hayır | Banka / Katılım Bankası | Leasing / Faktoring / Finansman Şirketi | Sigorta / Emeklilik Şirketi | Ödeme Kuruluşu / E-Cüzdan | FinTech (Regtech, InsurTech, LendTech vb.) | Kripto Varlık Hizmet Sağlayıcısı | Portföy Yönetimi / Yatırım Danışmanlığı

**S30 — Firmanız daha önce herhangi bir devlet desteği, hibe veya teşvikten yararlandı mı?** ⬛ ZORUNLU

- Tip: Çoklu Seçim
- Seçenekler: Hayır, hiç yararlanmadık | KOSGEB desteği aldık | TÜBİTAK projesi yürüttük | Yatırım Teşvik Belgesi aldık | Kalkınma Ajansı hibesi aldık | TKDK/IPARD hibesi aldık | Ticaret Bakanlığı ihracat desteği aldık | İŞKUR teşviğinden yararlandık | Başka devlet kurumundan destek aldık

### Koşullu Soru Tetikleme Kuralları (Özet)

| Soru | Tetikleme Koşulu |
|---|---|
| S09 (Bilanço) | S08 > 0 ise |
| S14 (İhracat Oranı) | S13 ≠ 'Hayır, yalnızca yurt içi pazar' ise |
| S15 (Hedef Ülkeler) | S13 ≠ 'Hayır' ise |
| S17 (Ar-Ge Personeli) | S16 ≠ 'Hayır' ise |
| S19 (Yatırım Bütçesi) | S18 ≠ 'Hayır' ise |
| S23 (Tarım Kaydı) | S03 = A veya S04 = Tarım ise |
| S26 (Savunma) | S04 = Savunma/Havacılık veya S16 = Savunma Ar-Ge ise |
| S27 (İnşaat) | S03 = F veya S04 = İnşaat ise |
| S28 (Turizm) | S03 = I veya S04 = Turizm ise |
| S29 (Finans) | S03 = K ise |

### Dezzcovery Akış Mimarisi

**Katman A** (30 sabit soru) → **Eliminasyon Kontrol Motoru** → **Skor Hesaplama** → %60 üstü eşleşmeler için **Katman B** (AI Dinamik Sorular) → **Final Karne**

**Eliminasyon Sırası:**
1. Temel Eliminatörler: S01 (Şirket türü), S10 (SGK borcu), S11 (Vergi borcu)
2. Sektörel Eliminasyon: S03 (NACE) + S04 (Alt sektör)
3. Konum Eliminasyonu: S05 (İl) + S06 (Konum tipi)
4. Ölçek Eliminasyonu: S07 (Personel) + S08/S09 (Ciro/Bilanço)
5. Faaliyet Eliminasyonu: S12 (KOSGEB kaydı) + S16 (Ar-Ge) + S13 (İhracat) + S22 (DYS/KEP) + S23 (Tarım kaydı)
6. Skor Hesaplama: Eliminasyondan geçen destekler için ağırlıklı skor
7. Katman B Tetikleme: Skoru %60+ olan destekler için derinleştirme soruları
8. Final Karne: Yüksekten düşüğe sıralı destek listesi

---

## 11. Bildirim Sistemi

Platform iki kanal üzerinden bildirim gönderir: e-posta ve uygulama içi (in-app notification).

| Olay | E-posta | In-App |
|---|---|---|
| Firmaya kullanıcı daveti | ✓ | ✓ |
| Başvuru durumu değişikliği | ✓ | ✓ |
| Review tamamlandı (AI veya Human) | ✓ | ✓ |
| Teşvik/destek onay veya red sonucu | ✓ | ✓ |
| Hesap doğrulama (OTP) | ✓ | ✗ |
| Şifre sıfırlama linki | ✓ | ✗ |
| Abonelik değişikliği / yenileme | ✓ | ✓ |

---

## 12. Dashboard

Her kullanıcı tipi kendine özgü bir dashboard deneyimine sahiptir.

### 12.1 Kullanıcı Dashboard

- Başvuru özeti (toplam, duruma göre dağılım)
- Edinilen destekler
- Firmalar ve ürünler özeti
- Dezzcovery sonuçları
- Bildirimler

### 12.2 Admin Dashboard

- Danışman olunan firmaların listesi
- Bu firmalardaki başvurular ve durumları
- Oluşturulan teşvik/destek durumları (onay bekleyen, onaylı, reddedilen)

### 12.3 Süper Admin Dashboard

- Sistem geneli istatistikler
- Onay bekleyen teşvik ve destekler
- Human Review bekleyen başvurular
- Abonelik özeti
- Kullanıcı ve firma istatistikleri

---

## 13. Fonksiyonel Olmayan Gereksinimler

### 13.1 Çoklu Dil Desteği

Platform Türkçe ve İngilizce olmak üzere iki dilde hizmet verecektir. Tüm arayüz metinleri, bildirimler ve sistem mesajları her iki dilde de sunulacaktır.

### 13.2 Ödeme Altyapısı

iyzico ödeme altyapısı entegre edilecektir. Aylık ve yıllık abonelik döngüleri, ek hak satın alımları ve fatura yönetimi desteklenecektir.

### 13.3 Güvenlik

- OAuth 2.0 ile sosyal giriş (Google, Outlook)
- OTP tabanlı e-posta doğrulama
- Rol bazlı erişim kontrolü (RBAC)
- Firma bazlı veri izolasyonu

### 13.4 Yapay Zekâ Altyapısı

Tüm yapay zekâ modülleri (Dezzcovery, Dezzviewer, Dezzviser) agno framework'ü ile implemente edilecektir. Başlangıçta basit yapılarak zamanla güçlendirilecektir.

---

## 14. MVP Kapsamı ve Yol Haritası

### 14.1 MVP'ye Dahil

- Kimlik doğrulama ve hesap yönetimi (kayıt, giriş, profil, parola)
- Firma yönetimi (CRUD, davet, rol atama)
- Ürün yönetimi (CRUD)
- Teşvik ve destek yönetimi (Admin oluşturma, Süper Admin onay)
- Form builder (sayfa/grup/alan hiyerarşisi, 4 alan türü)
- Başvuru yönetimi (oluşturma, durum takibi, CRUD)
- Dezzcovery (onboarding + AI destek keşfi)
- Dezzviewer (AI başvuru denetimi)
- Human Review (Süper Admin, yalnızca Premium)
- Abonelik sistemi (4 paket + ek hak satın alımı)
- Bildirim sistemi (e-posta + in-app)
- Dashboard (kullanıcı, admin, süper admin)
- Çoklu dil desteği (TR/EN)

### 14.2 MVP Sonrası (Gelecek Sürümler)

- Raporlama modülü (tüm kullanıcı tipleri için)
- Dezzviser (başvuru sırası stratejik öneri motoru)
- Devlete otomatik başvuru iletimi ve süreç takibi
- Gelişmiş analitik ve iş zekası araçları

---

## 15. Açık Kalemler (Bekleyen Kararlar)

Aşağıdaki konular henüz netleştirilmemiştir ve ilerleyen aşamalarda belirlenecektir:

| # | Konu | Durum |
|---|---|---|
| 1 | Kayıt sırasında alınacak kullanıcı bilgileri (alan listesi) | Bekliyor |
| 2 | Form builder alan tipleri (text, select, file upload vb.) detayları | Bekliyor |
| 3 | Abonelik fiyatlandırması | Bekliyor |
| 4 | Ek hak fiyatlandırması | Bekliyor |

---

*— Doküman Sonu —*