from sqlalchemy import Table, MetaData, \
    Column, String, Float, Integer, Boolean


def Favorites(metadata: MetaData) -> Table:
    return Table(
        'favorites',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, nullable=False),
        Column('folder_name', String, nullable=False),
        Column('cover', String, nullable=False),
        Column('description', String),
        Column('author', String),
        Column('score', Float),
        Column('notify', Boolean, default=False),
        Column('md_id', String, unique=True),
        Column('ml_id', Integer, unique=True),
        Column('ms_id', String, unique=True),
        Column('mc_id', String, unique=True),
        Column('mf_id', String, unique=True),
        Column('mx_id', String, unique=True),
        Column('tcb_id', String, unique=True),
        Column('tsct_id', String, unique=True),
        Column('op_id', String, unique=True),
        Column('gkk_id', String, unique=True),
        Column('lmorg_id', String, unique=True),
    )

favorite_columns = [
    'notify',
    'md_id', 
    'ml_id', 
    'ms_id', 
    'mc_id', 
    'mf_id', 
    'mx_id', 
    'tcb_id', 
    'tsct_id', 
    'op_id', 
    'gkk_id', 
    'lmorg_id'
]
