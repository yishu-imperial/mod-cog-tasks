"""
Full Mod-Cog task set (126 tasks).

The upstream `mod_cog_tasks.py` ships 93 named task builders. The int-x-seq
compositions (e.g. DlyGo_IntL_SeqR in the paper) are only present in the single
IntR_SeqR direction (the `*intseq` functions hardcode integrate=True, seq=True).

This module adds the 3 missing directional combos (IntR_SeqL, IntL_SeqR,
IntL_SeqL) for each of the 11 delay/int-capable tasks -> 11 x 3 = 33 extra,
giving 93 + 33 = 126 tasks, matching the repo README's stated maximum.

(The paper text says 84 + 48 = 132; that count and the promised supplementary
.zip were never reconciled with the public code, which tops out at 126.)

Usage:
    from mod_cog_all import make_all_envs, ALL_TASK_NAMES
    envs = make_all_envs()          # list of 126 env instances
    names = ALL_TASK_NAMES          # matching task names
"""
import inspect

import mod_cog_tasks as _M
from mod_cog_tasks import _reach, _DMFamily, _dlymatch, _dlydm_kwargs

_DEC = {'decision': 1000}  # sequence-production tasks use a long decision period


# --- directional int x seq builders for the 11 delay/int-capable tasks --------
# Each returns a fresh env; (integ, seqd) in {+1 (R), -1 (L)}.

def _reach_intseq(anti, integ, seqd, **kw):
    return _reach(anti=anti, integrate=integ, seq=seqd, timing=_DEC, **kw)

def _dm_intseq(w_mod, stim_mod, integ, seqd, **kw):
    ek = _dlydm_kwargs()
    ek.update({'w_mod': w_mod, 'stim_mod': stim_mod,
               'integrate': integ, 'seq': seqd, 'timing': _DEC})
    ek.update(kw)
    return _DMFamily(**ek)

def _match_intseq(matchto, matchgo, integ, seqd, **kw):
    return _dlymatch(matchto=matchto, matchgo=matchgo,
                     integrate=integ, seq=seqd, timing=_DEC, **kw)


# task_name_stem -> callable(integ, seqd) -> env
_DELAY_INT_TASKS = {
    'dlygo':      lambda i, s: _reach_intseq(False, i, s),
    'dlyanti':    lambda i, s: _reach_intseq(True,  i, s),
    'dlydm1':     lambda i, s: _dm_intseq((1, 1), (True, False), i, s),
    'dlydm2':     lambda i, s: _dm_intseq((1, 1), (False, True), i, s),
    'ctxdlydm1':  lambda i, s: _dm_intseq((1, 0), (True, True),  i, s),
    'ctxdlydm2':  lambda i, s: _dm_intseq((0, 1), (True, True),  i, s),
    'multidlydm': lambda i, s: _dm_intseq((1, 1), (True, True),  i, s),
    'dms':        lambda i, s: _match_intseq('sample',   True,  i, s),
    'dnms':       lambda i, s: _match_intseq('sample',   False, i, s),
    'dmc':        lambda i, s: _match_intseq('category', True,  i, s),
    'dnmc':       lambda i, s: _match_intseq('category', False, i, s),
}

_DIRS = {'intrseqr': (1, 1), 'intrseql': (1, -1),
         'intlseqr': (-1, 1), 'intlseql': (-1, -1)}


def _collect_named_builders():
    """All non-helper, module-level task builders already defined upstream (93)."""
    helpers = {'_get_dist', '_gaussianbump', '_cosinebump'}
    out = {}
    for name, obj in inspect.getmembers(_M, inspect.isfunction):
        if obj.__module__ == _M.__name__ and not name.startswith('_') \
                and name not in helpers:
            out[name] = obj
    return out


def build_task_dict():
    """Return {task_name: zero-arg builder} for the full 126-task set.

    Starts from the 93 upstream builders, drops the 11 legacy `*intseq`
    (== IntR_SeqR under an inconsistent name), then adds all 4 directional
    int x seq combos per delay task -> 93 - 11 + 44 = 126.
    """
    tasks = dict(_collect_named_builders())          # 93 existing
    for stem in _DELAY_INT_TASKS:                    # drop legacy IntR_SeqR-only
        tasks.pop(f'{stem}intseq', None)
    for stem, fn in _DELAY_INT_TASKS.items():
        for suffix, (i, s) in _DIRS.items():
            name = f'{stem}{suffix}'
            # bind i, s, fn at definition time
            tasks[name] = (lambda _fn, _i, _s: (lambda **kw: _fn(_i, _s)))(fn, i, s)
    return tasks


TASK_BUILDERS = build_task_dict()
ALL_TASK_NAMES = sorted(TASK_BUILDERS)


def make_all_envs(names=None):
    """Instantiate env objects for `names` (default: all)."""
    names = ALL_TASK_NAMES if names is None else names
    return [TASK_BUILDERS[n]() for n in names]


if __name__ == '__main__':
    print('total tasks:', len(ALL_TASK_NAMES))
