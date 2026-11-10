"""Umay'ın sitede 9 Kasım 2026'da eklenen iki modelini (Umay Ultra Hızlı, Umay Daha Zeki) Gambit Bench v2'de
düşünme açık ve kapalı koşturur; biten yapılandırmaları results-umay'a ekler ve raporu yeniden üretir.

  python umay_yeni_modeller.py --sure-siniri-yok   # 4 yapılandırma aynı anda, görev süre sınırı yok
  python umay_yeni_modeller.py                     # 4 yapılandırma aynı anda, önceki koşuların süre sınırıyla
  python umay_yeni_modeller.py --paralel model     # iki model aynı anda, her biri önce açık sonra kapalı
  python umay_yeni_modeller.py --paralel yok       # dört yapılandırma tek tek
  python umay_yeni_modeller.py --birlestir         # koşturmadan, bitenleri results-umay'a ekle ve raporu üret
  python umay_yeni_modeller.py --model umay-akilli --mod dusunme --mod varsayilan --mod kapali
                                                   # başka model ve modlar (varsayilan: düşünme alanı gönderilmez)

Her yapılandırma kendi klasöründe (results-umay-yeni/<model>__<mod>) koşar, böylece aynı anda koşanlar aynı dosyaya
yazmaz; her yapılandırmada istekler önceki koşulardaki gibi sırayla, tek tek gider. 39 görevin hepsi sonuçlanınca
(sunucu tarafı hatayla biten görev kalmayınca) yapılandırma results-umay'a taşınır. Sunucu tarafı hata: model hiçbir
şey üretmeden gelen HTTP/akış hatası; bu görevler yeniden koşar. Modelin boş ya da yarım cevabı ise önceki altı
koşudaki gibi sonuçtur ve tekrar denenmez. Anahtar bir kez gizli sorulur, alt süreçlere yalnızca ortam değişkeniyle
verilir, hiçbir dosyaya yazılmaz. Yarıda kalırsa aynı komutla yeniden başlat: biten görevler atlanır, results-umay'a
eklenmiş bir yapılandırmada sonradan hatalı çıkan görevler de yalnızca kendileri koşar."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

MODELS = ["umay-ultra-hizli", "umay-daha-zeki"]
MODES = {"dusunme": [], "varsayilan": ["--server-default-thinking"], "kapali": ["--no-thinking"]}
DEFAULT_MODES = ["dusunme", "kapali"]
MODE_TAGS = {"dusunme": "açık", "varsayilan": "otomatik", "kapali": "kapalı"}
_print = threading.Lock()


def say(prefix: str, text: str) -> None:
    with _print:
        print(f"[{prefix}] {text}" if prefix else text, flush=True)


def _rows(path: Path, model: str, mode: str) -> list[str]:
    """Bir jsonl dosyasının bu modele ve moda ait satırları (bozuk satırlar atlanır)."""
    out = []
    if path.is_file():
        for ln in path.read_text(encoding="utf-8-sig").splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("preset") == model and r.get("mode") == mode:
                out.append(ln)
    return out


def _append(path: Path, lines: list[str]) -> int:
    old = set(path.read_text(encoding="utf-8-sig").splitlines()) if path.is_file() else set()
    new = [ln for ln in lines if ln not in old]
    if new:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write("".join(ln + "\n" for ln in new))
    return len(new)


def server_side(r: dict) -> bool:
    """Sunucu tarafında kalan hata: model hiçbir şey üretmedi. 9 Kasım 2026'daki ilk görevlerde sürücü, Umay'ın arka
    ucunun sağlayıcıya hiç ulaşamadığı durumu ("Tüm API anahtarları denendi fakat yanıt alınamadı") henüz çökme diye
    kaydediyordu. Model çıktısı başladıktan sonraki kesilmeler (ör. "context deadline exceeded") sonuçtur."""
    return bool(r.get("server_error")) or "Tüm API anahtarları denendi" in (r.get("crash") or "")


def status(lines: list[str]) -> tuple[list[str], list[str]]:
    """Hiç koşmamış görevler ve son denemesi sunucu tarafı hatayla biten görevler."""
    import core
    import gorevler  # noqa: F401
    last = {}
    for ln in lines:
        r = json.loads(ln)
        last[r["task"]] = r  # aynı görev birden çok kez koştuysa sonuncusu (rapor.load gibi)
    ids = [t.id for t in core.TASKS]
    return [t for t in ids if t not in last], [t for t in ids if t in last and server_side(last[t])]


def complete(lines: list[str]) -> bool:
    missing, errored = status(lines)
    return not missing and not errored


def job(model: str, mode: str, lanes: Path, target: Path, env: dict, extra: list[str], only: str) -> None:
    """Bir yapılandırmayı koşturur; çıktıyı yapılandırma adıyla öneklenmiş satırlarla gösterir. Sunucu hatasıyla
    biten görevler (umay_kos.py her birini zaten üç kez dener) en fazla iki tur daha denenir."""
    tag = f"{model.removeprefix('umay-')} {MODE_TAGS[mode]}"
    out = lanes / f"{model}__{mode}"
    if complete(_rows(target / "results.jsonl", model, mode)):
        say(tag, f"{target.name} içinde zaten var; atlanıyor")
        return
    for _ in range(3):
        # Daha önce eklenmiş satırlar da sayılır: yalnızca eksik ya da sunucu hatasıyla biten görevler koşar
        rows = _rows(target / "results.jsonl", model, mode) + _rows(out / "results.jsonl", model, mode)
        missing, errored = status(rows)
        if rows and not missing and not errored:
            return
        todo = only or (",".join(missing + errored) if rows else "")
        if rows and not only:
            say(tag, f"{len(missing)} görev koşmadı, {len(errored)} görev sunucu hatasıyla bitti; yalnızca bunlar koşuyor")
        # Görev klasörü önceki altı koşudaki yerde açılır (results-umay/sandboxes/<yapılandırma>/<görev>): model bu
        # yolu sistem isteminde çalışma klasörü olarak görür, yolun biçimi koşullar arasında fark yaratmamalı.
        cmd = [sys.executable, "-u", str(HERE / "umay_kos.py"), "--model", model, *MODES[mode], "--out", str(out),
               "--sandbox-root", str(target / "sandboxes"), *(["--only", todo] if todo else []), *extra]
        proc = subprocess.Popen(cmd, cwd=HERE, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
        for line in proc.stdout:
            if line.strip():
                say(tag, line.rstrip())
        if proc.wait():
            say(tag, f"umay_kos.py {proc.returncode} koduyla çıktı")
            return
        if only:
            return


def merge(jobs: list[tuple[str, str]], lanes: Path, target: Path) -> list[str]:
    """Sonuçlanan yapılandırmaları target'a ekler: sonuç satırları, yanıtlar ve görev klasörleri.
    Tekrar çalıştırmak güvenlidir: eklenmiş satırlar yeniden eklenmez."""
    import run
    merged = []
    for model, mode in jobs:
        label = f"{model}__{mode}"
        src = lanes / label
        lines = _rows(src / "results.jsonl", model, mode)
        if not lines:
            continue
        if not complete(_rows(target / "results.jsonl", model, mode) + lines):
            missing, errored = status(_rows(target / "results.jsonl", model, mode) + lines)
            say("", f"{label}: {len(missing)} görev koşmadı, {len(errored)} görev sunucu hatasıyla bitti; "
                    "hepsi sonuçlanınca eklenecek (aynı komutla sürdür)")
            continue
        added = _append(target / "results.jsonl", lines)  # rapor.load her görevin son satırını kullanır
        _append(target / "configs.jsonl", _rows(src / "configs.jsonl", model, mode))
        for kind in ("responses", "sandboxes"):  # görev klasörleri zaten target/sandboxes altında açılır
            if (src / kind / label).is_dir():
                dest = target / kind / label
                dest.mkdir(parents=True, exist_ok=True)
                for child in (src / kind / label).iterdir():  # görev görev: önceki görevlerin dosyaları kalır
                    old = dest / child.name
                    if old.is_dir():
                        run.fresh_dir(old)  # run.py'nin Windows'a dayanıklı silme yolu
                        old.rmdir()
                    elif old.exists():
                        old.unlink()
                    shutil.move(str(child), str(old))
        shutil.rmtree(src, ignore_errors=True)  # geriye yalnızca türetilmiş rapor dosyaları kalmıştı
        merged.append(label)
        say("", f"{label}: {added} sonuç satırı {target.name} klasörüne eklendi")
    if lanes.is_dir() and not any(lanes.iterdir()):
        lanes.rmdir()
    return merged


def main() -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", action="append", help=f"koşturulacak model (birden çok verilebilir; varsayılan: {', '.join(MODELS)})")
    ap.add_argument("--mod", action="append", choices=list(MODES),
                    help=f"koşturulacak düşünme modu (birden çok verilebilir; varsayılan: {', '.join(DEFAULT_MODES)})")
    ap.add_argument("--yapilandirma", action="append", metavar="MODEL__MOD",
                    help="tek bir yapılandırma, ör. umay-akilli__varsayilan (birden çok verilebilir; --model ve --mod'u geçersiz kılar)")
    ap.add_argument("--paralel", choices=["hepsi", "model", "yok"], default="hepsi",
                    help="hepsi: tüm yapılandırmalar aynı anda; model: modeller aynı anda; yok: tek tek")
    ap.add_argument("--sure-siniri-yok", action="store_true", help="umay_kos.py'ye geçer: görev başına süre sınırı yok")
    ap.add_argument("--birlestir", action="store_true", help="koşturmaz; yalnızca bitenleri ekler ve raporu üretir")
    ap.add_argument("--only", default="", help="umay_kos.py'ye aynen geçer (deneme için görev önekleri)")
    ap.add_argument("--base-url", default="", help="umay_kos.py'ye aynen geçer (yerel deneme sunucusu için)")
    ap.add_argument("--kosu-klasoru", default=str(HERE / "results-umay-yeni"), help="yapılandırmaların ayrı klasörleri")
    ap.add_argument("--hedef", default=str(HERE / "results-umay"), help="bitenlerin ekleneceği sonuç klasörü")
    a = ap.parse_args()
    jobs = [(m, mode) for m in (a.model or MODELS) for mode in (a.mod or DEFAULT_MODES)]
    if a.yapilandirma:
        bad = [x for x in a.yapilandirma if "__" not in x or x.split("__", 1)[1] not in MODES]
        if bad:
            ap.error(f"geçersiz yapılandırma: {', '.join(bad)} (biçim: model__{'|'.join(MODES)})")
        jobs = [tuple(x.split("__", 1)) for x in a.yapilandirma]
    lanes, target = Path(a.kosu_klasoru), Path(a.hedef)

    if not a.birlestir:
        key = os.environ.get("UMAY_API_KEY", "").strip()
        if not key and not a.base_url.startswith("http://127.0.0.1"):
            key = getpass.getpass("Umay API anahtarı (gizli): ").strip()
            if not key:
                print("Anahtar girilmedi.")
                return 1
        env = {**os.environ, "UMAY_API_KEY": key or "yerel-deneme", "PYTHONIOENCODING": "utf-8"}
        extra = [*(["--sure-siniri-yok"] if a.sure_siniri_yok else []), *(["--base-url", a.base_url] if a.base_url else [])]
        if a.paralel == "hepsi":
            groups = [[j] for j in jobs]
        elif a.paralel == "model":
            groups = [[j for j in jobs if j[0] == m] for m in dict.fromkeys(m for m, _ in jobs)]
        else:
            groups = [jobs]
        say("", f"{len(jobs)} yapılandırma · {len(groups)} kol aynı anda · "
                f"{'süre sınırı yok' if a.sure_siniri_yok else 'süre sınırı 8/5 dk'} · geçici sonuçlar: {lanes}")

        def worker(group):
            for model, mode in group:
                job(model, mode, lanes, target, env, extra, a.only)

        threads = [threading.Thread(target=worker, args=(g,), daemon=True) for g in groups]
        try:
            for t in threads:
                t.start()
            for t in threads:
                while t.is_alive():
                    t.join(1)
        except KeyboardInterrupt:
            say("", "Durduruldu. Aynı komutla kaldığı yerden sürer.")
            return 130

    merged = merge(jobs, lanes, target)
    if merged or a.birlestir:
        subprocess.run([sys.executable, str(HERE / "umay_kos.py"), "--report", "--out", str(target)], cwd=HERE,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
