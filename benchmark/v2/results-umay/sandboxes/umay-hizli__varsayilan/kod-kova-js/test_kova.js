const { TokenBucket } = require('./kova.js');
function assert(cond, msg) { if (!cond) { console.error('FAIL:', msg); process.exit(1); } }

// 1) Temel başlangıç: dolu kova
let b = new TokenBucket({ capacity: 10, refillPerSecond: 5 });
assert(b.available() === 10, 'ilk available 10 olmalı');
assert(b.tryTake(1) === true, 'tryTake(1) true');
assert(Math.abs(b.available() - 9) < 1e-9, '9 jeton kaldı');
assert(b.tryTake(100) === false, 'yetersiz jeton false');
assert(Math.abs(b.available() - 9) < 1e-9, 'başarısız deneme sonrası değişmemeli');

// 2) Sürekli kesirli dolum
let t = 1000;
b = new TokenBucket({ capacity: 10, refillPerSecond: 10, now: () => t });
b.tryTake(10); // boşal
assert(Math.abs(b.available() - 0) < 1e-9, 'boş kova');
t += 500; // yarım saniye -> 5 jeton
assert(Math.abs(b.available() - 5) < 1e-9, 'yarım saniyede 5 jeton');

// 3) Kapasite sınırı
t = 0;
b = new TokenBucket({ capacity: 4, refillPerSecond: 1000, now: () => t });
t += 10000; // uzun süre, en fazla capacity'e kadar
assert(Math.abs(b.available() - 4) < 1e-9, 'kapasite sınırı');

// 4) Saat geri gider
t = 5000;
b = new TokenBucket({ capacity: 10, refillPerSecond: 10, now: () => t });
b.tryTake(10);
t += 1000; // 10 jeton dolu olmalı
assert(Math.abs(b.available() - 10) < 1e-9, '1 sn sonra dolu');
t = 4000; // geri git
assert(Math.abs(b.available() - 10) < 1e-9, 'geri gittiğinde değişmez');
t = 4001;
assert(Math.abs(b.available() - 10) < 1e-9, 'hala 10 (geri gelince kayıt kalır)');
t = 6000; // 4001'den itibaren 1999 ms ≈ 19.99 jeton ama cap 10
assert(Math.abs(b.available() - 10) < 1e-9, 'yine cap');

// 5) tryTake/msUntil n validasyonu
function expectRangeError(fn, msg) { try { fn(); return false; } catch (e) { return e instanceof RangeError; } }
assert(expectRangeError(() => b.tryTake(0)), 'n=0 RangeError');
assert(expectRangeError(() => b.tryTake(-1)), 'n=-1 RangeError');
assert(expectRangeError(() => b.tryTake(NaN)), 'n=NaN RangeError');
assert(expectRangeError(() => b.tryTake(Infinity)), 'n=Infinity RangeError');
assert(expectRangeError(() => b.msUntil(0)), 'msUntil(0) RangeError');

assert(expectRangeError(() => new TokenBucket({ capacity: 0, refillPerSecond: 1 })), 'capacity=0 RangeError');
assert(expectRangeError(() => new TokenBucket({ capacity: -1, refillPerSecond: 1 })), 'capacity=-1 RangeError');
assert(expectRangeError(() => new TokenBucket({ capacity: NaN, refillPerSecond: 1 })), 'capacity=NaN RangeError');
assert(expectRangeError(() => new TokenBucket({ capacity: Infinity, refillPerSecond: 1 })), 'capacity=Infinity RangeError');
assert(expectRangeError(() => new TokenBucket({ capacity: 1, refillPerSecond: -1 })), 'refill=-1 RangeError');
assert(expectRangeError(() => new TokenBucket({ capacity: 1, refillPerSecond: NaN })), 'refill=NaN RangeError');

// 6) msUntil
t = 0;
b = new TokenBucket({ capacity: 10, refillPerSecond: 10, now: () => t });
b.tryTake(10);
assert(b.msUntil(1) === 100, '1 jeton için 100 ms');
assert(b.msUntil(5) === 500, '5 jeton için 500 ms');
assert(b.msUntil(10) === 1000, '10 jeton için 1000 ms');
assert(b.msUntil(11) === Infinity, '11 > capacity => Infinity');

// refill hızı 0 ve yetmiyorsa Infinity
t = 0;
b = new TokenBucket({ capacity: 5, refillPerSecond: 0, now: () => t });
b.tryTake(5);
assert(b.available() === 0, 'refill 0 ile boş');
assert(b.msUntil(1) === Infinity, 'refill 0 ve jeton yok => Infinity');

// yeterliyse 0
t = 0;
b = new TokenBucket({ capacity: 5, refillPerSecond: 10, now: () => t });
assert(b.msUntil(3) === 0, 'zaten yeterliyse 0');

// 7) capacity validasyonu zaten yukarıda expectRangeError ile kontrol edildi

console.log('Tüm testler geçti');


console.log('Tüm testler geçti');
