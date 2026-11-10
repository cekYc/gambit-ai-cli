const { TokenBucket } = require('./kova.js');
let pass = 0, fail = 0;
function assert(cond, msg) {
  if (cond) { pass++; }
  else { fail++; console.error('FAIL:', msg); }
}
function approx(a, b, eps=1e-6) { return Math.abs(a - b) <= eps; }

// 1. Default now, full bucket
let tb = new TokenBucket({ capacity: 10, refillPerSecond: 5 });
assert(approx(tb.available(), 10), 'starts full');
assert(tb.tryTake(1) === true, 'tryTake 1 ok');
assert(approx(tb.available(), 9), 'after take 1');
assert(tb.tryTake(100) === false, 'tryTake too many returns false');
assert(approx(tb.available(), 9), 'tryTake too many does not change');

// 2. Fake clock refill fractional
t0 = 1000;
tb = new TokenBucket({ capacity: 10, refillPerSecond: 10, now: () => t0 });
assert(approx(tb.available(), 10), 'fake clock starts full');
tb.tryTake(10);
assert(approx(tb.available(), 0), 'after take 10 empty');
t0 += 500; // half second, 5 tokens/sec refill -> 5 tokens
assert(approx(tb.available(), 5), 'refill half second');
assert(tb.tryTake(5) === true, 'tryTake 5 after refill');
assert(approx(tb.available(), 0), 'empty again');

// 3. capacity clamp
t0 += 1000; // would refill 10 but capacity 10
tb = new TokenBucket({ capacity: 4, refillPerSecond: 100, now: () => t0 });
tb.tryTake(4);
t0 += 1000;
assert(approx(tb.available(), 4), 'clamped at capacity');

// 4. time backward ignored
t0 = 5000;
tb = new TokenBucket({ capacity: 10, refillPerSecond: 1000, now: () => t0 });
tb.tryTake(10);
assert(approx(tb.available(), 0), 'empty');
t0 -= 1000; // go backward
assert(approx(tb.available(), 0), 'backward time no tokens');
t0 += 2000; // now 7000, +2000ms from maxTimeSeen 5000 -> 2000 tokens clamped to 10
assert(approx(tb.available(), 10), 'after backward then forward clamped');

// 5. msUntil
t0 = 0;
tb = new TokenBucket({ capacity: 10, refillPerSecond: 10, now: () => t0 });
tb.tryTake(10);
assert(tb.msUntil(1) === 100, 'msUntil 1 token @10 tok/s = 100ms');
assert(tb.msUntil(10) === 1000, 'msUntil 10 tokens = 1000ms');
assert(tb.msUntil(11) === Infinity, 'n > capacity => Infinity');
assert(tb.msUntil(1) === 100, 'msUntil does not consume');
assert(approx(tb.available(), 0), 'available unchanged after msUntil');

tb2 = new TokenBucket({ capacity: 5, refillPerSecond: 0, now: () => t0 });
tb2.tryTake(5);
assert(tb2.msUntil(1) === Infinity, 'refill 0 and empty => Infinity');

// 6. validation
function expectRange(fn) { try { fn(); return false; } catch (e) { return e instanceof RangeError; } }
assert(expectRange(() => new TokenBucket({ capacity: 0, refillPerSecond: 1 })), 'capacity 0 RangeError');
assert(expectRange(() => new TokenBucket({ capacity: -1, refillPerSecond: 1 })), 'capacity neg RangeError');
assert(expectRange(() => new TokenBucket({ capacity: Infinity, refillPerSecond: 1 })), 'capacity Infinity RangeError');
assert(expectRange(() => new TokenBucket({ capacity: '10', refillPerSecond: 1 })), 'capacity string RangeError');
assert(expectRange(() => new TokenBucket({ capacity: 10, refillPerSecond: -1 })), 'refill neg RangeError');
assert(expectRange(() => new TokenBucket({ capacity: 10, refillPerSecond: NaN })), 'refill NaN RangeError');
assert(expectRange(() => new TokenBucket({ capacity: 10, refillPerSecond: '5' })), 'refill string RangeError');
tb = new TokenBucket({ capacity: 10, refillPerSecond: 1 });
assert(expectRange(() => tb.tryTake(0)), 'tryTake 0 RangeError');
assert(expectRange(() => tb.tryTake(-1)), 'tryTake -1 RangeError');
assert(expectRange(() => tb.tryTake(Infinity)), 'tryTake Infinity RangeError');
assert(expectRange(() => tb.tryTake('1')), 'tryTake string RangeError');
assert(expectRange(() => tb.msUntil(0)), 'msUntil 0 RangeError');
assert(expectRange(() => tb.msUntil(-1)), 'msUntil -1 RangeError');
assert(expectRange(() => tb.msUntil('2')), 'msUntil string RangeError');

// 7. tryTake default n=1
tb = new TokenBucket({ capacity: 1, refillPerSecond: 0 });
assert(tb.tryTake() === true, 'default n=1');
assert(tb.available() === 0, 'after default take empty');

console.log('pass:', pass, 'fail:', fail);
process.exit(fail > 0 ? 1 : 0);
