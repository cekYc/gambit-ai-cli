# okuma-olay-dongusu · puan 0.00

**Not:** beklenen 'A\nD\nF\nC\nE\nB', cevap 'A\nF\nD\nB\nC\nE'

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

text bloğu içinde ver:

```
A
F
D
B
C
E
```

## Notlandırılan kod/komut

```
A
F
D
B
C
E
```
