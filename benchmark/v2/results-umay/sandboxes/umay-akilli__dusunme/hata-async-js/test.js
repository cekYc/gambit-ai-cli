const assert = require("assert");
const { siraylaIsle, say, ortalama } = require("./islem.js");

(async () => {
  assert.deepStrictEqual(say(["a", "b", "a"]), { a: 2, b: 1 });
  assert.strictEqual(ortalama([2, 4]), 3);
  const r = await siraylaIsle([1, 2, 3], async (x) => x * 10);
  assert.deepStrictEqual(r, [10, 20, 30]);
  console.log("TÜM TESTLER GEÇTİ");
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
