'use strict';

class TokenBucket {
  constructor({ capacity, refillPerSecond, now } = {}) {
    if (
      typeof capacity !== 'number' ||
      !Number.isFinite(capacity) ||
      capacity <= 0
    ) {
      throw new RangeError('capacity pozitif bir sonlu sayı olmalıdır');
    }
    if (
      typeof refillPerSecond !== 'number' ||
      !Number.isFinite(refillPerSecond) ||
      refillPerSecond < 0
    ) {
      throw new RangeError('refillPerSecond negatif olmayan bir sonlu sayı olmalıdır');
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this.now = typeof now === 'function' ? now : Date.now;

    const start = this.now();
    this._tokens = capacity; // kova dolu başlar
    this._last = start;      // görülen en büyük zaman referansı
  }

  _sync() {
    const t = this.now();
    // Saat geri gitmezse ve ileri giderse sadece o kadar dolum yapılır.
    // Geri giden saatte jeton eklenmez/çıkarılmaz ve _last (max referans) güncellenmez.
    if (t > this._last) {
      const elapsed = t - this._last;
      this._tokens = Math.min(
        this.capacity,
        this._tokens + (elapsed * this.refillPerSecond) / 1000
      );
      this._last = t;
    }
    return this._tokens;
  }

  available() {
    this._sync();
    return this._tokens;
  }

  tryTake(n = 1) {
    if (typeof n !== 'number' || !Number.isFinite(n) || n <= 0) {
      throw new RangeError('n pozitif bir sonlu sayı olmalıdır');
    }
    this._sync();
    if (this._tokens >= n) {
      this._tokens -= n;
      return true;
    }
    return false;
  }

  msUntil(n = 1) {
    if (typeof n !== 'number' || !Number.isFinite(n) || n <= 0) {
      throw new RangeError('n pozitif bir sonlu sayı olmalıdır');
    }
    this._sync();

    if (this._tokens >= n) return 0;
    if (n > this.capacity) return Infinity;
    if (this.refillPerSecond <= 0) return Infinity;

    const needed = n - this._tokens;
    const ms = (needed * 1000) / this.refillPerSecond;
    return Math.ceil(ms);
  }
}

module.exports = { TokenBucket };
