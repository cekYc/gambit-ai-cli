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
function parseDuration(str) {
  if (typeof str !== 'string' || str === '') {
    throw new Error('Invalid input: empty or non-string');
  }

  let totalSeconds = 0;
  const units = ['h', 'm', 's'];
  let lastUnitIndex = -1;

  // Her parçayı (sayı + birim) yakalamak için regex
  const parts = str.match(/(\d+)([hms])/g);

  if (!parts || parts.length === 0) {
    throw new Error('Invalid duration format');
  }

  for (let i = 0; i < parts.length; i++) {
    const [valueStr, unit] = parts[i].match(/(\d+)([hms])/)[1]; // regex is applied per matched substring for safety in the loop context via match(..g) and re-run or direct split on digits
    // The above line needs careful handling with the g flag: instead of nested regex, use a structured approach
  }

  // Reimplementing clearly without ambiguity from .match() groups
  totalSeconds = 0;
  let lastUnitSeen = -1;
  const unitOrder = ['h', 'm', 's'];

  parts.forEach((part) => {
    const match = part.match(/^(\d+)([hms])$/);
    if (!match) throw new Error(`Invalid component: ${part}`);

    const value = parseInt(match[1], 10);
    const unit = match[2];
    const currentIndex = unitOrder.indexOf(unit);

    // Check order and repetition
    if (currentIndex <= lastUnitSeen) {
      throw new Error(`Invalid sequence or repeated unit at ${part}`);
    }

    switch (unit) {
      case 'h': totalSeconds += value * 3600; break;
      case 'm': totalSeconds += value * 60; break;
      case 's': totalSeconds += value; break;
    }
    lastUnitSeen = currentIndex;
  });

  // Ensure every unit appeared at most once and order is preserved by the lastUnitSeen check
  return totalSeconds;
}

module.exports = { parseDuration };
```

## Notlandırılan kod/komut

```
function parseDuration(str) {
  if (typeof str !== 'string' || str === '') {
    throw new Error('Invalid input: empty or non-string');
  }

  let totalSeconds = 0;
  const units = ['h', 'm', 's'];
  let lastUnitIndex = -1;

  // Her parçayı (sayı + birim) yakalamak için regex
  const parts = str.match(/(\d+)([hms])/g);

  if (!parts || parts.length === 0) {
    throw new Error('Invalid duration format');
  }

  for (let i = 0; i < parts.length; i++) {
    const [valueStr, unit] = parts[i].match(/(\d+)([hms])/)[1]; // regex is applied per matched substring for safety in the loop context via match(..g) and re-run or direct split on digits
    // The above line needs careful handling with the g flag: instead of nested regex, use a structured approach
  }

  // Reimplementing clearly without ambiguity from .match() groups
  totalSeconds = 0;
  let lastUnitSeen = -1;
  const unitOrder = ['h', 'm', 's'];

  parts.forEach((part) => {
    const match = part.match(/^(\d+)([hms])$/);
    if (!match) throw new Error(`Invalid component: ${part}`);

    const value = parseInt(match[1], 10);
    const unit = match[2];
    const currentIndex = unitOrder.indexOf(unit);

    // Check order and repetition
    if (currentIndex <= lastUnitSeen) {
      throw new Error(`Invalid sequence or repeated unit at ${part}`);
    }

    switch (unit) {
      case 'h': totalSeconds += value * 3600; break;
      case 'm': totalSeconds += value * 60; break;
      case 's': totalSeconds += value; break;
    }
    lastUnitSeen = currentIndex;
  });

  // Ensure every unit appeared at most once and order is preserved by the lastUnitSeen check
  return totalSeconds;
}

module.exports = { parseDuration };
```
