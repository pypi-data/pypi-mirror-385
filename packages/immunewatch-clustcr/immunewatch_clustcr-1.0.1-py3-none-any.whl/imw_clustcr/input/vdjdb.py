import pandas as pd

def parse_vdjdb(filename, q=0):
    """
    Parse files in the VDJdb format.
    q-score defines the quality of the database entry (3 > 2 > 1 > 0).
    """
    vdjdb = pd.read_csv(filename, sep='\t',low_memory=False)
    vdjdb = vdjdb[vdjdb['species']=='HomoSapiens']
    vdjdb = vdjdb[['cdr3.alpha', 'v.alpha', 
                   'cdr3.beta', 'v.beta',
                   'vdjdb.score', 'meta.subject.id', 'antigen.epitope']]
    vdjdb = vdjdb[vdjdb['vdjdb.score'] >= q]  # Quality score cut-off
    vdjdb = vdjdb[~vdjdb['v.alpha'].str.contains("/", na=False)]  # Remove ambiguous entries
    vdjdb = vdjdb[~vdjdb['v.beta'].str.contains("/", na=False)]  # Remove ambiguous entries
    vdjdb.drop(columns=['vdjdb.score'], inplace=True)
    vdjdb.rename(columns={'meta.subject.id':'subject'}, inplace=True)
    vdjdb = vdjdb[vdjdb['subject'].astype(bool)]
    vdjdb = vdjdb[~vdjdb.subject.str.contains('mouse', na=False)]
    vdjdb['count'] = [1] * len(vdjdb)
    vdjdb.drop_duplicates(inplace=True)
    return vdjdb