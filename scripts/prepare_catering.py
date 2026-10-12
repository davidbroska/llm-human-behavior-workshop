"""Create a readable catering table from the unchanged Cui effect tables."""
import hashlib
import json
from pathlib import Path
import pandas as pd


def prepare_catering():
    """Select and rename Study 1 means without changing values.

    Returns:
        pandas.DataFrame: Nine comparisons for each of three models.
    Notes:
        Group 1 is the point offer and group 2 is the named range.
        Human means were verified against Ames and Mason Table 1.
    """
    folder = Path(__file__).resolve().parents[1] / 'data/workshop/cui'
    tables, sources = [], []
    names = {'bolstering range':'Bolstering range','bracketing range':'Bracketing range','backdown range':'Backdown range'}
    for model,prefix in [('GPT','gpt'),('Claude','claude'),('DeepSeek','deepseek')]:
        path = folder / f'enhanced_dataset_{model}_main.csv'
        d = pd.read_csv(path)
        d = d[d.study_id=='JPSP_9_1'].copy()
        d['range'] = d.IV.str.extract(r'point vs\. (.*)\)',expand=False).map(names)
        if len(d)!=9 or d['range'].isna().any():
            raise ValueError('Expected nine mapped comparisons per model.')
        d['model'] = model
        columns = {'DV':'outcome','human_mean_group1':'human_point','human_mean_group2':'human_range',
                   prefix+'_mean_group1':'model_point',prefix+'_mean_group2':'model_range'}
        d = d.rename(columns=columns)
        for name in ['human_point','human_range','model_point','model_range']:
            d[name] = pd.to_numeric(d[name],errors='raise')
        tables.append(d[['model','study_id','effect_id','range','outcome','human_point','human_range','model_point','model_range']])
        sources.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    result = pd.concat(tables,ignore_index=True)
    result.to_csv(folder/'catering_comparisons.csv',index=False)
    (folder/'catering_provenance.json').write_text(json.dumps({'sources':sources,'changes':'Select JPSP_9_1; rename columns and condition labels; preserve condition means. Original inputs and provenance remain included.','human_reference':'Ames and Mason (2015), Table 1; rounded human means.','orientation':'range minus point, specified independently of the observed effect.','license':'No dataset licence declared by OSF; no new licence assigned.'},indent=2)+'\n')
    return result


if __name__=='__main__':
    print(prepare_catering().shape)
