from datetime import date, timedelta

def artik_yil(y):
    """Miladi takvimde artık yıl mı: 4'e bölünen yıllar; ancak 100'e bölünüp 400'e bölünmeyenler değil."""
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

def ay_sonu(y, m):
    """y yılının m. ayının (1-12) son günü."""
    gunler = [31, 29 if artik_yil(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return gunler[m]

def ay_ekle(d, n):
    """d tarihine n ay ekler (n negatif olabilir). Gün yeni ayda yoksa ayın son gününe çekilir:
31 Ocak 2024 + 1 ay = 29 Şubat 2024."""
    total_months = d.year * 12 + d.month - 1 + n
    y = total_months // 12
    m = total_months % 12 + 1
    return date(y, m, min(d.day, ay_sonu(y, m)))

def is_gunu_say(bas, bit):
    """bas ve bit DAHİL aradaki hafta içi (Pzt-Cum) günlerin sayısı; bas > bit ise 0."""
    if bas > bit:
        return 0
    
    gun = 0
    d = bas
    while d <= bit:
        if d.weekday() < 5:
            gun += 1
        d += timedelta(days=1)
    return gun