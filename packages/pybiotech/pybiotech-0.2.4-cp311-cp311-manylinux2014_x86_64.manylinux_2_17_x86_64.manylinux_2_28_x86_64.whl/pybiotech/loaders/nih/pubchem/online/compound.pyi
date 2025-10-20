from _typeshed import Incomplete
from pybiotech.loaders.sdf_loader import SDFLoader as SDFLoader
from pybiotech.type.nih.pubchem import ALNPCompound as ALNPCompound, ALNPConformer as ALNPConformer

logger: Incomplete
url_compound_partten: str
url_compound_conformer_partten: str
url_conformers_partten: str

def get_compound(cid_list: list[str], include_conformer: bool = False) -> dict[str, ALNPCompound]: ...

test_data: Incomplete
