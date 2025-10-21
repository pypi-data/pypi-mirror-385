import numpy as np
from typing import List, Tuple, Union

PixelScales = Union[Tuple[float], Tuple[float, float], float]


from autoarray.mask.mask_1d import Mask1D
from autoarray.mask.mask_2d import Mask2D

Mask1D2DLike = Union[Mask1D, Mask2D]


from autoarray.structures.arrays.uniform_1d import Array1D
from autoarray.structures.arrays.uniform_2d import Array2D

Array1D2DLike = Union[Array1D, Array2D]


from autoarray.structures.grids.uniform_1d import Grid1D
from autoarray.structures.grids.uniform_2d import Grid2D
from autoarray.structures.grids.irregular_2d import Grid2DIrregular

Grid1D2DLike = Union[np.ndarray, Grid1D, Grid2D, Grid2DIrregular]
Grid2DLike = Union[np.ndarray, Grid2D, Grid2DIrregular]

from autoarray.structures.arrays.irregular import ArrayIrregular
from autoarray.structures.visibilities import Visibilities
from autoarray.structures.visibilities import VisibilitiesNoiseMap

DataLike = Union[
    np.ndarray, Array1D, Array2D, ArrayIrregular, Visibilities, VisibilitiesNoiseMap
]

from autoarray.operators.transformer import TransformerDFT
from autoarray.operators.transformer import TransformerNUFFT

Transformer = Union[TransformerDFT, TransformerNUFFT]


from autoarray.layout.region import Region1D
from autoarray.layout.region import Region2D

Region1DLike = Union[Region1D, Tuple[int, int]]
Region1DList = Union[List[Region1D], List[Tuple[int, int]]]
Region2DLike = Union[Region2D, Tuple[int, int, int, int]]
Region2DList = Union[List[Region2D], List[Tuple[int, int, int, int]]]
