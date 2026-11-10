function _isPosFinite(v) {
  return typeof v === 'number' && Number.isFinite(v) && v > 0;
}

class TokenBucket {
  constructor({ capacity, refillPerSecond, now }) {
    if (!_isPosFinite(capacity)) {
      throw new RangeError('capacity pozitif sonlu sayı olmalıdır');
    }
    if (typeof refillPerSecond !== 'number' || !Number.isFinite(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError('refillPerSecond pozitif veya sıfır bir sonlu sayı olmalıdır');
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this._now = typeof now === 'function' ? now : Date.now;

    // Kova dolu başlar
    this._tokens = capacity;
    this._lastRefillTime = this._now();
  }

  _refill() {
    const now = this._now();
    const last = this._lastRefillTime;

    // Saat geri giderse jeton eklenmez/çıkarılmaz; kaydı eski en büyük zamana tutar.
    if (now < last) {
      return;
    }

    const deltaMs = now - last;
    if (deltaMs <= 0 || this.refillPerSecond <= 0) {
      return;
    }

    const added = (deltaMs / 1000) * this.refillPerSecond;
    this._tokens = Math.min(this.capacity, this._tokens + added);
    this._lastRefillTime = now;
  }

  available() {
    this._refill();
    return this._tokens;
  }

  tryTake(n = 1) {
    if (!_isPosFinite(n)) {
      throw new RangeError('n pozitif sonlu sayı olmalıdır');
    }

    const avail = this.available();
    if (avail >= n) {
      this._tokens = avail - n;
      return true;
    }
    return false;
  }

  msUntil(n = 1) {
    if (!_isPosFinite(n)) {
      throw new RangeError('n pozitif sonlu sayı olmalıdır');
    }

    // n > capacity ise asla olamaz
    if (n > this.capacity) {
      return Infinity;
    }

    this._refill();
    const avail = this._tokens;
    if (avail >= n) {
      return 0;
    }

    const needed = n - avail;
    if (this.refillPerSecond <= 0) {
      return Infinity;
    }

    const ms = (needed / this.refillPerSecond) * 1000;
    return Math.ceil(ms);
  }
}

module.exports = { TokenBucket };
