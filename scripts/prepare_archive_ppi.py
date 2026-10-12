"""Prepare response-level PPI exploration across the Ashokkumar archive."""

import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile
import warnings
import zipfile

import numpy as np
import pandas as pd
from workshop_helpers import ppi_correlation, effective_sample_size
from prepare_ashokkumar import _party


def prepare_archive_ppi():
    """Match party predictions and calculate package-based power summaries.

    Returns:
        dict: Coverage, source and planning assumptions.
    Notes:
        Includes all unordered condition pairs with sufficient complete responses.
        These exploratory pairs are not the authors' selected hypotheses.
    """
    root = Path(__file__).resolve().parents[1]
    source = root / 'studies/ashokkumar2026_nature/data_code/codeocean_capsule_9843791_v1_export.zip'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != '96e13b405e97700e041addb37a49f20d26d8c9d3d50d2ca8ed1b22121b7007f7':
        raise ValueError('The source capsule has changed.')
    output = root / 'data/workshop/ashokkumar'
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(source) as archive:
            for name in ['rct_responses.RDS', 'llm_responses.RDS']:
                (folder / name).write_bytes(archive.read('data/' + name))
        reader = folder / 'read.R'
        reader.write_text('''
f <- commandArgs(trailingOnly=TRUE)[1]
h <- readRDS(file.path(f,'rct_responses.RDS'))
rows <- lapply(seq_len(nrow(h)),function(i) {
 d <- h$data[[i]]
 if (!'pid_3' %in% names(d)) d$pid_3 <- NA_character_
 d$source_row <- seq_len(nrow(d))
 d$study <- h$study[i]
 d$outcome <- h$outcome.name[i]
 d[,c('study','outcome','source_row','condition.name','pid_3','y')]
})
write.csv(do.call(rbind,rows),file.path(f,'human.csv'),row.names=FALSE,na='')
p <- readRDS(file.path(f,'llm_responses.RDS'))
p <- p[p$model=='gpt-4',c('study','outcome.name','condition.name','prompt','expectation',
                         'weight','scale_flip','outcome_scale_min','outcome_scale_max')]
write.csv(p,file.path(f,'predicted.csv'),row.names=FALSE,na='')
''')
        subprocess.run(['Rscript', str(reader), str(folder)], check=True)
        human = pd.read_csv(folder / 'human.csv')
        predicted = pd.read_csv(folder / 'predicted.csv')
    predicted['pid_3'] = predicted.prompt.map(_party)
    unparsed = int(predicted.pid_3.isna().sum())
    predicted = predicted.dropna(subset=['pid_3']).copy()
    predicted['outcome'] = predicted['outcome.name']
    predicted['Yhat'] = np.where(predicted.scale_flip,
                                 predicted.outcome_scale_max + predicted.outcome_scale_min - predicted.expectation,
                                 predicted.expectation)
    predicted['weighted'] = predicted.Yhat * predicted.weight
    keys = ['study','outcome','condition.name','pid_3']
    groups = predicted.groupby(keys)[['weighted','weight']].sum().reset_index()
    groups = groups[groups.weight > 0].copy()
    groups['Yhat'] = groups.weighted / groups.weight
    joined = human.merge(groups[keys + ['Yhat']], on=keys, how='left', validate='many_to_one')
    joined = joined.rename(columns={'y':'Y','condition.name':'condition'})
    coverage = []
    for (study,outcome),d in joined.groupby(['study','outcome']):
        complete = np.isfinite(d.Y) & np.isfinite(d.Yhat)
        coverage.append([study,outcome,len(d),int(d.Y.isna().sum()),int(d.Yhat.isna().sum()),int(complete.sum())])
    pd.DataFrame(coverage,columns=['study','outcome','source_rows','missing_Y','missing_Yhat','complete_rows']).to_csv(output/'archive_ppi_coverage.csv',index=False)
    paired = joined[np.isfinite(joined.Y) & np.isfinite(joined.Yhat)].copy()
    paired = paired[['study','outcome','source_row','condition','Y','Yhat']]
    paired.to_csv(output/'archive_responses.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    rows = []
    for (study,outcome),d in paired.groupby(['study','outcome']):
        for reference,comparison in itertools.combinations(sorted(d.condition.unique()),2):
            subset = d[d.condition.isin([reference,comparison])]
            t = (subset.condition == comparison).to_numpy().astype(float)
            y = subset.Y.to_numpy()
            p = subset.Yhat.to_numpy()
            result = dict(study=study,outcome=outcome,reference=reference,comparison=comparison,
                          complete_n=len(y),n_reference=int((t==0).sum()),n_comparison=int((t==1).sum()))
            result['status'] = 'ok'
            if min(result['n_reference'], result['n_comparison']) < 10 or y.var()==0:
                result['status'] = 'Insufficient variation or fewer than 10 complete people in one condition'
            else:
                X = np.column_stack([np.ones(len(y)),t])
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter('error', RuntimeWarning)
                        rho = ppi_correlation(X,y,p)
                    if not np.isfinite(rho):
                        raise ValueError('Undefined PPI correlation')
                    n = len(y) // 2
                    N = len(y) - n
                    ess = effective_sample_size(rho,n,N)
                    result.update(ppi_corr=rho,labeled_n=n,unlabeled_N=N,
                                  effective_n=ess,ess_gain_percent=100*(ess/n-1))
                except (ValueError,RuntimeWarning,np.linalg.LinAlgError,OverflowError) as e:
                    result['status'] = str(e)
            rows.append(result)
    summary = pd.DataFrame(rows)
    summary.to_csv(output/'archive_ppi.csv',index=False)
    provenance = dict(ppi_reference_commit='2dc0ceede320ddf81b4d1050df04fbd1f48bd31b', source_sha256=digest,source_url='https://codeocean.com/capsule/9843791/tree/v1',
                      source_human_studies=int(human.study.nunique()),paired_studies=int(paired.study.nunique()),
                      source_human_rows=len(human),complete_response_rows=len(paired),
                      unparsed_model_party_rows=unparsed,pairwise_rows=len(summary),
                      valid_pairwise_rows=int((summary.status=='ok').sum()),
                      matching='Weighted GPT-4 means within study/outcome/condition/persona party; all available templates pooled. No human outcomes used. Same original outcome scale for Y and Yhat.',
                      selection='All unordered condition pairs, lexicographic reference; >=10 complete people per arm and nonconstant human outcomes. Check original design before treating a pair as a randomized causal contrast. No verified IDs across outcomes.',
                      planning='Fixed half-labeled/half-unlabeled design; PPI correlation uses all complete responses as pilot data. ESS = n / (1 - rho**2 * N/(n+N)), idealized optimal weighting; not a realized precision gain.',
                      coverage='Source studies without matched predictions remain in archive_ppi_coverage.csv; numerical failures retained with status. Pairs share people and are dependent.',license='CC0-1.0')
    return provenance


if __name__ == '__main__':
    print(json.dumps(prepare_archive_ppi(),indent=2))
