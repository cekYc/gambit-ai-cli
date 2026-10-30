# kod-sure-js · puan 1.00

**Not:** 11/11 test

## Prompt

JavaScript'te (Node.js) `parseDuration(str)` fonksiyonunu yaz. "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi
metinleri toplam saniyeye çevirsin. Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve
bu sırayla gelir; aralarında boşluk olabilir de olmayabilir de. Geçersiz girdide (boş metin, bilinmeyen birim,
sayısı olmayan birim, yanlış sıra, tekrar eden birim) Error fırlatsın.
Fonksiyonu `module.exports = { parseDuration };` ile dışa aktar.
Sadece JavaScript kodunu tek bir ```javascript bloğu içinde ver.

## Cevap

```javascript
/**
 * Verilen süre metnini toplam saniyeye çevirir.
 * Desteklenen birimler: h (saat), m (dakika), s (saniye).
 * 
 * @param {string} str - Süre metni (örn: "1h 30m", "45s")
 * @returns {number} Toplam saniye cinsinden değer
 * @throws {Error} Geçersiz format veya birimlerde hata durumunda
 */
function parseDuration(str) {
  if (!str || typeof str !== 'string' || str.trim() === "") {
    throw new Error("Geçersiz girdi: Metin boş olamaz.");
  }

  const trimmedStr = str.trim();
  // Regex açıklaması: 
  // Sayı (gruplar) + Birim (h, m veya s)
  // Aralarda boşluk olabilir (\s*)
  const pattern = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
  
  // Boşlukları temizleyip regex ile kontrol etme (boş string gelmemesi için trim sonrası kontrol önemli)
  // Ancak regex'in tüm metni kapsadığından emin olmak için replace ile boşlukları normalize edelim
  const normalized = trimmedStr.replace(/\s+/g, '');
  
  // Eğer girdi tamamen boşsa veya sadece boşluklardan oluşuyorsa (regex bunu yakalamayabilir)
  if (!normalized) {
    throw new Error("Geçersiz girdi: Boş metin.");
  }

  // Regex ile parçaları yakala
  // Not: regex'i normalize edilmiş string üzerinde çalıştırıyoruz ki boşluklar sorun çıkarmasın
  const match = normalized.match(/^(\d+h)?(\d+m)?(\d+s)?$/);

  if (!match || normalized === "") {
    throw new Error("Geçersiz format: Yanlış sıra, bilinmeyen birim veya tekrar eden birim.");
  }

  // Regex match dizisi: [full_match, h_part, m_part, s_part]
  const [, hPart, mPart, sPart] = match;

  // Eğer regex eşleşmediyse ama string hala doluysa (örn: "1h 20x") hata fırlatır
  if (!hPart && !mPart && !sPart) {
    throw new Error("Geçersiz girdi.");
  }

  // Regex'in tüm karakterleri tükettiğinden emin olalım (kalan karakter kontrolü)
  const combinedMatch = (hPart || "") + (mPart || "") + (sPart || "");
  if (combinedMatch.length !== normalized.length) {
    throw new Error("Geçersiz format: Bilinmeyen birim veya yanlış sıralama.");
  }

  let totalSeconds = 0;

  if (hPart) {
    totalSeconds += parseInt(hPart, 10) * 3600;
  }
  if (mPart) {
    totalSeconds += parseInt(mPart, 10) * 60;
  }
  if (sPart) {
    totalSeconds += parseInt(sPart, 10);
  }

  return totalSeconds;
}

module.exports = { parseDuration };
```

## Notlandırılan kod/komut

```
/**
 * Verilen süre metnini toplam saniyeye çevirir.
 * Desteklenen birimler: h (saat), m (dakika), s (saniye).
 * 
 * @param {string} str - Süre metni (örn: "1h 30m", "45s")
 * @returns {number} Toplam saniye cinsinden değer
 * @throws {Error} Geçersiz format veya birimlerde hata durumunda
 */
function parseDuration(str) {
  if (!str || typeof str !== 'string' || str.trim() === "") {
    throw new Error("Geçersiz girdi: Metin boş olamaz.");
  }

  const trimmedStr = str.trim();
  // Regex açıklaması: 
  // Sayı (gruplar) + Birim (h, m veya s)
  // Aralarda boşluk olabilir (\s*)
  const pattern = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
  
  // Boşlukları temizleyip regex ile kontrol etme (boş string gelmemesi için trim sonrası kontrol önemli)
  // Ancak regex'in tüm metni kapsadığından emin olmak için replace ile boşlukları normalize edelim
  const normalized = trimmedStr.replace(/\s+/g, '');
  
  // Eğer girdi tamamen boşsa veya sadece boşluklardan oluşuyorsa (regex bunu yakalamayabilir)
  if (!normalized) {
    throw new Error("Geçersiz girdi: Boş metin.");
  }

  // Regex ile parçaları yakala
  // Not: regex'i normalize edilmiş string üzerinde çalıştırıyoruz ki boşluklar sorun çıkarmasın
  const match = normalized.match(/^(\d+h)?(\d+m)?(\d+s)?$/);

  if (!match || normalized === "") {
    throw new Error("Geçersiz format: Yanlış sıra, bilinmeyen birim veya tekrar eden birim.");
  }

  // Regex match dizisi: [full_match, h_part, m_part, s_part]
  const [, hPart, mPart, sPart] = match;

  // Eğer regex eşleşmediyse ama string hala doluysa (örn: "1h 20x") hata fırlatır
  if (!hPart && !mPart && !sPart) {
    throw new Error("Geçersiz girdi.");
  }

  // Regex'in tüm karakterleri tükettiğinden emin olalım (kalan karakter kontrolü)
  const combinedMatch = (hPart || "") + (mPart || "") + (sPart || "");
  if (combinedMatch.length !== normalized.length) {
    throw new Error("Geçersiz format: Bilinmeyen birim veya yanlış sıralama.");
  }

  let totalSeconds = 0;

  if (hPart) {
    totalSeconds += parseInt(hPart, 10) * 3600;
  }
  if (mPart) {
    totalSeconds += parseInt(mPart, 10) * 60;
  }
  if (sPart) {
    totalSeconds += parseInt(sPart, 10);
  }

  return totalSeconds;
}

module.exports = { parseDuration };
```
