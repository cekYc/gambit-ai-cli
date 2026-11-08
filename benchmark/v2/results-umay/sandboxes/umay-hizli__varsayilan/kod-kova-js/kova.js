'use strict';

function _isPositiveFinite(value) {
  return typeof value === 'number' && isFinite(value) && value > 0;
}

function _isNonNegativeFinite(value) {
  return typeof value === 'number' && isFinite(value) && value >= 0;
}

class TokenBucket {
  constructor({ capacity, refillPerSecond, now } = {}) {
    if (!_isPositiveFinite(capacity)) {
      throw new RangeError('capacity must be a positive finite number');
    }
    if (!_isNonNegativeFinite(refillPerSecond)) {
      throw new RangeError('refillPerSecond must be a non-negative finite number');
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this.nowFn = typeof now === 'function' ? now : Date.now;
    this.tokens = capacity;
    this.lastTime = this.nowFn();
  }

  _refill() {
    const current = this.nowFn();
    if (current >= this.lastTime) {
      const elapsedMs = current - this.lastTime;
      this.tokens = Math.min(
        this.capacity,
        this.tokens + (elapsedMs / 1000) * this.refillPerSecond
      );
      this.lastTime = current;
    }
    // Saat geri giderse jeton eklenmez/çıkarılmaz ve o ana kadar görülen
    // en büyük zaman referans (lastTime) korunur.
  }

  available() {
    this._refill();
    return this.tokens;
  }

  tryTake(n = 1) {
    if (!_isPositiveFinite(n)) {
      throw new RangeError('n must be a positive finite number');
    }
    this._refill();
    if (this.tokens >= n) {
      this.tokens -= n;
      return true;
    }
    return false;
  }

  msUntil(n = 1) {
    if (!_isPositiveFinite(n)) {
      throw new RangeError('n must be a positive finite number');
    }
    this._refill();
    if (this.tokens >= n) {
      return 0;
    }
    if (n > this.capacity) {
      return Infinity;
    }
    if (this.refillPerSecond <= 0) {
      return Infinity;
    }
    const needed = n - this.tokens;
    const ms = (needed / this.refillPerSecond) * 1000;
    return Math.ceil(ms);
  }
}

module.exports = { TokenBucket };
