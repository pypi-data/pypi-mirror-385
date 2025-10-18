import sys
import csv
from types import SimpleNamespace
from .config import ensure_config_persisted, load_config

# USD / 1M tokens
MTOKEN_COSTS = {
    'Haiku 3.5':   dict(input=0.8,  output=4,    cache_write=1,     cache_read=0.08, cache_write_1h=1.6),
    'Haiku 3':     dict(input=0.25, output=1.25, cache_write=0.3,   cache_read=0.03, cache_write_1h=0.5),
    'Opus':        dict(input=15,   output=75,   cache_write=18.75, cache_read=1.5,  cache_write_1h=30),
    'Sonnet':      dict(input=3,    output=15,   cache_write=3.75,  cache_read=0.3,  cache_write_1h=6),
}

MODELS = {
    'claude-3-5-sonnet-20241022': 'Sonnet',
    'claude-3-7-sonnet-20250219': 'Sonnet',
    'claude-sonnet-4-20250514': 'Sonnet',
    'claude-3-haiku-20240307': 'Haiku 3',
    'claude-3-opus-20240229': 'Opus',
    'claude-opus-4-1-20250805': 'Opus',
    'claude-opus-4-20250514': 'Opus',
 }

ensure_config_persisted(MTOKEN_COSTS, MODELS)
MTOKEN_COSTS, MODELS = load_config()

TOKEN_TYPES = {
    'usage_input_tokens_no_cache': 'input',
    'usage_input_tokens_cache_write_5m': 'cache_write',
    'usage_input_tokens_cache_write_1h': 'cache_write_1h',
    'usage_input_tokens_cache_read': 'cache_read',
    'usage_output_tokens': 'output',
}


def calculate_savings(files:list[str]) -> list[dict]:
    recs = [rec for f in files for rec in read_csv(f)]
    model_ids = {r['model_version'] for r in recs}

    def new_stats():
        return SimpleNamespace(**{x:0 for x in [
            'hitrate',
            'input_cache_reads',
            'input_cost_est_uncached',
            'input_cost',
            'input_savings',
            'input_tokens_total',
            'output_cost',
            'output_tokens_total',
            'total_cost_est',
            'total_cost',
            'total_savings',
            'total_savings_usd'
        ]})

    def calculate_per_model(recs:list[dict], pricing:dict):
        stats = new_stats()

        for token_type, cost_type in TOKEN_TYPES.items():
            ntokens = sum_col(recs, token_type)
            cost_per_token = pricing[cost_type] / 1e6
            usd = ntokens * cost_per_token  # actual cost

            stats.total_cost += usd

            if 'usage_input' in token_type:
                stats.input_cost += usd
                stats.input_tokens_total += ntokens
                stats.input_cost_est_uncached += ntokens * pricing['input'] / 1e6

                if 'usage_input_tokens_cache_read' == token_type:
                    stats.input_cache_reads += ntokens
            else:
                stats.output_cost += usd
                stats.output_tokens_total += ntokens

        stats.total_cost_est = stats.input_cost_est_uncached + stats.output_cost
        return derive_fractions(stats)

    def calculate_totals(model_stats:list):
        out = new_stats()
        for _, stats in model_stats:
            for field, value in vars(stats).items():
                setattr(out, field, getattr(out, field) + value)
        return derive_fractions(out)

    recs_by_model = {mid:[r for r in recs if r['model_version'] == mid] for mid in model_ids}

    unknown_models = set(recs_by_model) - set(MODELS)
    if unknown_models:
        print('[!] Warning: the following model-ids do not have a pricing link established and will be excluded from '
              f'the statistics calculation: {unknown_models}', file=sys.stderr)

    models = [(model_id, mrecs, MTOKEN_COSTS[MODELS[model_id]])
              for model_id, mrecs in recs_by_model.items() if model_id not in unknown_models]

    model_stats = [(model_id, calculate_per_model(d, pricing)) for model_id, d, pricing in models]

    totals = calculate_totals(model_stats)
    totals.per_model = sorted(model_stats, key=lambda x: x[1].total_cost, reverse=True)
    return totals


def derive_fractions(stats):
    stats.hitrate = stats.input_cache_reads / stats.input_tokens_total
    stats.input_savings = 1 - stats.input_cost / stats.input_cost_est_uncached
    stats.total_savings = 1 - stats.total_cost / (stats.input_cost_est_uncached + stats.output_cost)
    return stats


def read_csv(fn:str) -> list[dict]:
    with open(fn) as f:
        return list(csv.DictReader(f))


def sum_col(rows:list[dict], key:str):
    return sum(int(r[key]) for r in rows)
