"""Gambit'in LM Studio sanal model tanımlarını (gambit/<ad>/model.yaml) üretir ve isteğe bağlı kurar.

  python lmstudio-hub/build.py            # gambit/ klasörünü yeniden üret
  python lmstudio-hub/build.py --install  # ayrıca ~/.lmstudio/hub/models/gambit/ altına kopyala

Sanal model, diskteki GGUF'u (base) değiştirmeden ona yükleme ayarları ve düşünme düzeyleri ekler. Her model için
iki tanım üretilir:
- gambit/<ad>: metin modu, --mmproj kaldırılır (görsel eki 6 GB'lık kartta 0,6-1,8 GB VRAM yiyordu).
- gambit/<ad>-vision: görsel modu, görsel eki yüklenir (Gambit'te /vision ve /image).
Ayrıca:
- Şablonu kademeli düzey tanıyan modellerde (Inkling, Qwen3.8/Bonsai) reasoning_effort bir seçim alanına bağlanır;
  LM Studio istekteki reasoning_effort'u ancak böyle şablona iletir.
- Inkling 2 Mini: llama.cpp'nin op offload'u (CPU'daki ağırlıkları hesap için GPU'ya kopyalama) 6-7 GB tampon istiyor,
  --no-op-offload ile kapatılır. Ama LM Studio'nun isteğe bağlı tensör yüklemesi (lazyMode) açıkken GPU katmanlarının
  ağırlıkları da op offload'la taşındığı için GPU'ya hiç gitmiyor ve 11,6 GB'lık uzman ağırlıklarının tamamı RAM'de
  kalıyordu. lazyMode kapatılır, bütün katmanlar GPU'ya verilir (--gpu max) ve uzman tensörlerinin GPU'ya sığmayan
  kısmı --override-tensor ile CPU'da tutulur. GPU'da en çok iş yapan döngülü blokların (6-17, token başına 3 kez
  çalışır) ilk INKLING_GPU_EXPERT_BLOCKS tanesinin uzmanları kalır."""
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Uzmanları GPU'da kalan döngülü blok sayısı (her biri 0,48 GB), metin / görsel modu. 27 Kasım ölçümü (16k, nvidia modu):
# metinde 5 blokla uzun prompttan sonra 263 MiB boş kalıyordu, 4 blokla 725 MiB (12,1 tok/s); görsel ek 0,61 GB daha ister
INKLING_GPU_EXPERT_BLOCKS = (4, 2)
# CPU'daki uzmanlar prompt'ta da CPU'da hesaplanıyor (op offload kapalı); LM Studio 6 iş parçacığı veriyor, Ryzen 7 6800HS'te
# 8 çekirdek var. Prompt için 8 (--threads-batch): uzun prompt 44 → 48 tok/s (iki ölçümde tutarlı). Üretim için 8
# (--threads), prompt için 16 ve işlem grubu 256 + 3 GPU bloğu gürültü içinde kaldı ya da üretimi düşürdü.
INKLING_THREADS_BATCH = "8"


def cpu_experts_regex(gpu_blocks: list[int], n_blocks: int = 24) -> str:
    """GPU'da kalmayacak blokların uzman tensörlerini CPU'ya yönlendiren --override-tensor değeri."""
    cpu = [str(b) for b in range(n_blocks) if b not in gpu_blocks]
    return rf"blk\.({'|'.join(cpu)})\.ffn_(gate_up|down)_exps\.weight=CPU"

THINK_TOGGLE = """  - key: enableThinking
    displayName: Enable Thinking
    description: Controls whether the model will think before replying
    type: boolean
    defaultValue: true
    effects:
      - type: setJinjaVariable
        variable: enable_thinking
"""


def effort_field(levels: list[str], default: str, note: str) -> str:
    opts = "".join(f"      - value: {v}\n        label: {v.capitalize()}\n" for v in levels)
    return (f"  - key: reasoningEffort\n    displayName: Reasoning Effort\n    description: {note}\n"
            f"    type: select\n    defaultValue: {default}\n    options:\n{opts}"
            "    effects:\n      - type: setJinjaVariable\n        variable: reasoning_effort\n")


