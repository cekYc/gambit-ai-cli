"""Benchmark sonuçlarını panonun okuduğu JSON dosyalarına çevirir (results/dashboard/*.json).

  python report.py               # results klasöründen
  python report.py --out <klasör>
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from bench import AGENT_MAX_STEPS, AGENT_TIME_BUDGET, MAX_TOKENS, RESULTS, SEED, load_jsonl  # noqa: E402
from tasks import CATEGORIES, TASKS  # noqa: E402

MODELS = {  # sıra = renk sırası; yeni model eklenince eskilerin rengi değişmez
    "coder": ("Qwen2.5-Coder 3B", "Coder 3B"),
    "4b": ("Qwen3.5 4B", "Qwen 4B"),
    "9b": ("Qwen3.5 9B", "Qwen 9B"),
    "gemma": ("Gemma 4 26B-A4B", "Gemma 26B"),
    "27b": ("Qwen3.8 27B", "Qwen 27B"),
    "coder30": ("Qwen3-Coder 30B-A3B", "Coder 30B"),
    "gemma12": ("Gemma 4 12B Coder", "Gemma 12B"),
}
MODES = {"off": "kapalı", "auto": "otomatik", "on": "açık"}  # sıra = tablolardaki sıra
HARDWARE = "RTX 3060 Laptop (6 GB VRAM), 15 GB RAM, LM Studio (llama.cpp CUDA 12)"


def model_fields(key: str, mode: str) -> dict:
    label, short = MODELS.get(key, (key, key))
    return {"config": f"{key}_{mode}", "model": key, "model_label": label, "model_short": short,
            "model_order": list(MODELS).index(key) if key in MODELS else len(MODELS),
            "mode": mode, "mode_label": MODES[mode]}


def _num(value: float, digits: int = 0) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def write_tables(rows: list[dict], configs: list[dict], out: Path) -> None:
    """Panodaki tabloları ayrı dosyalar olarak yazar: her biri .md (okumak için) ve .csv (Excel için)."""
    import csv
    from statistics import mean

    done = [c for c in configs if c["status"] != "atlandı"]
    by_config = {c["config"]: [r for r in rows if r["config"] == c["config"]] for c in done}
    # zorluk: 100 - tüm yapılandırmaların o görevdeki ortalama puanı (panodaki 'difficulty' hesabıyla aynı)
    difficulty = {t.id: round(100 * (1 - mean(r["score"] for r in rows if r["task"] == t.id)))
                  for t in TASKS if any(r["task"] == t.id for r in rows)}

    category_rows, summary_rows = [], []
    for c in done:
        cats = {}
        for cat in CATEGORIES:
            rs = [r for r in by_config[c["config"]] if r["category"] == cat]
            if not rs:
                continue
            cats[cat] = round(100 * mean(r["score"] for r in rs))
            category_rows.append([cat, len(rs), c["model_label"], c["mode_label"], cats[cat],
                                  _num(sum(r["wall_s"] for r in rs) / 60, 1), _num(sum(r["tokens"] for r in rs) / 1000, 1)])
        rs = by_config[c["config"]]
        if not rs:
            continue
        weight = sum(difficulty[r["task"]] for r in rs)
        hard = [r["score"] for r in rs if difficulty[r["task"]] >= 50]
        summary_rows.append([c["model_label"], c["mode_label"], round(mean(cats.values())),
                             round(100 * sum(difficulty[r["task"]] * r["score"] for r in rs) / weight) if weight else "",
                             round(100 * mean(hard)) if hard else ""]
                            + [cats.get(cat, "") for cat in CATEGORIES]
                            + [_num(sum(r["wall_s"] for r in rs) / 60, 1), _num(sum(r["tokens"] for r in rs) / 1000, 1),
                               sum(r["truncated"] for r in rs), c["status"]])
    category_rows.sort(key=lambda r: CATEGORIES.index(r[0]))

    task_rows = []
    for t in TASKS:
        cells = []
        for c in done:
            hit = next((r for r in by_config[c["config"]] if r["task"] == t.id), None)
            cells.append(round(100 * hit["score"]) if hit else "")
        task_rows.append([t.title, t.category, difficulty.get(t.id, "")] + cells)

    tables = {
        "1_puan_tablosu": (["Model", "Düşünme", "Genel", "Zorluk ağırlıklı", "Zor görevler"] + CATEGORIES + ["Süre (dk)", "Token (bin)", "Sınırda kesilen", "Durum"],
                           summary_rows),
        "2_kategori_ayrintisi": (["Kategori", "Soru", "Model", "Düşünme", "Puan", "Süre (dk)", "Token (bin)"], category_rows),
        "3_gorev_ayrintisi": (["Görev", "Kategori", "Zorluk"] + [f"{c['model_short']} ({c['mode_label']})" for c in done], task_rows),
    }
    out.mkdir(parents=True, exist_ok=True)
    for name, (header, body) in tables.items():
        with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f, delimiter=";").writerows([header, *body])
        md = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
        md += ["| " + " | ".join(str(v) for v in r) + " |" for r in body]
        (out / f"{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(RESULTS))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    results_dir = Path(args.results)
    out = Path(args.out) if args.out else results_dir / "dashboard"
    out.mkdir(parents=True, exist_ok=True)

    order = {t.id: i for i, t in enumerate(TASKS)}
    rows = []
    for r in load_jsonl(results_dir / "results.jsonl"):
        rows.append({
            **model_fields(r["model"], r["mode"]),
            "task": r["task"], "title": r["title"], "category": r["category"],
            "category_order": CATEGORIES.index(r["category"]), "task_order": order.get(r["task"], 99),
            "score": round(r["score"], 4), "wall_s": round(r.get("wall") or 0, 1), "tokens": r.get("tokens") or 0,
            "reasoning_chars": r.get("reasoning_chars") or 0, "truncated": bool(r.get("truncated")),
            "detail": r.get("detail", "")[:180],
        })

    done = {}
    for r in rows:
        done[r["config"]] = done.get(r["config"], 0) + 1
    configs = {}
    for c in load_jsonl(results_dir / "configs.jsonl"):  # aynı yapılandırma birden çok kez başlatıldıysa sonuncusu
        fields = model_fields(c["model"], c["mode"])
        if c.get("skipped"):
            configs[fields["config"]] = {**fields, "status": "atlandı", "note": c.get("reason", ""),
                                         "tasks_done": 0, "tasks_total": 0}
        else:
            n = done.get(fields["config"], 0)
            configs[fields["config"]] = {**fields, "status": "tamamlandı" if n >= len(TASKS) else "sürüyor",
                                         "note": "", "tasks_done": n, "tasks_total": len(TASKS)}
    config_rows = sorted(configs.values(), key=lambda c: (c["model_order"], list(MODES).index(c["mode"])))

    run = [{
        "tasks": len(TASKS), "categories": len(CATEGORIES), "max_tokens_off": MAX_TOKENS["off"],
        "max_tokens_on": MAX_TOKENS["on"], "seed": SEED, "agent_max_steps": AGENT_MAX_STEPS,
        "agent_budget_min": AGENT_TIME_BUDGET // 60, "hardware": HARDWARE,
        "updated": datetime.now().isoformat(timespec="minutes"),
    }]

    for name, data in [("results.json", rows), ("configs.json", config_rows), ("run.json", run)]:
        (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    write_tables(rows, config_rows, results_dir / "tablolar")
    print(f"{len(rows)} görev sonucu, {len(config_rows)} yapılandırma → {out}; tablolar → {results_dir / 'tablolar'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
