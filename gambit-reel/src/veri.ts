// Panodaki güvenilir skorlar: bishop ve queen kapalı (sabit örneklemeyle 3 koşu ortalaması), king otomatik, Gambit Bench v2 — 39 görev, zorluk ağırlıklı
export const KATEGORILER = ["Kod yazma", "Hata", "Okuma", "SQL", "Terminal", "Ajan", "Mantık", "Talimat", "İnceleme"] as const;

export type Model = {ad: string; model: string; renk: string; genel: number; kategoriler: number[]};

export const MODELLER: Model[] = [
  {
    "ad": "Bishop",
    "model": "Qwen3.5 9B",
    "renk": "#a855f7",
    "genel": 57.3,
    "kategoriler": [
      35,
      73,
      53,
      47,
      72,
      55,
      89,
      74,
      59
    ]
  },
  {
    "ad": "Queen",
    "model": "Gemma 4 26B",
    "renk": "#38bdf8",
    "genel": 79.5,
    "kategoriler": [
      85,
      92,
      64,
      66,
      93,
      62,
      99,
      93,
      90
    ]
  },
  {
    "ad": "King",
    "model": "Qwen3.8 27B",
    "renk": "#fbbf24",
    "genel": 89.1,
    "kategoriler": [
      81,
      91,
      97,
      79,
      100,
      87,
      96,
      100,
      78
    ]
  }
];
