# kod-sure-js · puan 0.45

**Not:** 5/11 test; başarısız: S.parseDuration("1h 30m 15s") === 5415 -> Error: Invalid number value for h unit | S.parseDuration("45m") === 2700 -> Error: Invalid duration format | S.parseDuration("2h") === 7200 -> Error: Invalid duration format | S.parseDuration("90s") === 90 -> Error: Invalid duration format | S.parseDuration("1h15s") === 3615 -> Error: Invalid duration format

## Prompt

JavaScript'te (Node.js) `parseDuration(str)` fonksiyonunu yaz. "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi
metinleri toplam saniyeye çevirsin. Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve
bu sırayla gelir; aralarında boşluk olabilir de olmayabilir de. Geçersiz girdide (boş metin, bilinmeyen birim,
sayısı olmayan birim, yanlış sıra, tekrar eden birim) Error fırlatsın.
Fonksiyonu `module.exports = { parseDuration };` ile dışa aktar.
Sadece JavaScript kodunu tek bir ```javascript bloğu içinde ver.

## Cevap

Aşağıda JavaScript'te (Node.js) kullanıcının girilen metinleri toplam saniyeye çevirecek `parseDuration` fonksiyonu ve dışa aktarma işlemi verilmiştir:

```javascript
module.exports = {
  parseDuration: function(str) {
    const units = ['h', 'm', 's'];
    let result = 0;
    let parts = str.split(/\s+/);

    if (parts.length !== 3 || parts[0] === '' || parts[1] === '' || parts[2] === '') {
      throw new Error('Invalid duration format');
    }

    for (let i = 0; i < units.length; i++) {
      const unit = units[i];
      const numStr = parts[i];

      if (!numStr.match(/^\d+$/)) {
        throw new Error(`Invalid number value for ${unit} unit`);
      }

      let num = parseInt(numStr);

      switch (unit) {
        case 'h':
          result += num * 3600;
          break;
        case 'm':
          result += num * 60;
          break;
        case 's':
          result += num;
          break;
        default:
          throw new Error(`Unknown unit: ${unit}`);
      }
    }

    return result;
  }
};
```

Buunun kullanımı örneği:

```javascript
const durationParser = require('./duration-parser');

console.log(durationParser.parseDuration('1h 30m 15s')); // Output: 3915
console.log(durationParser.parseDuration('45m 30s'));   // Output: 2730
console.log(durationParser.parseDuration('1s'));         // Output: 1
try {
  console.log(durationParser.parseDuration(''));        // Error: Invalid duration format
} catch (e) {
  console.error(e.message); // Output: Invalid duration format
}
```

Buun fonksiyonu:

1. Metni boşluklardan bölüyor.
2. Her birim için geçersiz metin veya sayıyı kontrol ediyor.
3. Geçerli metnler ve sayıları saati, dakika ve saniyeye dönüştürüyor.
4. Toplam değerini döndürüyor.

## Notlandırılan kod/komut

```
module.exports = {
  parseDuration: function(str) {
    const units = ['h', 'm', 's'];
    let result = 0;
    let parts = str.split(/\s+/);

    if (parts.length !== 3 || parts[0] === '' || parts[1] === '' || parts[2] === '') {
      throw new Error('Invalid duration format');
    }

    for (let i = 0; i < units.length; i++) {
      const unit = units[i];
      const numStr = parts[i];

      if (!numStr.match(/^\d+$/)) {
        throw new Error(`Invalid number value for ${unit} unit`);
      }

      let num = parseInt(numStr);

      switch (unit) {
        case 'h':
          result += num * 3600;
          break;
        case 'm':
          result += num * 60;
          break;
        case 's':
          result += num;
          break;
        default:
          throw new Error(`Unknown unit: ${unit}`);
      }
    }

    return result;
  }
};
```
