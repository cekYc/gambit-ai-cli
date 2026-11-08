'use strict';

class TokenBucket {
  /**
   * @param {Object} options
   * @param {number} options.capacity - Maksimum jeton kapasitesi (pozitif sonlu sayı)
   * @param {number} options.refillPerSecond - Saniyede eklenen jeton sayısı (negatif olamaz, sonlu sayı)
   * @param {Function} [options.now=Date.now] - Milisaniye cinsinden zaman döndüren fonksiyon
   */
  constructor({ capacity, refillPerSecond, now = Date.now }) {
    if (!Number.isFinite(capacity) || capacity <= 0) {
      throw new RangeError('capacity pozitif sonlu bir sayı olmalıdır');
    }
    if (!Number.isFinite(refillPerSecond) || refillPerSecond < 0) {
      throw new RangeError('refillPerSecond negatif olamaz ve sonlu bir sayı olmalıdır');
    }
    if (typeof now !== 'function') {
      throw new RangeError('now bir fonksiyon olmalıdır');
    }

    this._capacity = capacity;
    this._refillPerSecond = refillPerSecond;
    this._now = now;
    this._tokens = capacity; // Kova dolu başlar
    this._lastRefillTime = now(); // En büyük görülen zaman referansı
  }

  /**
   * İç dolum hesaplaması - zaman ilerledikçe jeton ekler
   * Saat geri giderse _lastRefillTime güncellenmez (en büyük zaman kalır)
   */
  _refill() {
    const now = this._now();
    if (now > this._lastRefillTime) {
      const elapsedSeconds = (now - this._lastRefillTime) / 1000;
      const addedTokens = elapsedSeconds * this._refillPerSecond;
      this._tokens = Math.min(this._capacity, this._tokens + addedTokens);
      this._lastRefillTime = now;
    }
    // now <= _lastRefillTime ise saat geri gitmiş, hiçbir şey yapma
  }

  /**
   * Mevcut jeton sayısını döner (kesirli olabilir)
   * @returns {number}
   */
  available() {
    this._refill();
    return this._tokens;
  }

  /**
   * n jeton almayı dener
   * @param {number} [n=1] - Alınacak jeton sayısı (pozitif sonlu sayı)
   * @returns {boolean} - Yeterli jeton varsa true, yoksa false (jeton düşmez)
   */
  tryTake(n = 1) {
    if (!Number.isFinite(n) || n <= 0) {
      throw new RangeError('n pozitif sonlu bir sayı olmalıdır');
    }
    this._refill();
    if (this._tokens >= n) {
      this._tokens -= n;
      return true;
    }
    return false;
  }

  /**
   * n jetonun kullanılabilir olmasına kadar geçecek milisaniye (yukarı yuvarlanmış)
   * @param {number} [n=1] - Beklenen jeton sayısı (pozitif sonlu sayı)
   * @returns {number} - Milisaniye (tam sayı), yeterliyse 0, asla olmazsa Infinity
   */
  msUntil(n = 1) {
    if (!Number.isFinite(n) || n <= 0) {
      throw new RangeError('n pozitif sonlu bir sayı olmalıdır');
    }
    if (n > this._capacity) {
      return Infinity;
    }
    this._refill();
    if (this._tokens >= n) {
      return 0;
    }
    if (this._refillPerSecond === 0) {
      return Infinity;
    }
    const needed = n - this._tokens;
    const secondsNeeded = needed / this._refillPerSecond;
    return Math.ceil(secondsNeeded * 1000);
  }
}

module.exports = { TokenBucket };
