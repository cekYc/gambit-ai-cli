from datetime import date, timedelta

def artik_yil(y):
    """Miladi takvimde artık yıl mı: 4'e bölünen yıllar; ancak 100'e bölünüp 400'e bölünmeyenler değil."""
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

def ay_sonu(y, m):
    """y yılının m. ayının (1-12) son günü."""
    # Liste 0'dan 11'e kadar ayları temsil eder.
    gunler = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if artik_yil(y):
        gunler[1] = 29
    return gunler[m - 1]

def ay_ekle(d, n):
    """d tarihine n ay ekler (n negatif olabilir). Gün yeni ayda yoksa ayın son gününe çekilir: 31 Ocak 2024 + 1 ay = 29 Şubat 2024."""
    # Ay ve yıl taşmasını doğru yönetmek için matematiksel düzeltme yapıldı.
    month_sum = d.month + n
    year_add = (month_sum - 1) // 12
    new_month = (month_sum - 1) % 12 + 1
    new_year = d.year + year_add
    
    # Ay sonunda olmayan bir gün isteniyorsa, o ayın son gününü döndür.
    return date(new_year, new_month, min(d.day, ay_sonu(new_year, new_month)))

def is_gunu_say(bas, bit):
    """bas ve bit DAHİL aradaki hafta içi (Pzt-Cum) günlerin sayısı; bas > bit ise 0."""
    if bas > bit:
        return 0
    
    gun = 0
    d = bas
    # DAHİL olması gerektiği için <= kullanıldı.
    while d <= bit:
        if d.weekday() < 5: # Pazartesi (0) - Cuma (4)
            gun += 1
        d += timedelta(days=1)
    return gun
