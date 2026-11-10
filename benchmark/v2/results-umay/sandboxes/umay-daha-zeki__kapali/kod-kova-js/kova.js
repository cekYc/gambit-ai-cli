class TokenBucket {
  /**
   * @param {object} options
   * @param {number} options.capacity - Kovadaki maksimum jeton kapasitesi.
   * @param {number} options.refillPerSecond - Saniyede yenilenen jeton miktarı.
   * @param {function(): number} [options.now] - Milisaniye döndüren zaman fonksiyonu (varsayılan Date.now).
   */
  constructor(options) {
    if (typeof options.capacity !== 'number' || options.capacity <= 0 || !isFinite(options.capacity)) {
      throw new RangeError('Capacity must be a positive finite number.');
    }
    if (typeof options.refillPerSecond !== 'number' || options.refillPerSecond < 0 || !isFinite(options.refillPerSecond)) {
      throw new RangeError('RefillPerSecond must be a non-negative finite number.');
    }
    
    this.capacity = options.capacity;
    this.refillPerSecond = options.refillPerSecond;
    this.now = options.now || Date.now;
    
    // Kova dolu başlar
    this.tokens = this.capacity;
    
    // Son dolumun gerçekleştiği zamanı izler (saat geriye gitmeyi engellemek için)
    this.lastRefillTime = this.now(); 
  }

  /**
   * Belirli bir zamana göre jeton miktarını günceller.
   * @private
   */
  refill() {
    const now = this.now();
    const timeElapsedMs = now - this.lastRefillTime;

    // Saat geriye gitmişse dolum yapılmaz.
    if (timeElapsedMs <= 0) {
      return;
    }

    // Geçen süreye göre yenilenmesi gereken jeton miktarı
    // (ms / 1000) * refillPerSecond
    const refillAmount = (timeElapsedMs / 1000) * this.refillPerSecond;
    
    // Yeni jeton miktarı, kapasiteyi geçmeyecek şekilde güncellenir
    this.tokens = Math.min(this.capacity, this.tokens + refillAmount);
    
    // Son dolum zamanını güncelliyoruz
    this.lastRefillTime = now;
  }

  /**
   * Mevcut jeton sayısını (kesirli) döndürür.
   * @returns {number}
   */
  available() {
    this.refill(); // Güncel durumu hesapla
    return this.tokens;
  }

  /**
   * Belirtilen miktarda jeton almayı dener.
   * @param {number} [n=1] - Alınacak jeton miktarı.
   * @returns {boolean} - Başarılıysa true, değilse false.
   */
  tryTake(n = 1) {
    if (typeof n !== 'number' || n <= 0 || !isFinite(n)) {
      throw new RangeError('n must be a positive finite number.');
    }
    
    // Önce yenilemeyi yap, mevcut jeton sayısını al
    this.refill();

    if (this.tokens >= n) {
      this.tokens -= n;
      return true;
    } else {
      // Yetersiz jeton varsa hiçbir şey düşülmez
      return false;
    }
  }

  /**
   * n jetonun kullanılabilir olmasına gereken süreyi milisaniye cinsinden hesaplar.
   * @param {number} [n=1] - Gereken jeton miktarı.
   * @returns {number} - Gerekli süre (ms) veya Infinity.
   */
  msUntil(n = 1) {
    if (typeof n !== 'number' || n <= 0 || !isFinite(n)) {
      throw new RangeError('n must be a positive finite number.');
    }

    this.refill();

    if (this.tokens >= n) {
      return 0; // Yeterli jeton var
    }

    if (this.refillPerSecond <= 0 || n > this.capacity) {
      return Infinity; // Yenilenme yok veya istek kapasiteyi aşıyor
    }

    // İhtiyaç duyulan ek jeton miktarı
    const neededTokens = n - this.tokens;
    
    // Gerekli süre (ms) = (İhtiyaç duyulan jeton / Yenilenme hızı) * 1000
    const requiredTimeMs = (neededTokens / this.refillPerSecond) * 1000;

    // Yukarı yuvarlanmış tam sayı olarak döndürülmeli
    return Math.ceil(requiredTimeMs);
  }
}

module.exports = { TokenBucket };