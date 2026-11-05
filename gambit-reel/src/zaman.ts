// Zaman çizelgesi şarkının vuruş ızgarasına göre: "Loucura Letal Funk (Ultra Slowed)", ~103 BPM.
// Şarkıdaki en güçlü dört bas vuruşu (6,55 / 8,87 / 11,19 / 13,54 sn) birer ölçü arayla geliyor;
// bishop, queen, king ve kapanış tam bunlara oturur. Vuruş 0 şarkının 0,14. saniyesi.
export const FPS = 60;
export const BPM = 103;
export const VURUS_SN = 60 / BPM; // ≈ 0,5825 sn
export const VURUS = FPS * VURUS_SN; // ≈ 35 kare
const FAZ_SN = 6.55 - 11 * VURUS_SN; // 11. vuruş = 6,55 sn (bishop'un girişi)
export const v = (n: number) => Math.round((FAZ_SN + n * VURUS_SN) * FPS);

// Önemli anlar (vuruş cinsinden)
export const VEZIR = 6.5; // vezir a4'e kaymaya başlar
export const DROP = 9; // vezir şah çeker: GAMBIT
export const LOGO = 24.5;
export const SAHNE = {
  satranc: [-1, 11],
  bishop: [11, 15],
  queen: [15, 19],
  king: [19, 23],
  kapanis: [23, 31],
} as const;
export const SURE_SN = 17.6; // şarkı kesitinin uzunluğu
export const TOPLAM = Math.round(SURE_SN * FPS);

// Vuruş anları ve gücü: titreşim, yakınlaşma, flaş ve renk kayması bunlardan türer
export const VURUSLAR: {at: number; guc: number}[] = [
  {at: 1, guc: 0.25}, {at: 2.5, guc: 0.25}, {at: 4, guc: 0.35}, {at: 5.5, guc: 0.45},
  {at: DROP, guc: 1},
  {at: 11, guc: 1}, {at: 15, guc: 0.95}, {at: 19, guc: 1},
  {at: 23, guc: 0.9}, {at: LOGO, guc: 1}, {at: 27, guc: 0.6}, {at: 28, guc: 0.5}, {at: 29, guc: 0.6},
];

// Vitrin sahnelerinde her vuruşta hafif nabız
export const NABIZ = Array.from({length: 23 - 11}, (_, i) => 11 + i);

/** Kare anındaki toplam vuruş etkisi (üstel sönümlü), 0..~1 */
export const etki = (kare: number, sonum = 0.55) =>
  VURUSLAR.reduce((t, h) => {
    const d = kare - v(h.at);
    return d < 0 ? t : t + h.guc * Math.exp(-d / (sonum * VURUS));
  }, 0);

/** Yalnızca büyük vuruşların (güç ≥ 0,8) hızlı sönen flaşı */
export const flas = (kare: number) =>
  VURUSLAR.filter((h) => h.guc >= 0.8).reduce((t, h) => {
    const d = kare - v(h.at);
    return d < 0 ? t : Math.max(t, Math.exp(-d / (0.18 * VURUS)));
  }, 0);

export const nabiz = (kare: number) =>
  NABIZ.reduce((t, n) => {
    const d = kare - v(n);
    return d < 0 ? t : t + 0.12 * Math.exp(-d / (0.25 * VURUS));
  }, 0);

/** Kareye bağlı, deterministik sözde rastgele sayı (-1..1) */
export const gurultu = (kare: number, tohum: number) => {
  const x = Math.sin(kare * 12.9898 + tohum * 78.233) * 43758.5453;
  return (x - Math.floor(x)) * 2 - 1;
};

export const kirp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const yumusak = (t: number) => {
  const x = kirp(t);
  return x * x * (3 - 2 * x);
};
