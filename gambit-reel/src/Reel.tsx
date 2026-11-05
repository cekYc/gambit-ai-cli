import {AbsoluteFill, Audio, spring, staticFile, useCurrentFrame} from "remotion";
import {Kapanis} from "./Kapanis";
import {Satranc} from "./Satranc";
import {Vitrin} from "./Vitrin";
import {DROP, etki, flas, FPS, gurultu, kirp, nabiz, SAHNE, v, VEZIR, VURUS} from "./zaman";

// Sahneler mutlak kareyle seçilir (Sequence kullanılmaz): bütün zamanlama zaman.ts'teki vuruş çizelgesinden
const sahnede = (f: number, [a, b]: readonly [number, number]) => f >= v(a) && f < v(b);

const NOTASYON = [
  {at: 0.5, metin: "1. d4"}, {at: 2, metin: "d5"}, {at: 3.5, metin: "2. c4"}, {at: 5, metin: "dxc4"}, {at: VEZIR, metin: "3. Va4+!!"},
];

const SatrancYazilari: React.FC<{f: number}> = ({f}) => {
  const drop = spring({frame: f - v(DROP), fps: FPS, config: {damping: 8, stiffness: 220}});
  const kay = etki(f) * 26;
  return (
    <>
      <div style={{position: "absolute", top: 210, width: "100%", textAlign: "center", fontFamily: "Arial, sans-serif",
        fontSize: 34, letterSpacing: 12, color: "rgba(255,255,255,0.7)", opacity: kirp(f / VURUS)}}>
        VEZİR GAMBİTİ</div>
      <div style={{position: "absolute", top: 290, width: "100%", display: "flex", justifyContent: "center", gap: 30,
        opacity: 1 - kirp((f - v(DROP)) / (0.3 * VURUS))}}>
        {NOTASYON.map((n) => {
          const g = spring({frame: f - v(n.at), fps: FPS, config: {damping: 10, stiffness: 240}});
          const son = n.at === VEZIR;
          return (
            <div key={n.metin} style={{fontFamily: "Arial Black, Impact, sans-serif", fontSize: son ? 64 : 48,
              color: son ? "#38bdf8" : "#fff", opacity: g, transform: `translateY(${(1 - g) * 40}px) scale(${0.6 + 0.4 * g})`,
              textShadow: son ? "0 0 30px #38bdf8" : "0 0 18px rgba(124,58,237,0.8)"}}>{n.metin}</div>
          );
        })}
      </div>
      {f >= v(DROP) && (
        <div style={{position: "absolute", top: 700, width: "100%", textAlign: "center", padding: "40px 0",
          background: "linear-gradient(90deg, transparent, rgba(0,0,0,0.75) 20%, rgba(0,0,0,0.75) 80%, transparent)",
          transform: `scale(${2.4 - 1.4 * drop}) rotate(${(1 - drop) * -6}deg)`, opacity: kirp(drop * 2)}}>
          <div style={{fontFamily: "Arial Black, Impact, sans-serif", fontSize: 270, color: "#fff", letterSpacing: 8, lineHeight: 1,
            textShadow: `${kay}px 0 #ff2bd6, ${-kay}px 0 #00f0ff, 0 0 70px #38bdf8`}}>GAMBIT</div>
          <div style={{fontFamily: "Arial, sans-serif", fontSize: 40, letterSpacing: 14, color: "#fff", marginTop: 10}}>ŞAH.</div>
        </div>
      )}
    </>
  );
};

export const Reel: React.FC<{sesli?: boolean}> = ({sesli = true}) => {
  const f = useCurrentFrame();
  const e = etki(f) + nabiz(f);
  const sx = gurultu(f, 1) * e * 26, sy = gurultu(f, 2) * e * 26;
  const zoom = 1 + e * 0.05;
  const rot = gurultu(f, 4) * e * 0.8;
  const kay = Math.min(18, etki(f) * 16);
  const fl = flas(f);
  return (
    <AbsoluteFill style={{background: "radial-gradient(ellipse at 50% 35%, #1b1036 0%, #07060f 55%, #000 100%)", overflow: "hidden"}}>
      {/* şarkı: kullanıcının kendi kesitinden; zaman.ts'teki vuruş ızgarası bu kesite göre */}
      {sesli && <Audio src={staticFile("sarki.wav")} volume={0.5} />}
      <AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${zoom}) rotate(${rot}deg)`,
        filter: kay > 0.5 ? `drop-shadow(${kay}px 0 0 rgba(255,43,214,0.7)) drop-shadow(${-kay}px 0 0 rgba(0,240,255,0.7))` : undefined}}>
        {sahnede(f, SAHNE.satranc) && (
          <>
            <Satranc />
            <SatrancYazilari f={f} />
          </>
        )}
        {f >= v(SAHNE.bishop[0]) && f < v(SAHNE.kapanis[0]) && <Vitrin />}
        {f >= v(SAHNE.kapanis[0]) && <Kapanis />}
      </AbsoluteFill>
      {/* tarama çizgileri ve kenar kararması */}
      <AbsoluteFill style={{pointerEvents: "none", opacity: 0.18,
        background: "repeating-linear-gradient(0deg, rgba(0,0,0,0.9) 0px, rgba(0,0,0,0.9) 2px, transparent 2px, transparent 5px)"}} />
      <AbsoluteFill style={{pointerEvents: "none", background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.75) 100%)"}} />
      {/* büyük vuruşlarda beyaz flaş */}
      <AbsoluteFill style={{pointerEvents: "none", background: "#fff", opacity: fl * 0.85, mixBlendMode: "screen"}} />
    </AbsoluteFill>
  );
};
