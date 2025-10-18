import argparse
import sys
from glob import glob
from .domain import calculate_savings

def parse_args():
    parser = argparse.ArgumentParser(
        description='Provides Anthropic Claude caching, model use and cost statistics'
    )

    parser.add_argument('-m', action='store_true', help='Show per-model breakdown')
    parser.add_argument('files', nargs='+', help='Exported API usage CSV files from the console')

    if len(sys.argv) < 2:
        sys.argv.append('-h')
    return parser.parse_args()


def main():
    opts = parse_args()
    files = [f for p in opts.files for f in glob(p)]
    stats = calculate_savings(files)

    def report(stats, indent=0):
        def log(*args):
            print((' '*indent), *args, sep='')
        log(f'Input cache hit   {stats.hitrate * 100:.0f} %')
        log(f'Input savings     {stats.input_savings * 100:.0f} %')
        log(f'Total savings     {stats.total_savings * 100:.0f} %')
        log()
        log(f'Total cost        $ {stats.total_cost:.2f}')
        log(f'Est cache-less    $ {stats.total_cost_est:.2f}')
        log()
        itt, ott = f'{stats.input_tokens_total:,}', f'{stats.output_tokens_total:,}'
        log(f'Input tokens      {itt:<12s} | $ {stats.input_cost:.2f}')
        log(f'Output tokens     {ott:<12s} | $ {stats.output_cost:.2f}')
        log(f'Input/output tok  {stats.input_tokens_total / stats.output_tokens_total:.0f}x')

    print('==[ Total ]' + '='*36 + '\n')
    report(stats)

    if not opts.m:
        return

    print('\n==[ Per model ]' + '='*32)

    for model_id, mstat in stats.per_model:
        cost_frac = mstat.total_cost / stats.total_cost
        use_frac = (mstat.output_tokens_total + mstat.input_tokens_total) / (
            stats.output_tokens_total + stats.input_tokens_total)
        print(f'\n{model_id:26}  (use-cost: {use_frac*100:.0f}% {cost_frac*100:.0f}%)')
        report(mstat, 2)

if __name__ == '__main__':
    main()
