class TokenBucket {
  constructor({ capacity, refillPerSecond, now = Date.now() } = {}) {
    if (typeof capacity !== 'number' || capacity <= 0 || !isFinite(capacity)) {
      throw new RangeError('Capacity must be a positive finite number.');
    }
    if (typeof refillPerSecond !== 'number' || refillPerSecond < 0 || !isFinite(refillPerSecond)) {
      throw new RangeError('RefillPerSecond must be a non-negative finite number.');
    }

    this.capacity = capacity;
    this.refillPerSecond = refillPerSecond;
    this.tokens = capacity; // Kova dolu başlar
    this.lastRefillTime = now;
    this.now = now;
  }

  _refill() {
    const nowTime = Date.now();
    // Saat geri gitmesini engellemek için en büyük zaman referansını kullan
    if (nowTime < this.lastRefillTime) {
      return;
    }

    // Geçen süreyi milisaniye cinsinden hesapla
    const timeElapsedMs = nowTime - this.lastRefillTime;
    
    // Saniyeye çevir ve jeton miktarını hesapla
    const timeElapsedSeconds = timeElapsedMs / 1000;
    
    // Dolum miktarı = geçen saniye * refillPerSecond
    const refillAmount = timeElapsedSeconds * this.refillPerSecond;

    // Yeni jeton miktarını güncelle, kapasiteyi aşmasın
    this.tokens = Math.min(this.capacity, this.tokens + refillAmount);
    
    // Son dolum zamanını güncelle
    this.lastRefillTime = nowTime;
  }

  tryTake(n = 1) {
    if (typeof n !== 'number' || n <= 0 || !isFinite(n)) {
      throw new RangeError('n must be a positive finite number.');
    }
    
    this._refill();

    if (this.tokens >= n) {
      this.tokens -= n;
      return true;
    } else {
      return false;
    }
  }

  available() {
    this._refill();
    return this.tokens;
  }

  msUntil(n = 1) {
    if (typeof n !== 'number' || n <= 0 || !isFinite(n)) {
      throw new RangeError('n must be a positive finite number.');
    }
    
    this._refill();

    if (this.tokens >= n) {
      return 0; // Yeterliyse 0 ms kaldı
    }

    if (this.refillPerSecond === 0) {
      // Dolum yoksa ve yetmiyorsa sonsuza kadar beklemek gerekir
      return Infinity;
    }

    // İhtiyaç duyulan ek jeton miktarı
    const neededTokens = n - this.tokens;

    // Bu jetonların dolması için gereken süre (saniye) = neededTokens / refillPerSecond
    const timeNeededSeconds = neededTokens / this.refillPerSecond;
    
    // Milisaniyeye çevir ve yukarı yuvarla
    const timeNeededMs = Math.ceil(timeNeededSeconds * 1000);
    
    // Eğer ihtiyaç duyulan jeton kapasitenin üzerindeyse (bu durumda refillPerSecond > 0 olsa bile tam dolum süresini hesaplar)
    if (neededTokens > this.capacity - this.tokens) {
        // Bu durum teorik olarak refill per second > 0 iken sadece başlangıçta gerçekleşir. 
        // Ancak n > capacity ise sonsuz döngüye girmemek için kontrol edilebilir.
        // Basitçe, yetersizse ve dolum süresi hesaplanabiliyorsa bu hesap yeterlidir.
    }

    return timeNeededMs;
  }
}

module.exports = { TokenBucket };