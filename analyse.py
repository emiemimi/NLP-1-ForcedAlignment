from itertools import count

import pandas as pd
import numpy as np
from collections import defaultdict
import os
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats


def get_df_from_csv(file):
    return pd.read_csv(file, sep=';')


def match(df1, df2):
    # normalize
    df1['utterance'] = df1['utterance'].str.strip(' .,').str.lower()
    df2['utterance'] = df2['utterance'].str.strip(' .,').str.lower()

    # merge on utterances (one to many)
    df_match = df1.merge(df2, on='utterance', suffixes=('_gold', '_other'))

    # add overlap column (overlap = min_end - max_start)
    min_end = np.minimum(df_match["end_gold"], df_match["end_other"])
    max_start = np.maximum(df_match["start_gold"], df_match["start_other"])
    df_match['overlap'] = (min_end - max_start)

    # remove rows where overlap is negative, and reset indexes
    df_match = df_match[df_match['overlap'] > 0].reset_index(drop=True)

    # add duration column for linear regression later
    df_match['duration_gold'] = df_match['end_gold'] - df_match['start_gold']

    return df_match[['utterance', 'duration_gold', 'start_gold', 'start_other', 'end_gold', 'end_other']]


def calculate(df):
    indicators = defaultdict(float)

    df['signed_start_error'] = df['start_other'] - df['start_gold']
    indicators['Signed start error (mean)'] = df['signed_start_error'].mean()
    indicators['Signed start error (median)'] = df['signed_start_error'].median()
    indicators['Signed start error (std)'] = df['signed_start_error'].std()

    df['abs_start_error'] = df['signed_start_error'].abs()
    indicators['Absolute start error (mean)'] = df['abs_start_error'].mean()
    indicators['Absolute start error (median)'] = df['abs_start_error'].median()
    indicators['Absolute start error (std)'] = df['abs_start_error'].std()

    df['signed_end_error'] = df['end_other'] - df['end_gold']
    indicators['Signed end error (mean)'] = df['signed_end_error'].mean()
    indicators['Signed end error (median)'] = df['signed_end_error'].median()
    indicators['Signed end error (std)'] = df['signed_end_error'].std()

    df['abs_end_error'] = df['signed_end_error'].abs()
    indicators['Absolute end error (mean)'] = df['abs_end_error'].mean()
    indicators['Absolute end error (median)'] = df['abs_end_error'].median()
    indicators['Absolute end error (std)'] = df['abs_end_error'].std()

    return df, indicators

def linear_regression(df, x_par, y_par, data_and_aligner):
    sns.regplot(data=df, x=x_par, y=y_par, scatter_kws={'s':10}, line_kws={'color': 'blue', 'linewidth': 0.8})
    plt.xlabel(x_par)
    plt.ylabel(y_par)
    data, forced_aligner = data_and_aligner.split('_')
    plt.title('Gold vs ' + forced_aligner + ': ' + data)
    plt.show()
    plt.savefig('plots/linreg_' + data_and_aligner + '.png')
    slope, intercept, r_value, p_value, std_err = stats.linregress(df[x_par], df[y_par])
    return {
            'Intercept': intercept,
            'Coefficient': slope,
            'R-squared': r_value**2,
            'P-value': p_value
            }


file_pairs = [
    ('data/gold/sentence3_manual_words.csv', 'data/MAUS/sentence3_MAUS_words.csv'),
    ('data/gold/sentence3_manual_words.csv', 'data/Whisper/sentence3_whisper.csv'),
    ('data/gold/s1102a_words.csv', 'data/MAUS/s1102a_MAUS_words.csv'),
    ('data/gold/s1102a_words.csv', 'data/Whisper/s1102a_whisper.csv'),
    ('data/gold/s1701a_words.csv', 'data/MAUS/s1701a_MAUS_words.csv'),
    ('data/gold/s1701a_words.csv', 'data/Whisper/s1701a_whisper.csv')
]

for pair in file_pairs:
    print(pair[0], 'VS', pair[1])
    gold = get_df_from_csv(pair[0])
    other = get_df_from_csv(pair[1])
    df_match = match(gold, other)
    df, dict = calculate(df_match)
    print('Gold length:', len(gold), '\t\tNb of matches found:', len(df), '\t\tMissing:', len(gold) - len(df))
    print('ERROR STATS')
    for key, value in dict.items():
        print('\t', key, '\t', round(value,3))
    path, ext = os.path.splitext(pair[1])
    info = '_'.join(path.split('/')[-1].split('_')[:2])
    df_without_non_words = df[~df['utterance'].isin(['<iver>', '<laugh>', '<noise>', '<sil>', '<vocnoise>'])]
    linreg = linear_regression(df[df['duration_gold'] < 1], 'duration_gold', 'signed_start_error', info)
    print('LINEAR REGRESSION: duration <- signed start error')
    for key, value in linreg.items():
        print('\t', key, '\t', round(value,3))
    print()
