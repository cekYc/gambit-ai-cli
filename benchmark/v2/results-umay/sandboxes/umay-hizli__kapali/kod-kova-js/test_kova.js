const { TokenBucket } = require('./kova.js');
let t = 0;
const b = new TokenBucket({ capacity: 10, refillPerSecond: 10, now: () => t });
console.log('avail', b.available());
console.log('take10', b.tryTake(10));
console.log('take1', b.tryTake(1));
t += 500;
console.log('avail500ms', b.available());
console.log('msUntil1', b.msUntil(1));
t += 1000;
console.log('msUntil1after1s', b.msUntil(1));
console.log('backwards', (() => { t -= 1000; return b.available(); })());
try { new TokenBucket({ capacity: 0, refillPerSecond: 1 }); } catch (e) { console.log('err cap', e.name); }
try { new TokenBucket({ capacity: 10, refillPerSecond: -1 }); } catch (e) { console.log('err refill', e.name); }
try { b.tryTake(0); } catch (e) { console.log('err take0', e.name); }
console.log('inf n>cap', b.msUntil(11));
console.log('inf no refill', (() => { const b2 = new TokenBucket({ capacity: 5, refillPerSecond: 0, now: () => 0 }); b2.tryTake(5); return b2.msUntil(1); })());
