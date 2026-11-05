import {KATEGORILER} from "./veri";

// Tek radar grafiği: değerler dışarıdan (geçişlerde bir modelden ötekine akarak) verilir
export const Radar: React.FC<{degerler: number[]; renk: string; boyut: number; parlama: number; yaziOpak: number}> = ({
  degerler, renk, boyut, parlama, yaziOpak,
}) => {
  const n = KATEGORILER.length;
  const m = boyut / 2;
  const R = boyut * 0.3;
  const nokta = (i: number, d: number) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    return [m + Math.cos(a) * R * d / 100, m + Math.sin(a) * R * d / 100];
  };
  const halka = (d: number) => KATEGORILER.map((_, i) => nokta(i, d).join(",")).join(" ");
  const sekil = degerler.map((d, i) => nokta(i, Math.max(0, d)).join(",")).join(" ");
  return (
    <svg width={boyut} height={boyut} viewBox={`0 0 ${boyut} ${boyut}`} style={{overflow: "visible"}}>
      <defs>
        <radialGradient id="dolgu">
          <stop offset="0%" stopColor={renk} stopOpacity={0.15} />
          <stop offset="100%" stopColor={renk} stopOpacity={0.55} />
        </radialGradient>
        <filter id="isik" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation={6 + parlama * 14} result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      {[25, 50, 75, 100].map((d) => (
        <polygon key={d} points={halka(d)} fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth={d === 100 ? 3 : 1.5}
          strokeDasharray={d === 50 ? "8 8" : undefined} />
      ))}
      {KATEGORILER.map((_, i) => {
        const [x, y] = nokta(i, 100);
        return <line key={i} x1={m} y1={m} x2={x} y2={y} stroke="rgba(255,255,255,0.1)" strokeWidth={1.5} />;
      })}
      <polygon points={sekil} fill="url(#dolgu)" stroke={renk} strokeWidth={6} strokeLinejoin="round" filter="url(#isik)" />
      {degerler.map((d, i) => {
        const [x, y] = nokta(i, Math.max(0, d));
        return <circle key={i} cx={x} cy={y} r={9} fill="#fff" stroke={renk} strokeWidth={5} />;
      })}
      {KATEGORILER.map((k, i) => {
        const [x, y] = nokta(i, 128);
        const sag = x > m + 10, sol = x < m - 10;
        return (
          <g key={k} opacity={yaziOpak}>
            <text x={x} y={y} textAnchor={sag ? "start" : sol ? "end" : "middle"} dominantBaseline="middle"
              fill="rgba(255,255,255,0.75)" fontSize={28} fontWeight={700} fontFamily="Arial Black, Arial, sans-serif"
              letterSpacing={1}>{k.toLocaleUpperCase("tr")}</text>
            <text x={x} y={y + 38} textAnchor={sag ? "start" : sol ? "end" : "middle"} dominantBaseline="middle"
              fill={renk} fontSize={34} fontWeight={900} fontFamily="Arial Black, Arial, sans-serif">
              {Math.round(Math.min(100, Math.max(0, degerler[i])))}
            </text>
          </g>
        );
      })}
    </svg>
  );
};
