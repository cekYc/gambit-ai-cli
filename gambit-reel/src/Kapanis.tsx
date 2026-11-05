import {ThreeCanvas} from "@remotion/three";
import {AbsoluteFill, spring, useCurrentFrame} from "remotion";
import {Tas, Tur} from "./Taslar";
import {MODELLER} from "./veri";
import {etki, FPS, LOGO, SAHNE, v} from "./zaman";

const TURLER: Tur[] = ["b", "q", "k"];

export const Kapanis: React.FC = () => {
  const f = useCurrentFrame();
  const d = f - v(SAHNE.kapanis[0]);
  const e = etki(f);
  const logo = spring({frame: f - v(LOGO), fps: FPS, config: {damping: 10, stiffness: 160}});
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{top: 420, height: 760}}>
        <ThreeCanvas width={1080} height={760} camera={{fov: 30, position: [0, 2.4, 10.5]}}>
          <ambientLight intensity={0.45} />
          <directionalLight position={[2, 6, 6]} intensity={1.6} />
          {MODELLER.map((m, k) => {
            const g = spring({frame: d - k * 6, fps: FPS, config: {damping: 11, stiffness: 150}});
            return (
              <group key={m.ad} position={[(k - 1) * 3, -1.4 + (1 - g) * -4, 0]} scale={1.3 + (k === 2 ? 0.2 : 0)}
                rotation={[0, f * 0.012 + k, 0]}>
                <Tas tur={TURLER[k]} beyaz isik={m.renk} isikGucu={0.5 + e} />
                <pointLight position={[0, 1, 1.5]} intensity={10 + e * 25} color={m.renk} />
              </group>
            );
          })}
        </ThreeCanvas>
      </AbsoluteFill>
      <div style={{position: "absolute", top: 1180, width: "100%", display: "flex", justifyContent: "space-around", padding: "0 60px",
        boxSizing: "border-box"}}>
        {MODELLER.map((m, k) => {
          const g = spring({frame: d - 8 - k * 6, fps: FPS, config: {damping: 12, stiffness: 180}});
          return (
            <div key={m.ad} style={{textAlign: "center", transform: `translateY(${(1 - g) * 80}px)`, opacity: g}}>
              <div style={{fontFamily: "Arial Black, Impact, sans-serif", fontSize: 92, color: "#fff",
                textShadow: `0 0 30px ${m.renk}`}}>{m.genel.toFixed(1).replace(".", ",")}</div>
              <div style={{fontFamily: "Arial, sans-serif", fontSize: 32, letterSpacing: 6, color: m.renk, fontWeight: 700}}>
                {m.ad.toUpperCase()}</div>
            </div>
          );
        })}
      </div>
      <div style={{position: "absolute", top: 160, width: "100%", textAlign: "center", transform: `scale(${0.6 + 0.4 * logo})`,
        opacity: logo}}>
        <div style={{fontFamily: "Arial Black, Impact, sans-serif", fontSize: 190, color: "#fff", letterSpacing: 14,
          textShadow: `${e * 18}px 0 #ff2bd6, ${-e * 18}px 0 #00f0ff, 0 0 60px #7c3aed`}}>GAMBIT</div>
        <div style={{fontFamily: "Arial, sans-serif", fontSize: 36, letterSpacing: 10, color: "rgba(255,255,255,0.7)"}}>
          YEREL YAPAY ZEKÂ · TAHTA SENİN</div>
      </div>
      <div style={{position: "absolute", bottom: 120, width: "100%", textAlign: "center", fontFamily: "Arial, sans-serif",
        fontSize: 26, letterSpacing: 6, color: "rgba(255,255,255,0.45)", opacity: logo}}>
        GAMBIT BENCH · 39 GÖREV · ZORLUK AĞIRLIKLI SKOR</div>
    </AbsoluteFill>
  );
};
