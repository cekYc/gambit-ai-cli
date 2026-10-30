# kod-sure-js · puan 0.82

**Not:** 9/11 test; başarısız: throws(() => S.parseDuration("10s 5m")) | throws(() => S.parseDuration("1h 2h"))

## Prompt

JavaScript'te (Node.js) `parseDuration(str)` fonksiyonunu yaz. "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi
metinleri toplam saniyeye çevirsin. Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve
bu sırayla gelir; aralarında boşluk olabilir de olmayabilir de. Geçersiz girdide (boş metin, bilinmeyen birim,
sayısı olmayan birim, yanlış sıra, tekrar eden birim) Error fırlatsın.
Fonksiyonu `module.exports = { parseDuration };` ile dışa aktar.
Sadece JavaScript kodunu tek bir ```javascript bloğu içinde ver.

## Cevap

```javascript
function parseDuration(str) {
  if (typeof str !== 'string' || str.trim() === '') {
    throw new Error('Geçersiz giriş: Boş metin veya null/undefined.');
  }

  const originalStr = str;
  let cleanStr = str.replace(/\s+/g, ''); // Tüm boşlukları kaldır
  if (cleanStr === '') {
    throw new Error('Geçersiz giriş: Sadece boşluklar içeriyor.');
  }

  // Regex ile desenleri yakala: sayı + birim
  const pattern = /(\d+)([hms])/g;
  let match;
  
  let hours = 0;
  let minutes = 0;
  let seconds = 0;
  let lastIndex = 0;

  while ((match = pattern.exec(cleanStr)) !== null) {
    const value = parseInt(match[1], 10);
    const unit = match[2];

    // Birim kontrolü (sadece h, m, s kabul edilir)
    if (!['h', 'm', 's'].includes(unit)) {
      throw new Error(`Bilinmeyen birim: ${unit}`);
    }

    // Sayısal değer kontrolü (Regex zaten sayı yakaladığı için burası daha çok mantıksal doğrulama)
    if (!/^\d+$/.test(match[1])) {
      throw new Error('Sayısı olmayan birim');
    }

    // Sıralama ve tekrar kontrolü
    const currentUnitIndex = ['h', 'm', 's'].indexOf(unit);
    
    // Bir önceki eşleşme var mı?
    if (match.index !== lastIndex) {
      // Eğer bir önceki birim mevcut değilse veya sırası yanlışsa hata ver
      // Ancak burada daha basit bir yaklaşım: Birimi zaten işledik mi kontrol et.
      
      // Daha kesin kontrol: İşlenen birimler dizisi
      const processedUnits = [];
      let tempMatch;
      let tempLastIndex = 0;
      while ((tempMatch = pattern.exec(cleanStr)) !== null) {
        if (tempMatch.index === lastIndex) break; // Aynı yerde duruyorsa devam et
        processedUnits.push(tempMatch[2]);
        tempLastIndex = tempMatch.index + tempMatch[1].length + 1; // Birim uzunluğu dahil
      }

      const currentUnit = unit;
      
      // Sıralama kontrolü: h -> m -> s olmalı.
      if (processedUnits.length > 0) {
        const lastProcessedIndex = ['h', 'm', 's'].indexOf(processedUnits[processedUnits.length - 1]);
        const currentIndex = ['h', 'm', 's'].indexOf(currentUnit);
        
        // Eğer bir önceki birim h, m veya s ise ve şu anki birim ondan sonra gelmiyorsa (veya aynıysa) hata.
        if (currentIndex <= lastProcessedIndex) {
           throw new Error('Yanlış sıra: Birimler h -> m -> s sırasıyla gelmelidir.');
        }
      }

      // Tekrar kontrolü: Aynı birim iki kez geldiyse
      const unitCount = processedUnits.filter(u => u === currentUnit).length;
      if (unitCount > 0) {
        throw new Error('Tekrar eden birim');
      }
    } else {
       // İlk eşleşme olduğu için sıralama ve tekrar kontrolü yukarıdaki döngü içinde yapılacak.
       // Ancak basitlik adına, her adımda tüm işlenenleri kontrol edelim.
    }

    // Değerleri ekle
    switch (unit) {
      case 'h': hours += value; break;
      case 'm': minutes += value; break;
      case 's': seconds += value; break;
    }

    lastIndex = match.index + match[0].length;
  }

  // Tüm string işlendi mi? Eğer hayır, kalan karakterler varsa hata (örneğin "1h2x")
  if (lastIndex !== cleanStr.length) {
    throw new Error('Geçersiz giriş: Beklenmeyen karakterler veya eksik birim.');
  }

  // Toplam saniye hesapla
  const totalSeconds = hours * 3600 + minutes * 60 + seconds;

  return totalSeconds;
}