MODELS = {
    "ornith-1.5-9b-uncensored": dict(
        title="Ornith 1.5 9B sansürsüz", base="mradermacher/ornith-1.5-9b-uncensored-gguf",
        user="mradermacher", repo="Ornith-1.5-9B-uncensored-GGUF", arch="qwen35", params="9B", ctx=262144,
        fields=THINK_TOGGLE),
    "inkling-2-mini-uncensored": dict(
        title="Inkling 2 Mini sansürsüz", base="atomicchat/inkling-2-mini-uncensored-gguf",
        user="AtomicChat", repo="Inkling-2-Mini-Uncensored-GGUF", arch="inkling2_loop", params="128x1.8B",
        ctx=1048576, lazy="off", ubatch=128, gpu_expert_blocks=INKLING_GPU_EXPERT_BLOCKS,
        override={"--no-op-offload": "", "--threads-batch": INKLING_THREADS_BATCH},
        fields=effort_field(["low", "medium", "high", "xhigh"], "high",
                            "How much the model thinks before replying (the lowest level still thinks a little)")),
    "qwen3.5-9b-defiant-fable": dict(
        title="Qwen3.5 9B Defiant Fable sansürsüz",
        base="davidau/qwen3.5-9b-the-defiant-fable-uncensored-heretic-neo-imatrix-max-mtp-gguf",
        user="DavidAU", repo="Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF",
        arch="qwen35", params="9B", ctx=262144, fields=THINK_TOGGLE),
    "gemma-4-26b-a4b-qat": dict(
        title="Gemma 4 26B A4B QAT", base="lmstudio-community/gemma-4-26b-a4b-it-qat-gguf",
        user="lmstudio-community", repo="gemma-4-26B-A4B-it-QAT-GGUF", arch="gemma4", params="26B", ctx=262144,
        fields=THINK_TOGGLE,
        # LM Studio'nun kendi tanımındaki (google/gemma-4-26b-a4b-qat) örnekleme ve düşünme ayrıştırması
        operation="""  operation:
    fields:
      - key: llm.prediction.temperature
        value: 1.0
      - key: llm.prediction.topPSampling
        value:
          checked: true
          value: 0.95
      - key: llm.prediction.topKSampling
        value: 64
      - key: llm.prediction.repeatPenalty
        value:
          checked: true
          value: 1
      - key: llm.prediction.reasoning.parsing
        value:
          enabled: true
          startString: "<|channel>thought"
          endString: "<channel|>"
"""),
    "ternary-bonsai-2.5-27b": dict(
        title="Ternary Bonsai 2.5 27B (Qwen3.8 27B)", base="prism-ml/ternary-bonsai-2.5-27b-gguf",
        user="prism-ml", repo="Ternary-Bonsai-2.5-27B-GGUF", arch="qwen35", params="27B", ctx=262144,
        fields=THINK_TOGGLE + effort_field(["medium", "xhigh"], "xhigh",
                                           "xhigh is the most accurate; medium is shorter (low is not supported)")),
}


def render(name: str, m: dict, vision: bool) -> str:
    override = dict(m.get("override", {}))
    if m.get("gpu_expert_blocks"):
        k = m["gpu_expert_blocks"][1 if vision else 0]
        override["--override-tensor"] = cpu_experts_regex(list(range(6, 6 + k)))
    overrides = "".join(f"            - key: \"{k}\"\n              value: '{v}'\n" for k, v in override.items())
    disabled = "          disabledParameters: []\n" if vision else '          disabledParameters:\n            - "--mmproj"\n'
    load = ["      - key: llm.load.llama.argumentsOverride\n        value:\n          enabled: true\n" + disabled
            + (f"          overrideParameters:\n{overrides}" if overrides else "          overrideParameters: []\n")
            + "          excludeAllConfig: false\n"]
    if m.get("lazy"):
        load.append(f'      - key: llm.load.lazyMode\n        value: "{m["lazy"]}"\n')
    if m.get("ubatch"):
        load.append(f"      - key: llm.load.llama.physicalBatchSize\n        value: {m['ubatch']}\n")
    mode = "görsel modu (görsel eki yüklenir)" if vision else "metin modu (görsel eki yüklenmez)"
    return (f"# Gambit: {m['title']}, {mode}; ai-cli/lmstudio-hub/build.py üretir, elle değiştirme\n"
            f"model: gambit/{name}{'-vision' if vision else ''}\nbase:\n  - key: {m['base']}\n    sources:\n      - type: huggingface\n"
            f"        user: {m['user']}\n        repo: {m['repo']}\n"
            f"config:\n{m.get('operation', '')}  load:\n    fields:\n{''.join(load)}"
            f"customFields:\n{m['fields']}"
            f"metadataOverrides:\n  domain: llm\n  architectures:\n    - {m['arch']}\n  compatibilityTypes:\n"
            f"    - gguf\n  paramsStrings:\n    - {m['params']}\n  contextLengths:\n    - {m['ctx']}\n"
            f"  vision: {'true' if vision else 'false'}\n  reasoning: true\n  trainedForToolUse: true\n")


def main() -> int:
    out = HERE / "gambit"
    shutil.rmtree(out, ignore_errors=True)
    for name, m in MODELS.items():
        for vision in (False, True):
            d = out / (name + ("-vision" if vision else ""))
            d.mkdir(parents=True)
            (d / "model.yaml").write_text(render(name, m, vision), encoding="utf-8")
    print(f"{2 * len(MODELS)} tanım: {out}")
    if "--install" in sys.argv:
        target = Path.home() / ".lmstudio" / "hub" / "models" / "gambit"
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(out, target)
        print(f"kuruldu: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
