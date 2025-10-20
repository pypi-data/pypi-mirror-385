from _typeshed import Incomplete
from pydantic import BaseModel

class ALNPConformer(BaseModel):
    PUBCHEM_COMPOUND_CID: str
    PUBCHEM_CONFORMER_ID: str
    ROW: str
    model_config: Incomplete
    def convert_pubchem_cid(cls, v): ...

class ALNPCompound(BaseModel):
    PUBCHEM_COMPOUND_CID: str
    ROW: str
    CONFORMER_ID: list[str] | None
    CONFORMERS: dict[str, ALNPConformer] | None
    model_config: Incomplete
    def convert_pubchem_cid(cls, v): ...
