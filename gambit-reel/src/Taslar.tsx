import {useMemo} from "react";
import * as THREE from "three";

// Satranç taşları: tornalanmış (lathe) profiller; birim = bir kare
export type Tur = "p" | "r" | "n" | "b" | "q" | "k";

const P = (pts: [number, number][]) => pts.map(([x, y]) => new THREE.Vector2(x, y));
const TABAN: [number, number][] = [[0, 0], [0.38, 0], [0.38, 0.06], [0.32, 0.1], [0.3, 0.14], [0.22, 0.18]];

const PROFIL: Record<Exclude<Tur, "n">, THREE.Vector2[]> = {
  p: P([...TABAN, [0.13, 0.42], [0.18, 0.46], [0.12, 0.5], [0.17, 0.56], [0.19, 0.64], [0.16, 0.72], [0.08, 0.77], [0, 0.78]]),
  r: P([...TABAN, [0.2, 0.5], [0.27, 0.56], [0.27, 0.74], [0.18, 0.74], [0.18, 0.68], [0, 0.68]]),
  b: P([...TABAN, [0.12, 0.6], [0.2, 0.64], [0.12, 0.68], [0.17, 0.78], [0.18, 0.88], [0.12, 0.98], [0.05, 1.04], [0.07, 1.08], [0, 1.12]]),
  q: P([...TABAN, [0.13, 0.72], [0.22, 0.76], [0.14, 0.8], [0.2, 0.96], [0.26, 1.06], [0.2, 1.1], [0.12, 1.12], [0.08, 1.17], [0, 1.18]]),
  k: P([...TABAN, [0.14, 0.78], [0.23, 0.82], [0.15, 0.86], [0.2, 1.0], [0.24, 1.08], [0.15, 1.12], [0, 1.13]]),
};

export const Tas: React.FC<{
  tur: Tur;
  beyaz: boolean;
  isik?: string; // vurgu rengi (kendinden ışık)
  isikGucu?: number;
  opaklik?: number;
}> = ({tur, beyaz, isik = "#000000", isikGucu = 0, opaklik = 1}) => {
  const geo = useMemo(() => (tur === "n" ? null : new THREE.LatheGeometry(PROFIL[tur], 40)), [tur]);
  const renk = beyaz ? "#e9e7f2" : "#1a1a24";
  const mat = (
    <meshStandardMaterial color={renk} roughness={beyaz ? 0.28 : 0.35} metalness={beyaz ? 0.15 : 0.55}
      emissive={isik} emissiveIntensity={isikGucu} transparent={opaklik < 1} opacity={opaklik} />
  );
  if (tur === "n") {
    // at: gövde + eğik baş + burun (basit ama okunur bir siluet)
    const yon = beyaz ? 1 : -1;
    return (
      <group>
        <mesh geometry={useMemo(() => new THREE.LatheGeometry(P([...TABAN, [0.2, 0.42], [0, 0.42]]), 40), [])}>{mat}</mesh>
        <mesh position={[0, 0.62, 0.02 * yon]} rotation={[-0.35 * yon, 0, 0]}><boxGeometry args={[0.26, 0.48, 0.3]} />{mat}</mesh>
        <mesh position={[0, 0.78, -0.16 * yon]} rotation={[0.5 * yon, 0, 0]}><boxGeometry args={[0.22, 0.2, 0.34]} />{mat}</mesh>
        <mesh position={[0, 0.92, 0.06 * yon]}><boxGeometry args={[0.08, 0.12, 0.1]} />{mat}</mesh>
      </group>
    );
  }
  return (
    <group>
      <mesh geometry={geo!}>{mat}</mesh>
      {tur === "k" && (
        <>
          <mesh position={[0, 1.24, 0]}><boxGeometry args={[0.06, 0.22, 0.06]} />{mat}</mesh>
          <mesh position={[0, 1.26, 0]}><boxGeometry args={[0.18, 0.06, 0.06]} />{mat}</mesh>
        </>
      )}
      {tur === "q" && [0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <mesh key={i} position={[Math.cos((i / 8) * Math.PI * 2) * 0.2, 1.1, Math.sin((i / 8) * Math.PI * 2) * 0.2]}>
          <sphereGeometry args={[0.035, 12, 12]} />{mat}
        </mesh>
      ))}
      {tur === "b" && (
        <mesh position={[0.06, 0.95, 0]} rotation={[0, 0, 0.6]}><boxGeometry args={[0.02, 0.14, 0.2]} />
          <meshStandardMaterial color="#000000" />
        </mesh>
      )}
    </group>
  );
};
