import {AbsoluteFill, useCurrentFrame} from "remotion";
import {FPS, gurultu, kirp, VURUS_SN} from "./zaman";

// Şarkının ilk 12,1 saniyesi: gambit-cli'de queen yüklenip gerçek bir görev çözülüyor. Görünüm ai-cli/ai.py'nin
// arayüzünden (logo, taş renkleri, araç satırları, alt çubuk); içerik benchmark'taki gerçek queen koşusundan
// (term-log-rapor, tam puan), 12 saniyeye sığsın diye kısaltılmış.
export const GIRIS_SN = 12.1035; // kırpılmış kesitin şarkıdaki başlangıcı (çapraz korelasyonla bulundu)
const B = (i: number) => 0.013 + i * VURUS_SN; // şarkının vuruş ızgarası (saniye)

const LOGO = [
  " ██████   █████  ███    ███ ██████  ██ ████████",
  "██       ██   ██ ████  ████ ██   ██ ██    ██   ",
  "██   ███ ███████ ██ ████ ██ ██████  ██    ██   ",
  "██    ██ ██   ██ ██  ██  ██ ██   ██ ██    ██   ",
  " ██████  ██   ██ ██      ██ ██████  ██    ██   ",
];
const MUTED = "#8a8a8a", YESIL = "#16c60c", CAMGOBEGI = "#3a96dd";
const QUEEN = ["#af5fd7", "#5f87d7"], VARSAYILAN = ["#5f87d7", "#af5fd7"];
const COLS = 60;
const SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏";

type Parca = {t: string; c?: string; b?: boolean; bg?: string};
type Satir = {at: number; p: Parca[]; yaz?: [number, number]; on?: number; gecici?: number; logo?: number};  // on: yazılırken hep görünen önek

/** İki #rrggbb rengin karışımı (#rrggbb); CLI'deki _mix ile aynı */
const karistir = (a: string, b: string, t: number) => {
  const h = (s: string) => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16));
  const x = h(a), y = h(b);
  return "#" + x.map((v, i) => Math.round(v + (y[i] - v) * kirp(t)).toString(16).padStart(2, "0")).join("");
};

/** `kod` ve **kalın** işaretli metni CLI'nin markdown görünümüne çevirip COLS genişliğinde sarar */
const md = (metin: string): Parca[][] => {
  const parcalar: Parca[] = [];
  metin.split(/(`[^`]+`|\*\*[^*]+\*\*)/).forEach((s) => {
    if (!s) return;
    if (s.startsWith("`")) parcalar.push({t: s.slice(1, -1), c: CAMGOBEGI, b: true});
    else if (s.startsWith("**")) parcalar.push({t: s.slice(2, -2), b: true, c: "#fff"});
    else parcalar.push({t: s});
  });
  const satirlar: Parca[][] = [[]];
  let uzun = 0;
  parcalar.forEach((p) => p.t.split(/(\s+)/).forEach((k) => {
    if (!k) return;
    if (uzun + k.length > COLS - 2 && k.trim()) { satirlar.push([]); uzun = 0; if (!k.trim()) return; }
    if (!uzun && !k.trim()) return;
    satirlar[satirlar.length - 1].push({...p, t: k});
    uzun += k.length;
  }));
  return satirlar;
};

const PROMPT = "loglar klasöründeki .log dosyalarında ERROR, WARN ve INFO satırlarını say, sonucu rapor.csv'ye yaz";
const CEVAP_GIRIS = "`loglar` klasöründeki tüm `.log` dosyaları taranmış, belirtilen kriterlere göre (ERROR, WARN, INFO seviyeleri) sayılmış ve `rapor.csv` dosyası oluşturulmuştur.";
const CSV = ["dosya,error,warn,info", "eski/worker.log,3,0,1", "api.log,2,1,3", "web.log,1,2,3", "eski/bos.log,0,0,0", "eski/derin/cron.log,0,1,1"];

