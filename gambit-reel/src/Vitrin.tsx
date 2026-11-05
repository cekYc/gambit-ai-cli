import {ThreeCanvas} from "@remotion/three";
import {AbsoluteFill, spring, useCurrentFrame} from "remotion";
import {Radar} from "./Radar";
import {Tas, Tur} from "./Taslar";
import {MODELLER} from "./veri";
import {etki, FPS, gurultu, kirp, SAHNE, v} from "./zaman";

const TURLER: Tur[] = ["b", "q", "k"];
const GECIS = [SAHNE.bishop[0], SAHNE.queen[0], SAHNE.king[0]];
const SIFIR = MODELLER[0].kategoriler.map(() => 0);

/** Kare anında hangi model öne çıkıyor ve geçişin yay (spring) ilerlemesi */
const asama = (f: number) => {
  const i = Math.max(0, GECIS.filter((g) => f >= v(g)).length - 1);
  const d = f - v(GECIS[i]);
  return {i, d};
};
// hafif aşan yay: değerler hedefi biraz geçip geri oturur (büyüyüp küçülme hissi)
const yay = (d: number) => spring({frame: d, fps: FPS, config: {damping: 9, stiffness: 140, mass: 0.7}});

export const Vitrin: React.FC = () => {
  const f = useCurrentFrame();
  const {i, d} = asama(f);
  const m = MODELLER[i];
  const once = i === 0 ? SIFIR : MODELLER[i - 1].kategoriler;
  // eksenler sırayla (dalga gibi) yeni değere akar
  const degerler = m.kategoriler.map((x, k) => once[k] + (x - once[k]) * yay(d - k * 1.6));
  const oncekiGenel = i === 0 ? 0 : MODELLER[i - 1].genel;
  const genel = oncekiGenel + (m.genel - oncekiGenel) * yay(d);
  const giris = spring({frame: d, fps: FPS, config: {damping: 12, stiffness: 200}});
  const e = etki(f);
  const kay = e * 22; // renk kayması (glitch) miktarı
  const isimOlcek = 1.7 - 0.7 * giris;

  return (
    <AbsoluteFill>
      {/* üstte üç taş yan yana: sırası gelen öne çıkar ve döner */}
      <AbsoluteFill style={{top: 70, height: 640}}>
        <ThreeCanvas width={1080} height={640} camera={{fov: 30, position: [0, 2.2, 9.5]}}>
          <ambientLight intensity={0.4} />
          <directionalLight position={[2, 6, 6]} intensity={1.5} />
          {MODELLER.map((mm, k) => {
            const aktif = k === i;
            const s = aktif ? 1.25 + 0.25 * giris + e * 0.1 : 0.95;
            const don = aktif ? (f - v(GECIS[i])) * 0.02 + (1 - giris) * 2 : (f * 0.004 + k);
            return (
              <group key={mm.ad} position={[(k - 1) * 2.9, -1.1 + (aktif ? 0.15 : 0), 0]} scale={s} rotation={[0, don, 0]}>
                <Tas tur={TURLER[k]} beyaz isik={mm.renk} isikGucu={aktif ? 0.55 + e * 1.2 : 0.02} opaklik={aktif ? 1 : 0.4} />
                <pointLight position={[0, 1, 1.4]} intensity={aktif ? 8 + e * 30 : 0} color={mm.renk} />
              </group>
            );
          })}
        </ThreeCanvas>
      </AbsoluteFill>

      {/* taşın adı */}
      <div style={{position: "absolute", top: 710, width: "100%", textAlign: "center"}}>
        <div style={{fontFamily: "Arial Black, Impact, sans-serif", fontSize: 150, fontWeight: 900, lineHeight: 1,
          color: "#fff", letterSpacing: 6, transform: `scale(${isimOlcek}) translateX(${gurultu(f, 3) * kay}px)`,
          textShadow: `${kay}px 0 #ff2bd6, ${-kay}px 0 #00f0ff, 0 0 40px ${m.renk}`}}>
          {m.ad.toUpperCase()}
        </div>
      </div>

      {/* radar ve ortasında genel skor */}
      <div style={{position: "absolute", top: 870, left: 40, width: 1000, height: 1000}}>
        <Radar degerler={degerler} renk={m.renk} boyut={1000} parlama={e} yaziOpak={kirp(giris * 1.5)} />
        <div style={{position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center",
          justifyContent: "center", pointerEvents: "none"}}>
          <div style={{fontFamily: "Arial Black, Impact, sans-serif", fontSize: 150, fontWeight: 900, color: "#fff",
            textShadow: `0 0 30px ${m.renk}, 0 0 80px ${m.renk}, 0 6px 0 rgba(0,0,0,0.6)`,
            transform: `scale(${1 + e * 0.12})`}}>{genel.toFixed(1).replace(".", ",")}</div>
          <div style={{fontFamily: "Arial, sans-serif", fontSize: 30, letterSpacing: 10, color: "rgba(255,255,255,0.7)",
            marginTop: -10}}>GENEL SKOR</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
