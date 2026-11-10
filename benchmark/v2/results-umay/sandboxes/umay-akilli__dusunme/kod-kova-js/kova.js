'use strict';

/**
 * TokenBucket implementation for rate limiting.
 * Tokens refill continuously at a fractional rate over time.
 */
class TokenBucket {
  /**
   * @param {Object} options
   * @param {number} options.capacity - Maximum number of tokens (positive finite)
   * @param {number} options.refillPerSecond - Tokens added per second (non-negative finite)
   * @param {Function} [options.now=Date.now] - Function returning current time in milliseconds
   */
  constructor({ capacity, refillPerSecond, now = Date.now }) {
    // Validate capacity
    if (!Number.isFinite(capacity) || capacity <= 0) {
      throw new RangeError('capacity must be a positive finite number');
    }
    
    // Validate refillPerSecond
    if (!Number.isFinite(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError('refillPerSecond must be a non-negative finite number');
    }
    
    // Validate now is a function
    if (typeof now !== 'function') {
      throw new RangeError('now must be a function');
    }

    this._capacity = capacity;
    this._refillPerSecond = refillPerSecond;
    this._now = now;
    
    // Bucket starts full
    this._tokens = capacity;
    // Track the largest time reference seen (for clock skew handling)
    this._lastRefillTime = now();
  }

  /**
   * Internal method to refill tokens based on elapsed time.
   * Handles clock going backwards by keeping the largest time reference.
   */
  _refill() {
    const now = this._now();
    
    // If clock went backwards, don't subtract tokens, just update lastRefillTime
    // to the larger value (which is already stored)
    if (now < this._lastRefillTime) {
      // Clock went backwards, keep the larger timestamp
      // No refill happens, tokens remain unchanged
      return;
    }
    
    const elapsedMs = now - this._lastRefillTime;
    if (elapsedMs > 0 && this._refillPerSecond > 0) {
      const elapsedSeconds = elapsedMs / 1000;
      const tokensToAdd = elapsedSeconds * this._refillPerSecond;
      this._tokens = Math.min(this._capacity, this._tokens + tokensToAdd);
    }
    
    this._lastRefillTime = now;
  }

  /**
   * Returns the current number of available tokens (can be fractional).
   * @returns {number}
   */
  available() {
    this._refill();
    return this._tokens;
  }

  /**
   * Attempts to take n tokens from the bucket.
   * @param {number} [n=1] - Number of tokens to take (positive finite)
   * @returns {boolean} - true if tokens were taken, false otherwise
   */
  tryTake(n = 1) {
    // Validate n
    if (!Number.isFinite(n) || n <= 0) {
      throw new RangeError('n must be a positive finite number');
    }
    
    this._refill();
    
    if (this._tokens >= n) {
      this._tokens -= n;
      return true;
    }
    
    return false;
  }

  /**
   * Returns milliseconds until n tokens are available (rounded up).
   * Returns 0 if enough tokens available now.
   * Returns Infinity if n > capacity or refillPerSecond is 0 and not enough tokens.
   * @param {number} [n=1] - Number of tokens needed (positive finite)
   * @returns {number}
   */
  msUntil(n = 1) {
    // Validate n
    if (!Number.isFinite(n) || n <= 0) {
      throw new RangeError('n must be a positive finite number');
    }
    
    // If n exceeds capacity, it will never be available
    if (n > this._capacity) {
      return Infinity;
    }
    
    this._refill();
    
    // If enough tokens now
    if (this._tokens >= n) {
      return 0;
    }
    
    // If no refill happening, will never get more tokens
    if (this._refillPerSecond <= 0) {
      return Infinity;
    }
    
    // Calculate time needed
    const tokensNeeded = n - this._tokens;
    const secondsNeeded = tokensNeeded / this._refillPerSecond;
    const msNeeded = secondsNeeded * 1000;
    
    // Round up to nearest millisecond
    return Math.ceil(msNeeded);
  }
}

module.exports = { TokenBucket };