const kur = (): Satir[] => {
  const s: Satir[] = [];
  LOGO.forEach((_, r) => s.push({at: B(1), p: [], logo: r}));
  // terminal genişliğine sığmayan bilgi satırı, terminalin kaydırdığı gibi ikinci satıra iner
  s.push({at: B(2), p: [{t: "  ♟ model yok · /load queen ile yükle", c: VARSAYILAN[0], b: true}]});
  s.push({at: B(2), p: [{t: "  ·  düşünme otomatik  ·  araçlar açık", c: MUTED}]});
  s.push({at: B(2), p: [{t: "  C:\\AI\\projeler\\sunucu", c: MUTED}]});
  s.push({at: B(2), p: [{t: "  /help komutlar · Ctrl+C durdurur", c: MUTED}]});
  s.push({at: B(2), p: [{t: " "}]});
  s.push({at: B(3), p: [{t: "♟ ", c: VARSAYILAN[0], b: true}, {t: "› ", c: MUTED}, {t: "/load queen", c: "#fff"}], yaz: [B(3), B(4.6)], on: 4});
  s.push({at: B(5), gecici: B(7), p: [{t: "SPIN ♛ queen yükleniyor", c: QUEEN[0], b: true}, {t: " · diğer modeller boşaltılıyor", c: MUTED}]});
  s.push({at: B(7), p: [{t: "  ✓ ", c: YESIL}, {t: "♛ queen", c: QUEEN[0], b: true}, {t: " hazır"}, {t: " · bağlam 16384", c: MUTED}]});
  s.push({at: B(7), p: [{t: " "}]});
  const pr = md(PROMPT);
  pr.forEach((satir, i) => s.push({at: B(7.5), p: [...(i ? [{t: "  "}] : [{t: "♛ ", c: QUEEN[0], b: true}, {t: "› ", c: MUTED}]), ...satir.map((x) => ({...x, c: "#fff"}))],
    yaz: [B(7.5) + (i * (B(11.6) - B(7.5))) / pr.length, B(7.5) + ((i + 1) * (B(11.6) - B(7.5))) / pr.length], on: i ? 2 : 4}));
  s.push({at: B(12), gecici: B(13), p: [{t: "SPIN ♛ bağlam işleniyor", c: MUTED}]});
  s.push({at: B(13), p: [{t: "● ", c: QUEEN[0]}, {t: "list_dir", b: true}, {t: "  loglar", c: MUTED}]});
  s.push({at: B(13), p: [{t: "  └ ", c: MUTED}, {t: "✓ ", c: YESIL}, {t: "5 öğe", c: MUTED}]});
  s.push({at: B(14), p: [{t: "● ", c: QUEEN[0]}, {t: "run_python", b: true}, {t: "  import os import csv import re…  (57 satır)", c: MUTED}]});
  s.push({at: B(14), p: [{t: "  └ ", c: MUTED}, {t: "✓ ", c: YESIL}, {t: "çıkış 0", c: MUTED}]});
  s.push({at: B(14), p: [{t: "    Başarıyla oluşturuldu: rapor.csv", c: MUTED}]});
  s.push({at: B(15), p: [{t: "● ", c: QUEEN[0]}, {t: "read_file", b: true}, {t: "  rapor.csv", c: MUTED}]});
  s.push({at: B(15), p: [{t: "  └ ", c: MUTED}, {t: "✓ ", c: YESIL}, {t: "6 satır", c: MUTED}]});
  s.push({at: B(15), p: [{t: " "}]});
  // vuruşun girdiği an (9,3 sn) cevap akmaya başlar
  const akis: Parca[][] = [...md(CEVAP_GIRIS), [{t: " "}], ...md("**Oluşturulan** `rapor.csv` **içeriği:**"),
    ...CSV.map((c) => [{t: ` ${c.padEnd(COLS - 6)}`, c: "#e6e6e6", bg: "#1f1f2a"}]), [{t: " "}],
    ...md("İşlem başarıyla tamamlandı ve dosya doğrulandı.")];
  akis.forEach((p, i) => s.push({at: B(16) + (i * (B(19) - B(16))) / akis.length, p}));
  s.push({at: B(19.2), p: [{t: "  967 token · 17.2 tok/s · bağlam ▮▮▮▯▯▯▯▯ 5.9k/16.4k", c: MUTED}]});
  return s;
};
const SATIRLAR = kur();
const GORUNUR = 31; // pencereye sığan satır

const Parcalar: React.FC<{p: Parca[]; kac?: number; zaman: number}> = ({p, kac, zaman}) => {
  let kalan = kac ?? Infinity;
  return (
    <>
      {p.map((x, i) => {
        let t = x.t.replace("SPIN", SPIN[Math.floor(zaman * 12.5) % SPIN.length]);
        if (kalan <= 0) return null;
        if (t.length > kalan) t = t.slice(0, kalan);
        kalan -= t.length;
        return <span key={i} style={{color: x.c ?? "#d4d4d4", fontWeight: x.b ? 700 : 400, background: x.bg}}>{t}</span>;
      })}
    </>
  );
};

