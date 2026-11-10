const {siraylaIsle, tekrarDene, say, ortalama, grupla} = require('./islem.js');
(async()=>{
  // siraylaIsle: sirayla ve tek tek calismali
  const sureler=[];
  const r=await siraylaIsle([1,2,3], async x=>{
    const t=Date.now();
    await new Promise(res=>setTimeout(res, 50));
    sureler.push(Date.now()-t);
    return x*10;
  });
  console.log('siraylaIsle:', JSON.stringify(r), 'sureler:', JSON.stringify(sureler));

  // tekrarDene: 3 denemeden sonra son hatayi firlatmali
  try{
    await tekrarDene(async i=>{ throw new Error('hata '+i); }, 3);
    console.log('tekrarDene: HATA firlatilmedi!');
  }catch(e){ console.log('tekrarDene son hata:', e.message); }

  // tekrarDene: en fazla 3 deneme, 2. denemede basarili
  let c=0;
  const r2=await tekrarDene(async i=>{ c++; if(i<1) throw new Error('hata'); return 'ok'; }, 3);
  console.log('tekrarDene deneme sayisi:', c, 'sonuc:', r2);

  // say: dogru sayim
  console.log('say:', JSON.stringify(say(['a','b','a'])));

  // ortalama: bos dizi 0
  console.log('ortalama bos:', ortalama([]), 'dolu:', ortalama([2,4]));

  // grupla: siralama korunur
  console.log('grupla:', JSON.stringify(grupla([{v:1},{v:2},{v:1}], o=>o.v)));

  console.log('DOGRULAMA TAMAM');
})().catch(e=>{console.error(e);process.exitCode=1;});
