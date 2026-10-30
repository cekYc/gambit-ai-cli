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

## Düşünme

Goal: determine the exact output of the provided JavaScript snippet (Node.js environment).

Code analysis:
1. `console.log("A")` → synchronous, prints immediately.
2. `setTimeout(..., 0)` → schedules "B" in a Macrotask; it will run after all current sync code and microtasks.
3. `Promise.resolve().then(...)` → adds "C" to the Microtask queue (next_tick/promise).
4. Async IIFE: `console.log("D")` is inside the function body — synchronous before first await; prints immediately after F's sync part? No, it runs as soon as its block is reached in the main flow. So D → E (after microtask resumption) → F. Wait, async functions run synchronously until the first await.
   - Execution order: A -> D [async body before first await] -> F [main continue after IIFE synchronous part] -> ... resumed...
5. `await null` in async IIFE resumes as a Microtask (same priority as promise .then).

Step-by-step execution flow:
Sync phase of main script: "A", then the async block starts → prints "D", then F is reached in main thread → print "F".
Microtask checkpoint after sync finishes.
Next microtasks are Promise then ("C") and resumed async IIFE ("E"). Order depends on registration order: "C" was registered first, so it runs before "E".
Macrotask phase: setTimeout fires → "B".

Full sequence: A (sync), D (async-sync), F (main sync continue), C (microtask 1), E (microtask 2 - after await resume), B (macrotask).

Edge cases: Node.js promises/settimeout behavior is standard here; no hidden side effects or complex dependencies between tasks.

Final output string: A\nD\nF\nC\nE\nB


## Cevap

A
D
F
C
E
B

## Notlandırılan kod/komut

```
A
D
F
C
E
B
```
