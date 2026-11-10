class TokenBucket {
  constructor({
    capacity,
    refillPerSecond,
    now = Date.now()
  }) {
    // 1. Validation
    if (!Number.isFinite(capacity) || capacity <= 0) {
      throw new RangeError('Capacity must be a positive finite number.');
    }
    if (typeof refillPerSecond !== 'number' || refillPerSecond < 0) {
      throw new RangeError('Refill rate must be a non-negative number.');
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this.tokens = capacity; // Starts full
    this.lastRefillTime = now;
  }

  // Helper to calculate and update tokens based on elapsed time
  _refill() {
    const currentTime = Date.now(); // Use actual time if external 'now' was just for initialization
    const timeElapsedMs = currentTime - this.lastRefillTime;

    if (timeElapsedMs <= 0) {
      // Time has not moved forward or is the initial call
      return;
    }

    // Tokens added: (timeElapsedMs / 1000) * refillPerSecond
    const tokensToAdd = (timeElapsedMs / 1000) * this.refillPerSecond;
    
    this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    this.lastRefillTime = currentTime;
  }

  available() {
    // Ensure tokens are updated before reporting availability
    this._refill();
    return this.tokens;
  }

  tryTake(n = 1) {
    if (!Number.isFinite(n) || n <= 0) {
      throw new RangeError('Token count (n) must be a positive finite number.');
    }
    
    this._refill();

    if (this.tokens >= n) {
      this.tokens -= n;
      return true;
    } else {
      return false;
    }
  }

  msUntil(n = 1) {
    if (!Number.isFinite(n) || n <= 0) {
      throw new RangeError('Token count (n) must be a positive finite number.');
    }
    
    this._refill();

    if (n > this.capacity || this.refillPerSecond === 0) {
      return Infinity;
    }

    // Required tokens to reach 'n'
    const neededTokens = Math.max(0, n - this.tokens);
    
    // Time required (in seconds) = neededTokens / refillPerSecond
    const timeRequiredSeconds = neededTokens / this.refillPerSecond;
    
    // Convert to milliseconds and ceiling (as requested)
    const msNeeded = Math.ceil(timeRequiredSeconds * 1000);
    
    // If already available, msUntil is 0
    return msNeeded > 0 ? msNeeded : 0;
  }
}

module.exports = { TokenBucket };