from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    folder_name = Column(String, nullable=False)
    cover = Column(String, nullable=False)
    description = Column(String)
    author = Column(String)
    score = Column(Float)
    notify = Column(Boolean, default=False)
    md_id = Column(String, unique=True)
    ml_id = Column(Integer, unique=True)
    ms_id = Column(String, unique=True)
    mc_id = Column(String, unique=True)
    mf_id = Column(String, unique=True)
    mx_id = Column(String, unique=True)
    tcb_id = Column(String, unique=True)
    tsct_id = Column(String, unique=True)
    op_id = Column(String, unique=True)
    gkk_id = Column(String, unique=True)
    lmorg_id = Column(String, unique=True)

    def __init__(
            self, name: str = None, folder_name: str = None, cover: str = None, 
            description: str = None, author: str = None, score: float = None, 
            notify: bool = False, md_id: str = None, ml_id: int = None, 
            ms_id: str = None, mc_id: str = None, mf_id: str = None, 
            mx_id: str = None, tcb_id: str = None, tsct_id: str = None, 
            op_id: str = None, gkk_id: str = None, lmorg_id: str = None
    ) -> None:
        self.name = name
        self.folder_name = folder_name
        self.cover = cover
        self.description = description
        self.author = author
        self.score = score
        self.notify = notify
        self.md_id = md_id
        self.ml_id = ml_id
        self.ms_id = ms_id
        self.mc_id = mc_id
        self.mf_id = mf_id
        self.mx_id = mx_id
        self.tcb_id = tcb_id
        self.tsct_id = tsct_id
        self.op_id = op_id
        self.gkk_id = gkk_id
        self.lmorg_id = lmorg_id

    def __repr__(self) -> str:
        return f'<Favorite {self.name}>'

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
