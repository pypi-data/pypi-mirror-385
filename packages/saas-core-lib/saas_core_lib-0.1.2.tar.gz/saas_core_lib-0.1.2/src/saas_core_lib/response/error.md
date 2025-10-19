# 📖 Hata Sözlüğü (Error Dictionary)

## 🔹 1. Kimlik Doğrulama (Auth & JWT)

| Kod                        | HTTP | Açıklama                                                         |
| -------------------------- | ---- | ---------------------------------------------------------------- |
| `AUTH_INVALID_CREDENTIALS` | 401  | Geçersiz kullanıcı adı veya şifre                                |
| `AUTH_TOKEN_MISSING`       | 401  | JWT token gönderilmedi                                           |
| `AUTH_TOKEN_INVALID`       | 401  | Geçersiz veya bozulan JWT token                                  |
| `AUTH_TOKEN_EXPIRED`       | 401  | JWT token süresi dolmuş                                          |
| `AUTH_UNAUTHORIZED`        | 403  | Bu işlem için yetkiniz yok                                       |
| `AUTH_PROVIDER_ERROR`      | 502  | Harici kimlik sağlayıcısında hata (Google, Microsoft, Apple vs.) |

---

## 🔹 2. API Key

| Kod                       | HTTP | Açıklama                                       |
| ------------------------- | ---- | ---------------------------------------------- |
| `API_KEY_MISSING`         | 401  | API key gönderilmedi                           |
| `API_KEY_INVALID`         | 401  | Geçersiz API key                               |
| `API_KEY_REVOKED`         | 403  | API key iptal edilmiş                          |
| `API_KEY_EXPIRED`         | 401  | API key süresi dolmuş                          |
| `API_KEY_SCOPE_DENIED`    | 403  | Bu işlem için gerekli scope’a sahip değilsiniz |
| `API_KEY_TENANT_MISMATCH` | 403  | API key farklı tenant’a ait                    |

---

## 🔹 3. Tenant / Kullanıcı Yönetimi

| Kod                      | HTTP | Açıklama                                         |
| ------------------------ | ---- | ------------------------------------------------ |
| `TENANT_NOT_FOUND`       | 404  | Tenant bulunamadı                                |
| `TENANT_DISABLED`        | 403  | Tenant devre dışı bırakılmış                     |
| `USER_NOT_FOUND`         | 404  | Kullanıcı bulunamadı                             |
| `USER_ALREADY_EXISTS`    | 409  | Bu e-posta/telefon ile kullanıcı zaten kayıtlı   |
| `USER_NOT_ACTIVE`        | 403  | Kullanıcı aktif değil                            |
| `USER_PERMISSION_DENIED` | 403  | Kullanıcı bu işlem için gerekli izne sahip değil |

---

## 🔹 4. Güvenlik / Rate Limit

| Kod                            | HTTP | Açıklama                                        |
| ------------------------------ | ---- | ----------------------------------------------- |
| `SECURITY_RATE_LIMIT`          | 429  | Çok fazla istek gönderdiniz, lütfen bekleyin    |
| `SECURITY_IP_BLOCKED`          | 403  | IP adresiniz geçici olarak engellendi           |
| `SECURITY_SUSPICIOUS_ACTIVITY` | 403  | Şüpheli aktivite tespit edildi                  |
| `SECURITY_FORBIDDEN`           | 403  | Güvenlik politikası nedeniyle erişim engellendi |

---

## 🔹 5. Veri & Kaynak İşlemleri

| Kod                         | HTTP | Açıklama                                             |
| --------------------------- | ---- | ---------------------------------------------------- |
| `RESOURCE_NOT_FOUND`        | 404  | İstenen kaynak bulunamadı                            |
| `RESOURCE_ALREADY_EXISTS`   | 409  | Kaynak zaten mevcut                                  |
| `RESOURCE_LOCKED`           | 423  | Kaynak başka bir işlem tarafından kilitlenmiş        |
| `RESOURCE_VALIDATION_ERROR` | 422  | Geçersiz veri girişi                                 |
| `RESOURCE_QUOTA_EXCEEDED`   | 403  | Kaynak kotası aşıldı (ör: maksimum kullanıcı sayısı) |

---

## 🔹 6. Ödeme & Abonelik

| Kod                              | HTTP | Açıklama                                  |
| -------------------------------- | ---- | ----------------------------------------- |
| `BILLING_PAYMENT_FAILED`         | 402  | Ödeme başarısız oldu                      |
| `BILLING_CARD_EXPIRED`           | 402  | Kartın süresi dolmuş                      |
| `BILLING_SUBSCRIPTION_NOT_FOUND` | 404  | Abonelik bulunamadı                       |
| `BILLING_SUBSCRIPTION_INACTIVE`  | 403  | Abonelik aktif değil                      |
| `BILLING_PLAN_UPGRADE_REQUIRED`  | 403  | Bu özellik için plan yükseltmeniz gerekli |

---

## 🔹 7. Sistem / Altyapı

| Kod                       | HTTP | Açıklama                                        |
| ------------------------- | ---- | ----------------------------------------------- |
| `SYSTEM_MAINTENANCE`      | 503  | Sistem bakımda                                  |
| `SYSTEM_ERROR`            | 500  | Beklenmedik bir sistem hatası oluştu            |
| `SYSTEM_DEPENDENCY_ERROR` | 502  | Harici servis hatası (ör: Redis, Elasticsearch) |
| `SYSTEM_TIMEOUT`          | 504  | İstek zaman aşımına uğradı                      |
| `SYSTEM_NOT_IMPLEMENTED`  | 501  | Bu özellik henüz uygulanmadı                    |

---


