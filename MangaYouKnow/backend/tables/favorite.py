from sqlmodel import SQLModel, Field


class Favorite(SQLModel, table=True):
    __tablename__ = 'favorites'
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    folder_name: str = Field(nullable=False)
    cover: str = Field(nullable=False)
    source: str = Field(nullable=False)
    source_id: str = Field(nullable=False)
    type: str = Field(nullable=False)
    description: str = None
    author: str = None
    score: float = None
    notify: bool = False
    # md_id: str = Field(unique=True, nullable=True)
    # ml_id: str = Field(unique=True, nullable=True)
    # ms_id: str = Field(unique=True, nullable=True)
    # mc_id: str = Field(unique=True, nullable=True)
    # mf_id: str = Field(unique=True, nullable=True)
    # mx_id: str = Field(unique=True, nullable=True)
    # tcb_id: str = Field(unique=True, nullable=True)
    # tsct_id: str = Field(unique=True, nullable=True)
    # op_id: str = Field(unique=True, nullable=True)
    # gkk_id: str = Field(unique=True, nullable=True)
    # lmorg_id: str = Field(unique=True, nullable=True)

# favorite_columns = [
#     'notify',

# ]
