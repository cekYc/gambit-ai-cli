# okuma-olay-dongusu · puan 0.00

**Not:** beklenen 'A\nD\nF\nC\nE\nB', cevap 'A\nD\nF\nC\nB\nE'

## Prompt

Aşağıdaki JavaScript (Node.js) kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```javascript
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
(async () => {
  console.log("D");
  await null;
  console.log("E");
})();
console.log("F");
```

## Cevap

```text
A
D
F
C
B
E
```

**Adım adım çalışma mantığı:**
1. `console.log("A")` hemen çalışır: **A** yazdırılır.
2. `setTimeout(..., 0)` bir callback'i Task Queue (Macrotask) kuyruğuna atar.
3. `Promise.resolve().then(...)` bir callback'i Microtask Queue kuyruğuna atar.
4. `async` fonksiyon başlatılır:
   - `console.log("D")` hemen çalışır: **D** yazdırılır.
   - `await null` ifadesi, geri kalan kısmını (E) Microtask Queue'ya atar ve async fonksiyonun yürütülmesini durdurup ana akışa döner.
5. `console.log("F")` hemen çalışır: **F** yazdırılır.
6. Call Stack boşaldığında önce Microtask Queue kontrol edilir:
   - Promise callback'i çalışır: **C** yazdırılır.
   - `await` sonrası kalan async fonksiyon parçası çalışır: **E** yazdırılır.
7. Son olarak Macrotask Queue kontrol edilir:
   - `setTimeout` callback'i çalışır: **B** yazdırılır.

*Not: JavaScript motoruna ve Node.js versiyonuna göre Microtask önceliği nedeniyle C ve E'nin sırası (ikisi de microtask olduğu için) aynı anda kuyruğa girmelerine bağlı olarak değişebilir ancak standart bir Node.js ortamında sıralama yukarıdaki gibidir.*

## Notlandırılan kod/komut

```
A
D
F
C
B
E
```
