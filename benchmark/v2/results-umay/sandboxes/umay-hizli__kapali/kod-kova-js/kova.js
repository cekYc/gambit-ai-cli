class TokenBucket {
  constructor({ capacity, refillPerSecond, now }) {
    if (typeof capacity !== "number" || !Number.isFinite(capacity) || capacity <= 0) {
      throw new RangeError("capacity pozitif sonlu sayı olmalıdır");
    }
    if (typeof refillPerSecond !== "number" || !Number.isFinite(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError("refillPerSecond negatif olmayan bir sayı olmalıdır");
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this.now = typeof now === "function" ? now : Date.now;

    this.tokens = capacity;
    this.lastRefill = this.now();
  }

  _refill(now) {
    if (now < this.lastRefill) {
      return;
    }

    const elapsed = (now - this.lastRefill) / 1000;
    const added = elapsed * this.refillPerSecond;
    this.tokens = Math.min(this.capacity, this.tokens + added);
    this.lastRefill = now;
  }

  tryTake(n = 1) {
    if (typeof n !== "number" || !Number.isFinite(n) || n <= 0) {
      throw new RangeError("n pozitif sonlu sayı olmalıdır");
    }

    const now = this.now();
    this._refill(now);

    if (this.tokens >= n) {
      this.tokens -= n;
      return true;
    }
    return false;
  }

  available() {
    const now = this.now();
    this._refill(now);
    return this.tokens;
  }

  msUntil(n = 1) {
    if (typeof n !== "number" || !Number.isFinite(n) || n <= 0) {
      throw new RangeError("n pozitif sonlu sayı olmalıdır");
    }

    const now = this.now();
    this._refill(now);

    if (this.tokens >= n) {
      return 0;
    }

    if (this.refillPerSecond <= 0 || n > this.capacity) {
      return Infinity;
    }

    const missing = n - this.tokens;
    const ms = (missing / this.refillPerSecond) * 1000;
    return Math.ceil(ms);
  }
}

module.exports = { TokenBucket };
