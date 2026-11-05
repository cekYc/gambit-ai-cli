import {ThreeCanvas} from "@remotion/three";
import {useThree} from "@react-three/fiber";
import {AbsoluteFill, useCurrentFrame} from "remotion";
import {Tas, Tur} from "./Taslar";
import {DROP, etki, kirp, v, VEZIR, VURUS, yumusak} from "./zaman";

// Vezir Gambiti: 1.d4 d5 2.c4 dxc4 3.Va4+ — son hamle ağır çekimde, şah çekişi drop'a denk gelir
type Hamle = {kim: string; hedef: string; bas: number; sure: number; alinan?: string};
const HAMLELER: Hamle[] = [
  {kim: "d2", hedef: "d4", bas: 0.5, sure: 0.5},
  {kim: "d7", hedef: "d5", bas: 2, sure: 0.5},
  {kim: "c2", hedef: "c4", bas: 3.5, sure: 0.5},
  {kim: "d7", hedef: "c4", bas: 5, sure: 0.5, alinan: "c2"},
  {kim: "d1", hedef: "a4", bas: VEZIR, sure: DROP - VEZIR},
];

const kare = (s: string): [number, number] => [s.charCodeAt(0) - 97, Number(s[1]) - 1];
const xz = (s: string): [number, number] => {
  const [f, r] = kare(s);
  return [f - 3.5, 3.5 - r];
};

const DIZILIS = ["r", "n", "b", "q", "k", "b", "n", "r"] as Tur[];
const TASLAR: {id: string; tur: Tur; beyaz: boolean}[] = [
  ...DIZILIS.map((t, i) => ({id: String.fromCharCode(97 + i) + "1", tur: t, beyaz: true})),
  ...DIZILIS.map((_, i) => ({id: String.fromCharCode(97 + i) + "2", tur: "p" as Tur, beyaz: true})),
  ...DIZILIS.map((_, i) => ({id: String.fromCharCode(97 + i) + "7", tur: "p" as Tur, beyaz: false})),
  ...DIZILIS.map((t, i) => ({id: String.fromCharCode(97 + i) + "8", tur: t, beyaz: false})),
];

/** Taşın karedeki konumu, yüksekliği ve alınıp alınmadığı */
const durum = (id: string, f: number) => {
  let [x, z] = xz(id);
  let y = 0;
  let alindi = 1; // 1 görünür, 0 alındı
  for (const h of HAMLELER) {
    const t = (f - v(h.bas)) / (h.sure * VURUS);
    if (h.alinan === id && t >= 1) alindi = Math.max(0, 1 - (t - 1) * 6);
    if (h.kim !== id || t < 0) continue;
    const e = h.sure > 1 ? 1 - Math.pow(1 - kirp(t), 3) : yumusak(t); // ağır çekim: sonda yavaşlayarak oturur
    const [hx, hz] = xz(h.hedef);
    x += (hx - x) * e;
    z += (hz - z) * e;
    y = Math.sin(Math.PI * kirp(t)) * (h.sure > 1 ? 1.2 : 0.5);
  }
  return {x, y, z, alindi};
};

const Kamera: React.FC = () => {
  const f = useCurrentFrame();
  const {camera} = useThree();
  // yavaş itme; vezir hamlesinde a4'e dönüp yaklaşır; drop'ta sarsılır
  const t = kirp(f / v(VEZIR));
  const vt = yumusak((f - v(VEZIR)) / ((DROP - VEZIR + 0.2) * VURUS));
  const [qx, qz] = xz("a4");
  const hedef = [qx * vt * 0.6, 0, qz * vt * 0.6];
  const s = etki(f) * 0.25;
  // dikey kadraj dar: tahtanın tamamı için uzaktan başlayıp yavaşça yaklaşır
  camera.position.set(hedef[0] + Math.sin(f * 1.7) * s, 14 - 2.5 * t - 4 * vt, 10 - 1.5 * t - 2.5 * vt + Math.cos(f * 2.3) * s);
  camera.lookAt(hedef[0], 0, hedef[2] + 0.4);
  return null;
};

export const Satranc: React.FC = () => {
  const f = useCurrentFrame();
  const sah = kirp((f - v(DROP)) / (0.2 * VURUS)) * Math.exp(-Math.max(0, f - v(DROP)) / (2 * VURUS));
  return (
    <AbsoluteFill>
      <ThreeCanvas width={1080} height={1920} camera={{fov: 56, position: [0, 14, 10]}} style={{background: "transparent"}}>
        <Kamera />
        <ambientLight intensity={0.35} />
        <directionalLight position={[3, 10, 6]} intensity={1.6} />
        <pointLight position={[-6, 3, -2]} intensity={60} color="#7c3aed" />
        <pointLight position={[6, 3, 2]} intensity={60} color="#06b6d4" />
        {/* tahta */}
        {Array.from({length: 64}, (_, i) => {
          const fi = i % 8, r = Math.floor(i / 8);
          const acik = (fi + r) % 2 === 1;
          return (
            <mesh key={i} position={[fi - 3.5, -0.05, 3.5 - r]}>
              <boxGeometry args={[1, 0.1, 1]} />
              <meshStandardMaterial color={acik ? "#2a2a40" : "#0d0d18"} roughness={0.5} metalness={0.3} />
            </mesh>
          );
        })}
        <mesh position={[0, -0.12, 0]}>
          <boxGeometry args={[8.4, 0.1, 8.4]} />
          <meshStandardMaterial color="#05050a" emissive="#7c3aed" emissiveIntensity={0.25 + etki(f) * 0.6} />
        </mesh>
        {TASLAR.map((p) => {
          const d = durum(p.id, f);
          if (d.alindi <= 0) return null;
          const vezir = p.id === "d1";
          const kara = p.id === "e8";
          return (
            <group key={p.id} position={[d.x, d.y, d.z]} scale={d.alindi}>
              <Tas tur={p.tur} beyaz={p.beyaz}
                isik={vezir ? "#38bdf8" : kara ? "#ef4444" : "#000000"}
                isikGucu={vezir ? 0.4 + etki(f) : kara ? sah * 3 : 0} />
            </group>
          );
        })}
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
