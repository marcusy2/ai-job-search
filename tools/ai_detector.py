#!/usr/bin/env python3
"""Local AI-text detector for application prose (form answers, cover letters, emails).

Approximates how commercial detectors (GPTZero, Originality, etc.) score text, in two layers:

1. Language-model layer (the GPTZero method): score every token with GPT-2.
   - Perplexity: how predictable the text is to a language model. LLM output picks
     high-probability words, so it reads as low-perplexity.
   - Burstiness: how much perplexity swings between sentences. Humans mix plain and
     surprising sentences; LLMs are uniformly smooth.
2. Style-tell layer: surface patterns detectors and human readers both key on
   (em-dashes, colon setups, tricolons, stock "AI vocabulary", "not just X",
   aphoristic closers, uniform sentence lengths, repeated sentence openers).

Each signal maps to a 0-1 "AI-likeness" and the weighted blend is a 0-100 score.
PASS means score < --threshold (default 35) AND sentence-length CV >= --min-cv (0.38). This is an approximation, not GPTZero:
treat a PASS as necessary, not sufficient. Calibration (2026-10-29): GPT-2 small
perplexity did NOT separate a known-AI draft (ppl 56) from the candidate's plainer
writing (ppl 41) - jargon inflates perplexity - so it is down-weighted and style tells +
burstiness carry the score. Recalibrate once real samples of the candidate's writing exist.

Usage (needs the venv with torch + transformers):
    ~/.venvs/ai-detector/Scripts/python tools/ai_detector.py answers.txt
    ~/.venvs/ai-detector/Scripts/python tools/ai_detector.py --text "Some paragraph."
    ~/.venvs/ai-detector/Scripts/python tools/ai_detector.py --fields form_fields.txt
      (--fields scores each FIELD block of a documents/applications form_fields.txt
       separately and skips NOTE TO SELF blocks)
"""

import argparse
import math
import re
import statistics
import sys
from pathlib import Path

AI_VOCAB = [
    "delve", "tapestry", "testament", "pivotal", "crucial", "foster", "leverage",
    "seamless", "seamlessly", "robust", "showcase", "underscore", "underscores",
    "ever-evolving", "landscape", "navigate", "navigating", "realm", "meticulous",
    "intricate", "embark", "journey", "elevate", "empower", "harness", "unwavering",
    "invaluable", "multifaceted", "holistic", "paramount", "resonate", "resonates",
    "thrive", "dynamic", "cutting-edge", "innovative", "passionate", "spearhead",
    "synergy", "transformative", "vibrant", "nuanced", "commendable", "profound",
    "deeply", "truly", "genuinely", "firsthand", "invigorating",
]
AI_PHRASES = [
    r"\bnot just\b", r"\bnot only\b", r"\bmore than just\b", r"\brather than\b",
    r"\bin today's\b", r"\bat the intersection of\b", r"\bplays a (key|vital|crucial) role\b",
    r"\bit's not about\b", r"\bwhat (really|truly) matters\b", r"\bthe real \w+ is\b",
    r"\bi am (excited|eager|thrilled) to\b", r"\bfrom day one\b", r"\bevery single\b",
    r"\bat its core\b", r"\bin other words\b", r"\bultimately\b", r"\bmoreover\b",
    r"\bfurthermore\b", r"\badditionally\b", r"\bin conclusion\b", r"\bthat's exactly\b",
    r"\bexactly what\b", r"\bnot because\b", r"\bthe gap between\b",
]
TRICOLON = re.compile(r"\b[\w'-]+(?: [\w'-]+){0,3}, [\w'-]+(?: [\w'-]+){0,3},? and [\w'-]+", re.I)


def sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", text)
    return [p for p in parts if len(p.split()) >= 3]


def clamp(x):
    return max(0.0, min(1.0, x))


def lm_scores(sents, model_name):
    import torch
    from transformers import GPT2LMHeadModel, GPT2TokenizerFast

    tok = GPT2TokenizerFast.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name).eval()
    per_sent, all_nll, n_tok = [], 0.0, 0
    context = []
    with torch.no_grad():
        for s in sents:
            # score each sentence conditioned on preceding text (up to 512 tokens)
            ctx_ids = tok(" ".join(context), return_tensors="pt").input_ids[0][-400:] if context else None
            s_ids = tok((" " if context else "") + s, return_tensors="pt").input_ids[0]
            ids = torch.cat([ctx_ids, s_ids]) if ctx_ids is not None else torch.cat([torch.tensor([tok.bos_token_id]), s_ids])
            labels = ids.clone()
            labels[: len(ids) - len(s_ids)] = -100
            out = model(ids.unsqueeze(0), labels=labels.unsqueeze(0))
            nll = out.loss.item()
            per_sent.append(math.exp(nll))
            all_nll += nll * len(s_ids)
            n_tok += len(s_ids)
            context.append(s)
    ppl = math.exp(all_nll / max(n_tok, 1))
    burst = statistics.pstdev(per_sent) / statistics.mean(per_sent) if len(per_sent) > 1 else 0.0
    return ppl, burst, per_sent


