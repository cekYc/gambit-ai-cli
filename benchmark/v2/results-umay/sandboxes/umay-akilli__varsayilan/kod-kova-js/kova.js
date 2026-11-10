class TokenBucket {
  constructor({ capacity, refillPerSecond, now = Date.now }) {
    if (!Number.isFinite(capacity) || capacity <= 0) {
      throw new RangeError('capacity must be a positive finite number');
    }
    if (!Number.isFinite(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError('refillPerSecond must be a non-negative finite number');
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this.now = now;
    this.tokens = capacity;
    this.lastRefillTime = now();
    this.maxSeenTime = this.lastRefillTime;
  }

  _refill() {
    const currentTime = this.now();
    
    if (currentTime < this.maxSeenTime) {
      return;
    }
    
    const elapsedMs = currentTime - this.lastRefillTime;
    if (elapsedMs > 0) {
      const elapsedSeconds = elapsedMs / 1000;
      const tokensToAdd = elapsedSeconds * this.refillPerSecond;
      this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    }
    
    this.lastRefillTime = currentTime;
    this.maxSeenTime = currentTime;
  }

  tryTake(n = 1) {
    if (!Number.isFinite(n) || n <= 0 || !Number.isInteger(n)) {
      throw new RangeError('n must be a positive finite integer');
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
    if (!Number.isFinite(n) || n <= 0 || !Number.isInteger(n)) {
      throw new RangeError('n must be a positive finite integer');
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
    
    const neededTokens = n - this.tokens;
    const secondsNeeded = neededTokens / this.refillPerSecond;
    return Math.ceil(secondsNeeded * 1000);
  }
}

module.exports = { TokenBucket };
