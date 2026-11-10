class TokenBucket {
  constructor({ capacity, refillPerSecond, now } = {}) {
    if (typeof capacity !== 'number' || !isFinite(capacity) || capacity <= 0) {
      throw new RangeError('capacity pozitif sonlu bir sayı olmalıdır');
    }
    if (typeof refillPerSecond !== 'number' || isNaN(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError('refillPerSecond sayı olmalı ve negatif olmamalıdır');
    }
    if (now !== undefined && typeof now !== 'function') {
      throw new TypeError('now bir fonksiyon olmalıdır');
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this._now = typeof now === 'function' ? now : Date.now;
    this._tokens = capacity; // kova dolu başlar
    this._lastTime = this._now(); // o ana kadar görülen en büyük zaman referansı
  }

  _refill(time) {
    // Saat geri giderse jeton eklenmez/çıkarılmaz; _lastTime en büyük referans kalır
    if (time < this._lastTime) {
      return;
    }
    const elapsedSeconds = (time - this._lastTime) / 1000;
    this._tokens = Math.min(this.capacity, this._tokens + elapsedSeconds * this.refillPerSecond);
    this._lastTime = time;
  }

  available() {
    this._refill(this._now());
    return this._tokens;
  }

  tryTake(n = 1) {
    if (typeof n !== 'number' || !isFinite(n) || n <= 0) {
      throw new RangeError('n pozitif sonlu bir sayı olmalıdır');
    }
    this._refill(this._now());
    if (this._tokens >= n) {
      this._tokens -= n;
      return true;
    }
    return false;
  }

  msUntil(n = 1) {
    if (typeof n !== 'number' || !isFinite(n) || n <= 0) {
      throw new RangeError('n pozitif sonlu bir sayı olmalıdır');
    }
    this._refill(this._now());

    if (this._tokens >= n) {
      return 0;
    }
    if (n > this.capacity) {
      return Infinity;
    }
    if (this.refillPerSecond <= 0) {
      return Infinity;
    }

    const needed = n - this._tokens;
    const ms = (needed / this.refillPerSecond) * 1000;
    return Math.ceil(ms);
  }
}

module.exports = { TokenBucket };