def style_signals(text, sents):
    words = re.findall(r"[A-Za-z'-]+", text)
    nw = max(len(words), 1)
    per100 = 100.0 / nw
    low = text.lower()
    lens = [len(s.split()) for s in sents]
    cv = statistics.pstdev(lens) / statistics.mean(lens) if len(lens) > 1 else 0.0
    openers = [s.split()[0].lower() for s in sents]
    opener_rep = 1 - len(set(openers)) / max(len(openers), 1)
    vocab_hits = [w for w in AI_VOCAB if re.search(rf"\b{re.escape(w)}\b", low)]
    phrase_hits = [p for p in AI_PHRASES if re.search(p, low)]
    colon_setups = len(re.findall(r"[a-z]: [A-Za-z]", text))
    emdash = text.count("—") + text.count(" -- ") + text.count("– ")
    semis = text.count(";")
    tricolons = len(TRICOLON.findall(text))
    # aphoristic closer: a paragraph's last sentence that is general (no digits, no "I/my")
    closers = 0
    for para in [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]:
        ps = sentences(para)
        if len(ps) >= 3:
            last = ps[-1]
            if not re.search(r"\d", last) and not re.search(r"\b(I|my|me|I'm|I've)\b", last):
                closers += 1
    return {
        "words": nw,
        "sent_len_cv": cv,
        "opener_repetition": opener_rep,
        "ai_vocab": vocab_hits,
        "ai_phrases": phrase_hits,
        "colon_setups": colon_setups,
        "em_dashes": emdash,
        "semicolons": semis,
        "tricolons_per100": tricolons * per100,
        "aphoristic_closers": closers,
    }


def score(text, model_name="gpt2", use_lm=True):
    sents = sentences(text)
    st = style_signals(text, sents)
    sig = {}
    reasons = []
    if use_lm and sents:
        ppl, burst, per = lm_scores(sents, model_name)
        st["perplexity"], st["burstiness"] = ppl, burst
        # GPT-2 small: polished LLM prose ~15-30, human application prose ~40-90+
        sig["perplexity"] = (clamp((55 - ppl) / 35), 0.10)
        # human sentence-PPL CV usually > 0.5; LLM prose ~0.2-0.4
        sig["burstiness"] = (clamp((0.55 - burst) / 0.35), 0.20)
        if ppl < 35: reasons.append(f"low perplexity {ppl:.0f} (text is very predictable)")
        if burst < 0.40: reasons.append(f"low burstiness {burst:.2f} (every sentence equally smooth)")
        low_sents = sorted(zip(per, sents))[:3]
        st["most_predictable"] = [f"{p:.0f}: {s[:90]}" for p, s in low_sents]
    sig["sent_len_uniform"] = (clamp((0.50 - st["sent_len_cv"]) / 0.30), 0.15)
    if st["sent_len_cv"] < 0.35: reasons.append(f"sentence lengths too uniform (CV {st['sent_len_cv']:.2f})")
    tell = (len(st["ai_vocab"]) * 0.5 + len(st["ai_phrases"]) * 0.6 + st["colon_setups"] * 0.6
            + st["em_dashes"] * 1.0 + st["semicolons"] * 0.4 + st["aphoristic_closers"] * 0.6
            + max(0, st["tricolons_per100"] - 0.6) * 1.5 + max(0, st["opener_repetition"] - 0.35) * 3)
    sig["style_tells"] = (clamp(tell / 3.0), 0.55 if use_lm else 0.85)
    for k in ("ai_vocab", "ai_phrases"):
        if st[k]: reasons.append(f"{k.replace('_', ' ')}: {', '.join(st[k])}")
    for k in ("colon_setups", "em_dashes", "semicolons", "aphoristic_closers"):
        if st[k]: reasons.append(f"{k.replace('_', ' ')}: {st[k]}")
    if st["tricolons_per100"] > 0.6: reasons.append(f"tricolons: {st['tricolons_per100']:.1f}/100 words")
    total_w = sum(w for _, w in sig.values())
    s = 100 * sum(v * w for v, w in sig.values()) / total_w
    return s, st, reasons, sig


def split_fields(text):
    blocks = re.split(r"={10,}\n(FIELD [^\n]*|NOTE TO SELF[^\n]*)\n={10,}\n", text)
    out = []
    for i in range(1, len(blocks), 2):
        if blocks[i].startswith("FIELD"):
            body = blocks[i + 1].strip()
            if len(body.split()) >= 40:
                out.append((blocks[i][:70], body))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--text")
    ap.add_argument("--fields", action="store_true")
    ap.add_argument("--threshold", type=float, default=35.0)
    ap.add_argument("--min-cv", type=float, default=0.38, help="hard floor on sentence-length variation")
    ap.add_argument("--model", default="gpt2")
    ap.add_argument("--no-lm", action="store_true", help="style layer only (no torch needed)")
    a = ap.parse_args()
    raw = a.text if a.text else Path(a.file).read_text(encoding="utf-8")
    items = split_fields(raw) if a.fields else [("text", raw)]
    worst = 0
    for name, body in items:
        s, st, reasons, _ = score(body, a.model, not a.no_lm)
        worst = max(worst, s)
        ok = s < a.threshold and st["sent_len_cv"] >= a.min_cv
        if not ok:
            worst = max(worst, a.threshold)
        verdict = "PASS" if ok else "FAIL"
        extra = f" ppl={st['perplexity']:.0f} burst={st['burstiness']:.2f}" if "perplexity" in st else ""
        print(f"[{verdict}] {name}: AI-likeness {s:.0f}/100 ({st['words']} words{extra}, sent-len CV {st['sent_len_cv']:.2f})")
        for r in reasons:
            print(f"    - {r}")
        for m in st.get("most_predictable", []):
            print(f"    ~ predictable: {m}")
    sys.exit(0 if worst < a.threshold else 1)


if __name__ == "__main__":
    main()
