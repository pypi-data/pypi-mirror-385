from _typeshed import Incomplete
from enum import Enum as Enum
from pybiotech.loaders.sdf_loader import SDFLoader as SDFLoader
from pybiotech.type.nih.pubchem import ALNPCompound as ALNPCompound, ALNPConformer as ALNPConformer, EInputType as EInputType, EOperationType as EOperationType, EOutputType as EOutputType
from typing import Callable

logger: Incomplete
url_compound_partten: str
url_compound_conformer_partten: str
url_conformers_partten: str

def get_compound(cid_list: list[str], include_conformer: bool = False, progress_callback: Callable[[int, int, str], None] | None = None, is_error_continue: bool = False) -> dict[str, ALNPCompound]: ...

url_compund_similarity_partten: str

def get_similarity_compound(input: EInputType, value: str | int, operation: EOperationType, output: EOutputType, threshold: int = 90, max_records: int = 10) -> list[str]: ...
