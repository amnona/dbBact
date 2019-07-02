import psycopg2

from .utils import debug


def get_primers(con, cur):
    '''Get information about all the sequencing primers used in dbbact

    Returns
    -------
    primers: list of dict of {
        'primerid': int
            dbbact internal id of the primer region (i.e. 1 for v4, etc.)
        'name': str,
            name of the primer region (i.e. 'v4', 'its1', etc.)
        'fprimer': str
        'rprimer: str
            name of the forward and reverse primers for the region (i.e. 515f, etc.)
        'fprimerseq': str
            the concensus sequence for the forward primer
    '''
    debug(1, 'get_primers')

    primers = []
    cur.execute('SELECT id, regionname, forwardprimer, reverseprimer, fprimerseq FROM PrimersTable')
    res = cur.fetchall()
    for cres in res:
        cprimer = {}
        cprimer['primerid'] = cres['id']
        cprimer['name'] = cres['regionname']
        cprimer['fprimer'] = cres['forwardprimer']
        cprimer['rprimer'] = cres['reverseprimer']
        cprimer['fprimerseq'] = cres['fprimerseq']
        primers.append(cprimer)
    debug(1, 'found %d primers' % len(primers))
    return '', primers


def GetNameFromID(con, cur, primer_id):
    '''Get primer region name from id

    Parameters
    ----------
    con, cur:
    primer_id: int
        the id of the primer region

    Returns
    -------
    err: str
        empty strung ('') if ok, otherwise error encountered
    name: str
        name of the primer region
    '''
    cur.execute('SELECT RegionName from PrimersTable WHERE id=%s', [primer_id])
    if cur.rowcount == 0:
        msg = 'primerid %d not found' % primer_id
        debug(5, msg)
        return msg, ''
    res = cur.fetchone()
    return '', res['regionname']


def GetIdFromName(con, cur, name):
    """
    get id of primer based on regionName

    input:
    regionName : str
        name of the primer region (i.e. 'V4')

    output:
    id : int
        the id of the region (>0)
        -1 if region not found
        -2 if database error
    """
    name = name.lower()
    try:
        cur.execute('SELECT id from PrimersTable where regionName=%s', [name])
        rowCount = cur.rowcount
        if rowCount == 0:
            # region not found
            return -1
        else:
            # Return the id
            res = cur.fetchone()
            return res[0]
    except psycopg2.DatabaseError as e:
        debug(4, 'Error %s' % e)
        # DB exception
        return -2


def AddPrimerRegion(con, cur, regionname, forwardprimer='', reverseprimer='', userid=None, commit=True):
    '''Add a new region to the primers table

    Parameters
    ----------
    regionname: str
        The name of the primer region to add (i.e 'V4')
    forward_primer, reverse_primer: str, optional
        name (i.e. 515f) or sequence of the corresponding primer used to amplify the region
    userid: int, optional
        the user adding the primer

    Returns
    -------
    empty string('') if ok, error string if error encountered
    '''
    regionname = regionname.lower()
    forwardprimer = forwardprimer.lower()
    reverseprimer = reverseprimer.lower()
    cid = GetIdFromName(con, cur, regionname)
    if cid != -1:
        debug(2, 'region %s already exists in PrimersTable' % regionname)
        return 'region %s already exists in PrimersTalbe' % regionname
    try:
        cur.execute('INSERT INTO PrimersTable (regionname, forwardprimer, reverseprimer, iduser) VALUES (%s, %s, %s, %s)', [regionname, forwardprimer, reverseprimer, userid])
        if commit:
            con.commit()
        debug(2, 'primer region %s added' % regionname)
        return ''
    except psycopg2.DatabaseError as e:
        debug(4, 'Database error %s encountered when adding primer region %s' % (e, regionname))
        return 'db error when adding primer region'
