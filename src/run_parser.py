from ParseUtils import get_series_parsed_episodes


def run_parser():
    all_series_parsed = []
    all_series = ['StarTrek', 'NextGen', 'DS9', 'VOY', 'Enterprise', 'DIS', 'PIC', 'LD', 'movies']
    for series in all_series:
        episodes_parsed = get_series_parsed_episodes(series)
        all_series_parsed.append({
            'series': series,
            'episodes_parsed': episodes_parsed
        })
    return all_series_parsed


parsed = run_parser()
