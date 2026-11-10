const { TokenBucket } = require('./kova.js');
let pass = 0, fail = 0;
function check(name, cond) { if (cond) { pass++; console.log('PASS:', name); } else { fail++; console.log('FAIL:', name); } }

// 1. dolu başlar
const b1 = new TokenBucket({ capacity: 10, refillPerSecond: 5 });
check('dolu baslar', b1.available() === 10);

// 2. zamanla kesirli dolum, kapasite sınırı
let t = 1000;
const b2 = new TokenBucket({ capacity: 10, refillPerSecond: 10, now: () => t });
b2.tryTake(10);
check('bosaltildi', b2.available() === 0);
t += 500;
check('kesirli dolum', Math.abs(b2.available() - 5) < 1e-9);
t += 500;
check('kapasite siniri', b2.available() === 10);
t += 1000;
check('asiri dolum yok', b2.available() === 10);

// 3. tryTake
const b3 = new TokenBucket({ capacity: 5, refillPerSecond: 0, now: () => 0 });
check('tryTake true', b3.tryTake(3) === true);
check('kalan 2', b3.available() === 2);
check('tryTake false yetersiz', b3.tryTake(3) === false);
check('hiç düşmeden false', b3.available() === 2);

// 4. saat geri gider
const b4 = new TokenBucket({ capacity: 10, refillPerSecond: 100, now: () => t });
b4.tryTake(10);
t += 1000;
check('doldu', b4.available() === 10);
t = 500;
t += 10;
check('geri gittiğinde ekleme yok', b4.available() === 10);

// 5. available refill
const b5 = new TokenBucket({ capacity: 10, refillPerSecond: 1000, now: () => t });
b5.tryTake(10);
t += 5;
check('available refill', Math.abs(b5.available() - 5) < 1e-9);
t += 1000;
check('available sonra dolu', b5.available() === 10);

// 6. msUntil - bağımsız saat
let t6 = 0;
const b6 = new TokenBucket({ capacity: 10, refillPerSecond: 10, now: () => t6 });
b6.tryTake(10);
check('msUntil simdi yetersiz', b6.msUntil(1) === 100);
t6 = 50;
check('msUntil 50ms sonra', b6.msUntil(1) === 50);
t6 = 100;
check('msUntil yeterliyse 0', b6.msUntil(1) === 0);
check('msUntil n>capacity Infinity', b6.msUntil(11) === Infinity);

const b7 = new TokenBucket({ capacity: 5, refillPerSecond: 0, now: () => t6 });
b7.tryTake(5);
check('msUntil refill 0 ve yetersiz Infinity', b7.msUntil(1) === Infinity);

// 7. RangeError
const expectRange = (fn) => { try { fn(); return false; } catch (e) { return e instanceof RangeError; } };
check('capacity negatif RangeError', expectRange(() => new TokenBucket({ capacity: -1, refillPerSecond: 1 })));
check('capacity sıfır RangeError', expectRange(() => new TokenBucket({ capacity: 0, refillPerSecond: 1 })));
check('capacity Infinity RangeError', expectRange(() => new TokenBucket({ capacity: Infinity, refillPerSecond: 1 })));
check('capacity NaN RangeError', expectRange(() => new TokenBucket({ capacity: NaN, refillPerSecond: 1 })));
check('capacity string RangeError', expectRange(() => new TokenBucket({ capacity: '5', refillPerSecond: 1 })));
check('refill negatif RangeError', expectRange(() => new TokenBucket({ capacity: 5, refillPerSecond: -1 })));
check('refill string RangeError', expectRange(() => new TokenBucket({ capacity: 5, refillPerSecond: 'x' })));
check('refill NaN RangeError', expectRange(() => new TokenBucket({ capacity: 5, refillPerSecond: NaN })));
check('tryTake n sıfır RangeError', expectRange(() => b1.tryTake(0)));
check('tryTake n negatif RangeError', expectRange(() => b1.tryTake(-1)));
check('tryTake n Infinity RangeError', expectRange(() => b1.tryTake(Infinity)));
check('tryTake n string RangeError', expectRange(() => b1.tryTake('a')));
check('msUntil n sıfır RangeError', expectRange(() => b1.msUntil(0)));
check('msUntil n negatif RangeError', expectRange(() => b1.msUntil(-1)));
check('msUntil n string RangeError', expectRange(() => b1.msUntil('a')));

console.log('\nSonuç:', pass, 'geçti,', fail, 'başarısız.');
process.exit(fail > 0 ? 1 : 0);