module.exports = { parseDuration };
```

## Notlandırılan kod/komut

```
function parseDuration(str) {
  if (typeof str !== 'string' || str.trim() === '') {
    throw new Error('Geçersiz giriş: Boş metin veya null/undefined.');
  }

  const originalStr = str;
  let cleanStr = str.replace(/\s+/g, ''); // Tüm boşlukları kaldır
  if (cleanStr === '') {
    throw new Error('Geçersiz giriş: Sadece boşluklar içeriyor.');
  }

  // Regex ile desenleri yakala: sayı + birim
  const pattern = /(\d+)([hms])/g;
  let match;
  
  let hours = 0;
  let minutes = 0;
  let seconds = 0;
  let lastIndex = 0;

  while ((match = pattern.exec(cleanStr)) !== null) {
    const value = parseInt(match[1], 10);
    const unit = match[2];

    // Birim kontrolü (sadece h, m, s kabul edilir)
    if (!['h', 'm', 's'].includes(unit)) {
      throw new Error(`Bilinmeyen birim: ${unit}`);
    }

    // Sayısal değer kontrolü (Regex zaten sayı yakaladığı için burası daha çok mantıksal doğrulama)
    if (!/^\d+$/.test(match[1])) {
      throw new Error('Sayısı olmayan birim');
    }

    // Sıralama ve tekrar kontrolü
    const currentUnitIndex = ['h', 'm', 's'].indexOf(unit);
    
    // Bir önceki eşleşme var mı?
    if (match.index !== lastIndex) {
      // Eğer bir önceki birim mevcut değilse veya sırası yanlışsa hata ver
      // Ancak burada daha basit bir yaklaşım: Birimi zaten işledik mi kontrol et.
      
      // Daha kesin kontrol: İşlenen birimler dizisi
      const processedUnits = [];
      let tempMatch;
      let tempLastIndex = 0;
      while ((tempMatch = pattern.exec(cleanStr)) !== null) {
        if (tempMatch.index === lastIndex) break; // Aynı yerde duruyorsa devam et
        processedUnits.push(tempMatch[2]);
        tempLastIndex = tempMatch.index + tempMatch[1].length + 1; // Birim uzunluğu dahil
      }

      const currentUnit = unit;
      
      // Sıralama kontrolü: h -> m -> s olmalı.
      if (processedUnits.length > 0) {
        const lastProcessedIndex = ['h', 'm', 's'].indexOf(processedUnits[processedUnits.length - 1]);
        const currentIndex = ['h', 'm', 's'].indexOf(currentUnit);
        
        // Eğer bir önceki birim h, m veya s ise ve şu anki birim ondan sonra gelmiyorsa (veya aynıysa) hata.
        if (currentIndex <= lastProcessedIndex) {
           throw new Error('Yanlış sıra: Birimler h -> m -> s sırasıyla gelmelidir.');
        }
      }

      // Tekrar kontrolü: Aynı birim iki kez geldiyse
      const unitCount = processedUnits.filter(u => u === currentUnit).length;
      if (unitCount > 0) {
        throw new Error('Tekrar eden birim');
      }
    } else {
       // İlk eşleşme olduğu için sıralama ve tekrar kontrolü yukarıdaki döngü içinde yapılacak.
       // Ancak basitlik adına, her adımda tüm işlenenleri kontrol edelim.
    }

    // Değerleri ekle
    switch (unit) {
      case 'h': hours += value; break;
      case 'm': minutes += value; break;
      case 's': seconds += value; break;
    }

    lastIndex = match.index + match[0].length;
  }

  // Tüm string işlendi mi? Eğer hayır, kalan karakterler varsa hata (örneğin "1h2x")
  if (lastIndex !== cleanStr.length) {
    throw new Error('Geçersiz giriş: Beklenmeyen karakterler veya eksik birim.');
  }

  // Toplam saniye hesapla
  const totalSeconds = hours * 3600 + minutes * 60 + seconds;

  return totalSeconds;
}

module.exports = { parseDuration };
```
