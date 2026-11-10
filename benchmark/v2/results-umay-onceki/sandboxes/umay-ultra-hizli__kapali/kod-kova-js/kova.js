class TokenBucket {
  constructor({ capacity, refillPerSecond, now }) {
    // Validate capacity
    if (typeof capacity !== 'number' || !isFinite(capacity) || capacity <= 0) {
      throw new RangeError('capacity must be a positive finite number');
    }

    // Validate refillPerSecond
    if (typeof refillPerSecond !== 'number' || !isFinite(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError('refillPerSecond must be a non-negative finite number');
    }

    this._capacity = capacity;
    this._refillPerSecond = refillPerSecond;
    this._now = now || Date.now;

    this._tokens = capacity; // Start full
    this._lastRefillTime = this._now();
    this._maxTimeSeen = this._now();
  }

  _refill() {
    const now = this._now();

    // Check if time went backward
    if (now < this._maxTimeSeen) {
      // Time went backward, don't add or remove tokens
      // The max time reference remains as the greatest seen so far
      return;
    }

    // Calculate elapsed time in seconds
    const elapsedMs = now - this._lastRefillTime;
    const elapsedSeconds = elapsedMs / 1000;

    // Add tokens up to capacity
    const addTokens = elapsedSeconds * this._refillPerSecond;
    this._tokens = Math.min(this._capacity, this._tokens + addTokens);

    // Update last refill time
    this._lastRefillTime = now;
    // Update max time seen
    if (now > this._maxTimeSeen) {
      this._maxTimeSeen = now;
    }
  }

  tryTake(n = 1) {
    // Validate n must be a positive finite number
    if (typeof n !== 'number' || !isFinite(n) || n <= 0) {
      throw new RangeError('n must be a positive finite number');
    }

    // Refill first
    this._refill();

    if (this._tokens >= n) {
      this._tokens -= n;
      return true;
    }
    return false;
  }

  available() {
    this._refill();
    return this._tokens;
  }

  msUntil(n = 1) {
    // Validate n must be a positive finite number
    if (typeof n !== 'number' || !isFinite(n) || n <= 0) {
      throw new RangeError('n must be a positive finite number');
    }

    if (n > this._capacity) {
      return Infinity;
    }

    if (this._refillPerSecond === 0) {
      if (this._tokens >= n) {
        return 0;
      }
      return Infinity;
    }

    this._refill();

    if (this._tokens >= n) {
      return 0;
    }

    const needed = n - this._tokens;
    const secondsNeeded = needed / this._refillPerSecond;
    const msNeeded = secondsNeeded * 1000;

    // Round up to nearest integer
    return Math.ceil(msNeeded);
  }
}

module.exports = { TokenBucket };
