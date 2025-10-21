import logging
from pathlib import Path
from typing import Optional

import pyproj
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


DEFAULT_CRS = pyproj.CRS.from_user_input("EPSG:4326")


def parse_crs(v) -> pyproj.CRS:
    if v is None or v.strip() == "":
        return str(DEFAULT_CRS)
    else:
        try:
            # Check that the crs can be parsed and store as WKT
            crs_obj = pyproj.CRS.from_user_input(v)
            return str(crs_obj)
        except pyproj.exceptions.CRSError as e:
            logger.error(
                f"Provided CRS {v} could not be parsed, defaulting to EPSG:4326"
            )
            raise e


def crs_validator(field: str) -> classmethod:
    decorator = field_validator(field, mode="before")
    validator_func = decorator(parse_crs)
    return validator_func


class BoundingBox(BaseModel, arbitrary_types_allowed=True):
    west: float
    east: float
    north: float
    south: float
    base: Optional[float] = None
    height: Optional[float] = None
    crs: Optional[str] = None

    # validators
    _parse_crs: classmethod = crs_validator("crs")


class sen2like_options(BaseModel):
    doGeometry: Optional[bool] = True
    doStitching: Optional[bool] = True
    doGeometryCheck: Optional[bool] = True
    doToa: Optional[bool] = True
    doInterCalibration: Optional[bool] = True
    doAtmcor: Optional[bool] = True
    doNbar: Optional[bool] = True
    doSbaf: Optional[bool] = True


class Sen2LikeParameters(BaseModel):
    """Pydantic model of sen2like supported parameters."""

    spatial_extent: BoundingBox
    temporal_extent: list
    user_workspace: Path
    s2_paths: Optional[list] = []
    target_resolution: Optional[int] = None
    target_product: Optional[str] = Field(pattern=r"L2F|L2H|l2f|l2h", default="L2F")
    bands: list = []
    options: Optional[sen2like_options] = None
    cloud_cover: int = 50

    @field_validator("target_resolution")
    def check_resolution(cls, v):
        if v not in [None, 10, 20, 60]:
            raise ValueError("Resolution must be set to 10, 20 or 60.")
        return v

    @property
    def root_path(self) -> Path:
        return self.user_workspace / "SEN2LIKE"

    @property
    def output_path(self) -> Path:
        return self.root_path / "output"


def get_output_stac_item_paths(
    sen2like_parameters: Sen2LikeParameters, target_product: str = "L2F"
) -> list[Path]:
    stac_item_paths = []

    for tile in sen2like_parameters.output_path.iterdir():
        for item in tile.iterdir():
            if (
                item.suffix == ".SAFE"
                and target_product.upper() in item.name
                and (item.name.startswith("S2") or item.name.startswith("LS"))
            ):  # result either L2F or L2H
                item_path = item / (item.stem + ".json")
                if item_path.exists():
                    stac_item_paths.append(item_path)

    logger.info(
        f"Found {len(stac_item_paths)} STAC items in {sen2like_parameters.output_path}"
    )

    return stac_item_paths