export const Terminal: React.FC = () => {
  const f = useCurrentFrame();
  const sn = f / FPS;
  const yuklendi = sn >= B(7);
  const renk = yuklendi ? QUEEN : VARSAYILAN;
  const gorunen = SATIRLAR.filter((s) => s.at <= sn && !(s.gecici && sn >= s.gecici));
  const kayma = Math.max(0, gorunen.length - GORUNUR);
  // vuruş etkisi: yazı ve araç satırlarında küçük, vuruşun girdiği anda (9,3 sn) büyük
  const GUC: [number, number][] = [[3, 0.3], [7, 0.4], [12, 0.3], [13, 0.4], [14, 0.4], [15, 0.4], [16, 1.6], [17, 0.35], [18, 0.35], [19, 0.5]];
  const vurus = GUC.reduce((t, [i, g]) => {
    const d = sn - B(i);
    return d < 0 ? t : t + g * Math.exp(-d / (i === 16 ? 0.25 : 0.18));
  }, 0);
  const son = kirp((sn - B(19.6)) / (GIRIS_SN - B(19.6))); // son 0,5 sn: ekran kırılır
  const kay = vurus * 10 + son * 40;
  const zoom = 0.92 + kirp(sn / GIRIS_SN) * 0.1 + vurus * 0.02 + son * 0.25;
  const sx = gurultu(f, 7) * (vurus * 10 + son * 30), sy = gurultu(f, 8) * (vurus * 10 + son * 30);
  const imlec = Math.floor(sn * 2) % 2 === 0;
  return (
    <AbsoluteFill style={{background: "radial-gradient(ellipse at 50% 40%, #16122a 0%, #050508 70%)"}}>
      <AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${zoom}) rotate(${gurultu(f, 9) * son * 3}deg)`,
        filter: kay > 0.5 ? `drop-shadow(${kay}px 0 0 rgba(255,43,214,0.75)) drop-shadow(${-kay}px 0 0 rgba(0,240,255,0.75))` : undefined,
        opacity: kirp(sn / 0.25)}}>
        <div style={{position: "absolute", left: 30, right: 30, top: 300, height: 1320, background: "#0c0c0c", borderRadius: 18,
          border: `2px solid ${renk[0]}`, boxShadow: `0 0 ${40 + vurus * 60}px ${renk[0]}66, inset 0 0 60px #000`, overflow: "hidden"}}>
          {/* başlık çubuğu */}
          <div style={{height: 54, background: "#1b1b1f", display: "flex", alignItems: "center", padding: "0 22px", gap: 12}}>
            {["#ff5f57", "#febc2e", "#28c840"].map((c) => <div key={c} style={{width: 16, height: 16, borderRadius: 8, background: c}} />)}
            <div style={{marginLeft: 20, fontFamily: "Consolas, monospace", fontSize: 22, color: MUTED}}>gambit · PowerShell</div>
          </div>
          {/* satırlar */}
          <div style={{padding: "22px 26px", fontFamily: "Consolas, 'Cascadia Mono', monospace", fontSize: 28, lineHeight: "38px",
            whiteSpace: "pre", transform: `translateY(${-kayma * 38}px)`}}>
            {gorunen.map((s, i) => {
              if (s.logo !== undefined) {
                const row = LOGO[s.logo];
                const kenar = kirp((sn - B(1)) / (B(2) - B(1))) * (row.length + 6);
                return (
                  <div key={i} style={{lineHeight: "33px"}}>{"  "}{[...row].map((ch, c) => {
                    if (ch === " " || c > kenar) return <span key={c}> </span>;
                    const parla = Math.max(0, 1 - (kenar - c) / 6) * (kenar < row.length + 6 ? 1 : 0);
                    const taban = karistir(VARSAYILAN[0], VARSAYILAN[1], (c + s.logo! * 2) / 55);
                    return <span key={c} style={{color: karistir(taban, "#ffffff", parla * 0.7)}}>{ch}</span>;
                  })}</div>
                );
              }
              const toplam = s.p.reduce((t, x) => t + x.t.length, 0);
              const on = s.on ?? 0;
              const kac = s.yaz ? on + Math.floor((toplam - on) * kirp((sn - s.yaz[0]) / (s.yaz[1] - s.yaz[0]))) : undefined;
              const yaziliyor = !!s.yaz && sn >= s.yaz[0] && sn < s.yaz[1] + 0.3;
              return (
                <div key={i} style={{minHeight: 38}}>
                  <Parcalar p={s.p} kac={kac} zaman={sn} />
                  {yaziliyor && (imlec || sn < s.yaz![1]) && <span style={{background: "#d4d4d4"}}> </span>}
                </div>
              );
            })}
            {/* model yüklendiyse ve henüz yazılmadıysa bekleyen istem */}
            {sn >= B(7) && sn < B(7.5) && (
              <div><span style={{color: QUEEN[0], fontWeight: 700}}>♛ </span><span style={{color: MUTED}}>› </span>
                {imlec && <span style={{background: "#d4d4d4"}}> </span>}</div>
            )}
          </div>
          {/* alt çubuk */}
          {yuklendi && (
            <div style={{position: "absolute", bottom: 0, left: 0, right: 0, height: 46, background: "#262626", display: "flex",
              alignItems: "center", fontFamily: "Consolas, monospace", fontSize: 24, color: "#bcbcbc"}}>
              <span style={{background: QUEEN[0], color: "#000", fontWeight: 700, padding: "0 10px", height: "100%", display: "flex",
                alignItems: "center"}}>♛ queen</span>
              <span>{"  düşünme otomatik · araçlar açık · onay otomatik · /help"}</span>
            </div>
          )}
        </div>
      </AbsoluteFill>
      {/* son anda beyaz flaş ile satranç tahtasına geçiş */}
      <AbsoluteFill style={{background: "#fff", opacity: kirp((sn - (GIRIS_SN - 0.12)) / 0.12) * 0.9 + (sn >= B(16) ? 0.6 * Math.exp(-(sn - B(16)) / 0.12) : 0)}} />
    </AbsoluteFill>
  );
};
