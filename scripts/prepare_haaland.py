"""Prepare Haaland and Roth outcomes from the Ashokkumar capsule."""

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

import numpy as np
import pandas as pd
from prepare_ashokkumar import _party


def prepare_haaland():
    """Build three outcome extracts with explicitly assigned party predictions.

    Returns:
        dict: Source hash, matching rule and missingness by outcome.
    Notes:
        Original RDS objects are decoded with base R; no source code is run.
        Source-row identifiers are outcome-specific, not cross-outcome IDs.
    """
    root = Path(__file__).resolve().parents[1]
    source = root / 'studies/ashokkumar2026_nature/data_code/codeocean_capsule_9843791_v1_export.zip'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != '96e13b405e97700e041addb37a49f20d26d8c9d3d50d2ca8ed1b22121b7007f7':
        raise ValueError('Source capsule does not match the pinned version.')
    output = root / 'data/workshop/ashokkumar'
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(source) as archive:
            for name in ['rct_responses.RDS', 'llm_responses.RDS']:
                (folder / name).write_bytes(archive.read('data/' + name))
        reader = folder / 'read.R'
        reader.write_text('''
f <- commandArgs(trailingOnly=TRUE)[1]
h <- readRDS(file.path(f, 'rct_responses.RDS'))
h <- h[h$study == 'Haaland874', ]
rows <- lapply(seq_len(nrow(h)), function(i) {
 d <- h$data[[i]]
 d$source_row <- seq_len(nrow(d))
 d$outcome <- h$outcome.name[i]
 d[, c('source_row','outcome','condition.name','pid_3','y')]
})
write.csv(do.call(rbind, rows), file.path(f,'human.csv'), row.names=FALSE, na='')
p <- readRDS(file.path(f, 'llm_responses.RDS'))
p <- p[p$study == 'Haaland874' & p$model == 'gpt-4', ]
p <- p[, c('outcome.name','condition.name','prompt','expectation','weight',
           'scale_flip','outcome_scale_min','outcome_scale_max')]
write.csv(p, file.path(f,'predicted.csv'), row.names=FALSE, na='')
''')
        subprocess.run(['Rscript', str(reader), str(folder)], check=True)
        human = pd.read_csv(folder / 'human.csv')
        predicted = pd.read_csv(folder / 'predicted.csv')
    predicted['pid_3'] = predicted.prompt.map(_party)
    if predicted.pid_3.isna().any():
        raise ValueError('An unrecognized persona party prevents matching.')
    if not ((predicted.outcome_scale_min == 1) & (predicted.outcome_scale_max == 5)).all():
        raise ValueError('Expected all outcomes on 1–5 scales.')
    predicted['Yhat'] = np.where(predicted.scale_flip, 6 - predicted.expectation, predicted.expectation)
    predicted['outcome'] = predicted['outcome.name']
    predicted['weighted_prediction'] = predicted.Yhat * predicted.weight
    keys = ['outcome', 'condition.name', 'pid_3']
    groups = predicted.groupby(keys)[['weighted_prediction', 'weight']].sum().reset_index()
    if (groups.weight <= 0).any():
        raise ValueError('Prediction weights must have positive group totals.')
    groups['Yhat'] = groups.weighted_prediction / groups.weight
    paired = human.merge(groups[keys + ['Yhat']], on=keys, how='left', validate='many_to_one')
    counts = []
    for outcome, d in paired.groupby('outcome'):
        counts.append({'outcome': outcome, 'source_rows': len(d),
                       'missing_Y': int(d.y.isna().sum()),
                       'missing_Yhat': int(d.Yhat.isna().sum()),
                       'complete_rows': int(d[['y', 'Yhat']].notna().all(axis=1).sum())})
    paired = paired.dropna(subset=['y', 'Yhat']).copy()
    if set(paired['condition.name']) != {'CONTROL', 'TREATMENT'}:
        raise ValueError('Unexpected experimental conditions.')
    paired['treated'] = (paired['condition.name'] == 'TREATMENT').astype(int)
    paired = paired.rename(columns={'y': 'Y'})
    paired = paired[['outcome', 'source_row', 'treated', 'Y', 'Yhat']]
    if not paired[['Y', 'Yhat']].ge(1).all().all() or not paired[['Y', 'Yhat']].le(5).all().all():
        raise ValueError('Outcome outside its documented range.')
    paired.to_csv(output / 'haaland_responses.csv', index=False)
    groups.to_csv(output / 'haaland_party_predictions.csv', index=False)
    provenance = {'source_url': 'https://codeocean.com/capsule/9843791/tree/v1',
                  'source_sha256': digest, 'study': 'Haaland874', 'model': 'gpt-4',
                  'matching': 'Weighted persona predictions by outcome, condition and party; all GPT-4 templates pooled. Leaners assigned to their named party. No human outcomes used in prediction.',
                  'scale': 'Original 1–5 scales, larger values mean greater seriousness or support.',
                  'identifier': 'source_row is local to each outcome table; do not join outcomes by row position.',
                  'exclusions': counts, 'license': 'CC0-1.0'}
    (output / 'haaland_provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    return provenance


if __name__ == '__main__':
    print(json.dumps(prepare_haaland(), indent=2))
