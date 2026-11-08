class TokenBucket {
  constructor({ capacity, refillPerSecond, now = Date.now }) {
    if (typeof capacity !== 'number' || !Number.isFinite(capacity) || capacity <= 0) {
      throw new RangeError('capacity must be a positive finite number');
    }
    if (typeof refillPerSecond !== 'number' || !Number.isFinite(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError('refillPerSecond must be a non-negative finite number');
    }
    if (typeof now !== 'function') {
      throw new RangeError('now must be a function');
    }

    this._capacity = capacity;
    this._refillPerSecond = refillPerSecond;
    this._now = now;
    this._tokens = capacity;
    this._lastRefillTime = now();
  }

  _refill() {
    const now = this._now();
    if (now < this._lastRefillTime) {
      return;
    }
    const elapsedSeconds = (now - this._lastRefillTime) / 1000;
    const addedTokens = elapsedSeconds * this._refillPerSecond;
    this._tokens = Math.min(this._capacity, this._tokens + addedTokens);
    this._lastRefillTime = now;
  }

  _validateN(n) {
    if (typeof n !== 'number' || !Number.isFinite(n) || n <= 0 || !Number.isInteger(n)) {
      throw new RangeError('n must be a positive finite integer');
    }
  }

  tryTake(n = 1) {
    this._validateN(n);
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
    this._validateN(n);
    this._refill();

    if (n > this._capacity) {
      return Infinity;
    }
    if (this._tokens >= n) {
      return 0;
    }
    if (this._refillPerSecond === 0) {
      return Infinity;
    }

    const neededTokens = n - this._tokens;
    const secondsNeeded = neededTokens / this._refillPerSecond;
    return Math.ceil(secondsNeeded * 1000);
  }
}

module.exports = { TokenBucket };