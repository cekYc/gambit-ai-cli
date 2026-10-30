# okuma-olay-dongusu · puan 1.00

**Not:** doğru

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
E
B
```

## Notlandırılan kod/komut

```
A
D
F
C
E
B
```
