# kod-sure-js · puan 0.91

**Not:** 10/11 test; başarısız: S.parseDuration("1h 0m") === 3600 -> Error: Invalid unit value

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
  if (!str || typeof str !== 'string') {
    throw new Error('Invalid input');
  }

  const unitMap = {
    h: 3600,
    m: 60,
    s: 1
  };

  const pattern = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
  const match = str.match(pattern);

  if (!match) {
    throw new Error('Invalid format');
  }

  let totalSeconds = 0;
  const units = [];

  for (let i = 1; i < match.length; i++) {
    if (match[i]) {
      const unit = match[i].slice(-1);
      const value = parseInt(match[i].slice(0, -1));
      
      if (isNaN(value) || value <= 0) {
        throw new Error('Invalid unit value');
      }

      if (units.includes(unit)) {
        throw new Error('Duplicate unit');
      }

      units.push(unit);
      totalSeconds += value * unitMap[unit];
    }
  }

  // Kontrol: birimlerin sırası doğru mu?
  const orderedUnits = ['h', 'm', 's'];
  for (let i = 0; i < units.length - 1; i++) {
    if (orderedUnits.indexOf(units[i]) > orderedUnits.indexOf(units[i+1])) {
      throw new Error('Invalid unit order');
    }
  }

  return totalSeconds;
}

module.exports = { parseDuration };
```

## Notlandırılan kod/komut

```
function parseDuration(str) {
  if (!str || typeof str !== 'string') {
    throw new Error('Invalid input');
  }

  const unitMap = {
    h: 3600,
    m: 60,
    s: 1
  };

  const pattern = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
  const match = str.match(pattern);

  if (!match) {
    throw new Error('Invalid format');
  }

  let totalSeconds = 0;
  const units = [];

  for (let i = 1; i < match.length; i++) {
    if (match[i]) {
      const unit = match[i].slice(-1);
      const value = parseInt(match[i].slice(0, -1));
      
      if (isNaN(value) || value <= 0) {
        throw new Error('Invalid unit value');
      }

      if (units.includes(unit)) {
        throw new Error('Duplicate unit');
      }

      units.push(unit);
      totalSeconds += value * unitMap[unit];
    }
  }

  // Kontrol: birimlerin sırası doğru mu?
  const orderedUnits = ['h', 'm', 's'];
  for (let i = 0; i < units.length - 1; i++) {
    if (orderedUnits.indexOf(units[i]) > orderedUnits.indexOf(units[i+1])) {
      throw new Error('Invalid unit order');
    }
  }

  return totalSeconds;
}

module.exports = { parseDuration };
```
