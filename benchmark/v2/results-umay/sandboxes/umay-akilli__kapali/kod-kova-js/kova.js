class TokenBucket {
  constructor({ capacity, refillPerSecond, now = Date.now }) {
    if (!Number.isFinite(capacity) || capacity <= 0) {
      throw new RangeError('capacity must be a positive finite number');
    }
    if (!Number.isFinite(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError('refillPerSecond must be a non-negative finite number');
    }
    if (typeof now !== 'function') {
      throw new RangeError('now must be a function');
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this.now = now;
    this.tokens = capacity;
    this.lastRefill = now();
  }

  _refill() {
    const now = this.now();
    if (now < this.lastRefill) {
      return;
    }
    const elapsedSeconds = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsedSeconds * this.refillPerSecond);
    this.lastRefill = now;
  }

  tryTake(n = 1) {
    if (!Number.isFinite(n) || n <= 0) {
      throw new RangeError('n must be a positive finite number');
    }
    this._refill();
    if (this.tokens >= n) {
      this.tokens -= n;
      return true;
    }
    return false;
  }

  available() {
    this._refill();
    return this.tokens;
  }

  msUntil(n = 1) {
    if (!Number.isFinite(n) || n <= 0) {
      throw new RangeError('n must be a positive finite number');
    }
    if (n > this.capacity) {
      return Infinity;
    }
    this._refill();
    if (this.tokens >= n) {
      return 0;
    }
    if (this.refillPerSecond === 0) {
      return Infinity;
    }
    const needed = n - this.tokens;
    const secondsNeeded = needed / this.refillPerSecond;
    return Math.ceil(secondsNeeded * 1000);
  }
}

module.exports = { TokenBucket };