#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import canonical_remake_sep12_13_v2 as v2


def gap_safe_build_ass(words, ass: pathlib.Path):
    """Bridge short intra-speech caption gaps without changing narration timing.

    Edge TTS can omit WordBoundary metadata, so v2 reconstructs timings from the
    encoded narration duration. Small proportional gaps between synthetic words
    can land exactly on a visual QA sample. Extend each word through the next
    word start when that gap is short; genuine long pauses remain untouched.
    """
    if not words:
        raise RuntimeError('CC_WORD_BOUNDARIES_EMPTY_AFTER_FALLBACK')

    fixed = [dict(w) for w in words]
    for i in range(len(fixed) - 1):
        cur = fixed[i]
        nxt = fixed[i + 1]
        cur_start = float(cur.get('offset', 0)) / 10_000_000
        cur_end = cur_start + float(cur.get('duration', 0)) / 10_000_000
        next_start = float(nxt.get('offset', 0)) / 10_000_000
        gap = next_start - cur_end
        if 0 < gap <= 0.80:
            cur['duration'] = int(max(0.06, next_start - cur_start) * 10_000_000)

    v2.corrected_build_ass(fixed, ass)


v2.base.build_ass = gap_safe_build_ass

if __name__ == '__main__':
    v2.base.main()
