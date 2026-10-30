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

*   `console.log("A");`: Synchronous operation. Prints "A" immediately.
    *   `setTimeout(() => console.log("B"), 0);`: Asynchronous (Macrotask). The callback is pushed to the Task Queue/Event Loop's timer phase. It will run after all current synchronous code and microtasks are finished.
    *   `Promise.resolve().then(() => console.log("C"));`: Microtask. The `.then()` callback is pushed to the Microtask Queue. It will run after the current execution context finishes but before the next Macrotask.
    *   `(async () => { ... })();`: An IIFE (Immediately Invoked Function Expression) that is `async`.
        *   `console.log("D");`: Synchronous inside the async function. Prints "D" immediately.
        *   `await null;`: This pauses the execution of this specific async function. The rest of the function (`console.log("E")`) is scheduled as a microtask to run after the current stack and other microtasks are cleared.
        *   `console.log("E");`: Scheduled as a microtask (after `await`).
    *   `console.log("F");`: Synchronous operation. Prints "F" immediately.

    1.  **Synchronous Execution Phase:**
        *   `console.log("A")` -> Output: **A**
        *   `setTimeout(...)` -> Scheduled (Macrotask)
        *   `Promise.resolve().then(...)` -> Scheduled (Microtask)
        *   Async IIFE starts:
            *   `console.log("D")` -> Output: **D**
            *   `await null` -> The rest of the function is scheduled as a Microtask.
        *   `console.log("F")` -> Output: **F**

    2.  **Microtask Queue Phase (after synchronous code finishes):**
        *   The microtask queue currently contains:
            1.  The `.then()` from `Promise.resolve()` (prints "C").
            2.  The remainder of the async IIFE after `await null` (prints "E").
        *   Execution order in Microtask Queue depends on when they were added.
            *   `Promise.resolve().then(...)` was added first. -> Output: **C**
            *   The code after `await null` was added second. -> Output: **E**

    3.  **Macrotask Queue Phase (after Microtask queue is empty):**
        *   The macrotask queue contains:
            1.  The `setTimeout` callback (prints "B").
        *   Execution order: -> Output: **B**

    1.  A (Sync)
    2.  D (Sync - inside async IIFE before await)
    3.  F (Sync)
    4.  C (Microtask - Promise)
    5.  E (Microtask - after await)
    6.  B (Macrotask - setTimeout)

    *   `console.log("A")` -> A
    *   `setTimeout(...)` -> Macrotask queue: [B]
    *   `Promise.resolve().then(...)` -> Microtask queue: [C]
    *   Async IIFE:
        *   `console.log("D")` -> D
        *   `await null` -> Microtask queue: [C, E]
    *   `console.log("F")` -> F

    Current Stack is empty.
    Microtasks: C, then E.
    Macrotasks: B.

    Order: A, D, F, C, E, B.

    Wait, let's re-verify the order of `C` and `E`.
    1. `Promise.resolve().then(...)` is called *before* the `await null` in the async function?
       Let's look at the code structure:
       ```javascript
       console.log("A"); // 1
       setTimeout(...); // Macrotask B
       Promise.resolve().then(...); // Microtask C
       (async () => {
         console.log("D"); // 2
         await null; // Schedules E as microtask
         console.log("E");
       })();
       console.log("F"); // 3
       ```

    Execution flow:
    - `A` is logged.
    - `setTimeout` (B) added to Macrotask queue.
    - `Promise.resolve().then` (C) added to Microtask queue.
    - Async function starts.
    - `D` is logged.
    - `await null` encountered. The rest of the async function (`E`) is pushed to the Microtask queue.
    - `F` is logged.

    Current state:
    Synchronous output so far: A, D, F.
    Microtask Queue: [C, E]
    Macrotask Queue: [B]

    Next step: Process all microtasks.
    - Pop C -> Log C.
    - Pop E -> Log E.

    Next step: Process macrotasks.
    - Pop B -> Log B.

    Final sequence: A, D, F, C, E, B.

    *   `A`: Sync (Yes)
    *   `D`: Sync inside async function before await (Yes)
    *   `F`: Sync (Yes)
    *   `C`: Microtask from Promise (Yes)
    *   `E`: Microtask from `await` (Yes)
    *   `B`: Macrotask from `setTimeout` (Yes)

    Wait, let's check the order of C and E again.
    Code:
    ```javascript
    Promise.resolve().then(() => console.log("C")); // Microtask 1 added here
    (async () => {
      console.log("D");
      await null; // Microtask 2 added here
      console.log("E");
    })();
    ```
    Yes, `C` is added to the microtask queue before `E`.

    Result:
    A
    D
    F
    C
    E
    B

    Wait, let me double check if there's any nuance with Node.js vs Browser regarding `await null`. In both, `await` wraps the remainder in a microtask.

    Let's re-trace:
    1. `console.log("A")` -> Output: A
    2. `setTimeout(B)` -> Macrotask Queue: [B]
    3. `Promise.resolve().then(C)` -> Microtask Queue: [C]
    4. Async IIFE starts:
       - `console.log("D")` -> Output: D
       - `await null` -> The rest of the function (E) is scheduled as a microtask. Microtask Queue: [C, E]
    5. `console.log("F")` -> Output: F

    Stack empty.
    Microtasks: C, then E.
    Macrotasks: B.

    Final order: A, D, F, C, E, B.

    Wait, let me check the code again to ensure I didn't miss anything.
    ```javascript
    console.log("A"); // 1
    setTimeout(() => console.log("B"), 0); // Macrotask: B
    Promise.resolve().then(() => console.log("C")); // Microtask: C
    (async () => {
      console.log("D"); // 2
      await null; // Microtask: E
      console.log("E");
    })();
    console.log("F"); // 3
    ```

    Sequence of execution:
    1. `A` (Sync)
    2. `setTimeout` scheduled.
    3. `Promise.then` scheduled.
    4. Async IIFE starts.
    5. `D` (Sync inside async).
    6. `await null` schedules the rest of the function as a microtask.
    7. `F` (Sync).

    Current output: A, D, F.
    Microtasks queue: [C, E].
    Macrotasks queue: [B].

    Process Microtasks:
    - C
    - E

    Process Macrotasks:
    - B

    Final sequence:
    A
    D
    F
    C
    E
    B

    Wait, let me re-read the code one more time.
    `console.log("A");` -> A
    `setTimeout(() => console.log("B"), 0);` -> B (Macrotask)
    `Promise.resolve().then(() => console.log("C"));` -> C (Microtask)
    `(async () => { ... })();`
      `console.log("D");` -> D
      `await null;` -> E (Microtask)
      `console.log("E");`
    `console.log("F");` -> F

    Yes, the order is A, D, F, C, E, B.

    Wait, let me check if `await null` behaves differently than `await Promise.resolve()`. No, it's essentially the same in terms of microtask scheduling. The execution of the async function is suspended and the remainder is put into the microtask queue.

    Let's double-check the order of C and E again.
    Line 4: `Promise.resolve().then(() => console.log("C"));` -> This adds "C" to the Microtask Queue.
    Line 5: The async function starts. It logs "D". Then it hits `await null`. At this point, the rest of the function (the part that logs "E") is added to the Microtask Queue.

    So the queue looks like: [C, E].
    Then synchronous code finishes with `F`.
    Then microtasks are processed: C, then E.
    Then macrotasks are processed: B.

    Final check of output format: "Sadece çıktıyı tek bir ```text bloğu içinde ver." (Only provide the output in a single ```text block).

    Output lines:
    A
    D
    F
    C
    E
    B

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
