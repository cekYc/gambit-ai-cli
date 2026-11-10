"use strict";

/**
 * Token bucket rate limiter (fractional, continuous refill).
 *
 * @param {object} opts
 * @param {number} opts.capacity - Positive finite number, bucket capacity.
 * @param {number} opts.refillPerSecond - Non-negative finite number, tokens per second.
 * @param {function} [opts.now] - Optional function returning current time in ms.
 *        Defaults to Date.now.
 */
function TokenBucket({ capacity, refillPerSecond, now }) {
  if (typeof capacity !== 'number' || !Number.isFinite(capacity) || capacity <= 0) {
    throw new RangeError("capacity must be a positive finite number");
  }
  if (typeof refillPerSecond !== 'number' || !Number.isFinite(refillPerSecond) || refillPerSecond < 0) {
    throw new RangeError("refillPerSecond must be a non-negative finite number");
  }

  this.capacity = capacity;
  this.refillPerSecond = refillPerSecond;
  this._now = typeof now === 'function' ? now : Date.now;

  const start = this._now();
  this._tokens = capacity;
  this._lastTime = start;
  this._maxTimeSeen = start;
}

/**
 * Refills tokens fractionally up to capacity based on elapsed time.
 * Time moving backward is ignored; _maxTimeSeen keeps the largest observed time.
 */
TokenBucket.prototype._refill = function () {
  const now = this._now();
  const effectiveTime = now > this._maxTimeSeen ? now : this._maxTimeSeen;
  const elapsedMs = effectiveTime - this._lastTime;

  if (elapsedMs > 0) {
    this._tokens = Math.min(
      this.capacity,
      this._tokens + (elapsedMs / 1000) * this.refillPerSecond
    );
  }

  this._lastTime = effectiveTime;
  this._maxTimeSeen = effectiveTime;
};

/**
 * Returns current available token count (fractional possible).
 */
TokenBucket.prototype.available = function () {
  this._refill();
  return this._tokens;
};

/**
 * Tries to take n tokens (default 1).
 * @param {number} [n=1]
 * @returns {boolean}
 */
TokenBucket.prototype.tryTake = function (n = 1) {
  if (typeof n !== 'number' || !Number.isFinite(n) || n <= 0) {
    throw new RangeError("n must be a positive finite number");
  }

  this._refill();
  if (this._tokens >= n) {
    this._tokens -= n;
    return true;
  }
  return false;
};

/**
 * Returns milliseconds until n tokens are available (ceiled integer).
 * @param {number} [n=1]
 * @returns {number} 0 if already available, Infinity if impossible.
 */
TokenBucket.prototype.msUntil = function (n = 1) {
  if (typeof n !== 'number' || !Number.isFinite(n) || n <= 0) {
    throw new RangeError("n must be a positive finite number");
  }

  if (n > this.capacity) {
    return Infinity;
  }

  const current = this.available(); // refills
  if (current >= n) {
    return 0;
  }

  if (this.refillPerSecond <= 0) {
    return Infinity;
  }

  const deficit = n - current;
  const msNeeded = (deficit / this.refillPerSecond) * 1000;
  return Math.ceil(msNeeded);
};

module.exports = { TokenBucket };
