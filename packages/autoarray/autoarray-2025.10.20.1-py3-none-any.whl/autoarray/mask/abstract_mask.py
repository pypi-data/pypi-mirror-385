from __future__ import annotations

from abc import ABC
import logging
import numpy as np
from typing import Dict

from autoconf.fitsable import output_to_fits

from autoarray.abstract_ndarray import AbstractNDArray

from autoarray import type as ty

logging.basicConfig()
logger = logging.getLogger(__name__)


class Mask(AbstractNDArray, ABC):
    pixel_scales = None

    # noinspection PyUnusedLocal
    def __init__(
        self,
        mask: np.ndarray,
        origin: tuple,
        pixel_scales: ty.PixelScales,
        *args,
        **kwargs,
    ):
        """
        An abstract class for a mask that represents data structure that can be in 1D, 2D or other shapes.

        When applied to data it extracts or masks the unmasked image pixels corresponding to mask entries
        that are (`False` or 0).

        The mask also defines the geometry of the data structure it is paired with, for example how its pixels convert
        to physical units via the pixel_scales and origin parameters and a grid which is used for
        perform calculations via super-sampling.

        Parameters
        ----------
        mask
            The ndarray containing the bool's representing the mask, where `False` signifies an entry is
            unmasked and used in calculations.
        pixel_scales
            The scaled units to pixel units conversion factors of every pixel. If this is input as a float, it is
            converted to a (float, float) structure.
        origin
            The origin of the mask's coordinate system in scaled units.
        """

        # noinspection PyArgumentList
        mask = mask.astype("bool")
        super().__init__(mask)

        self.pixel_scales = pixel_scales
        self.origin = origin

    @property
    def mask(self):
        return self._array

    def __array_finalize__(self, obj):
        if isinstance(obj, Mask):
            self.pixel_scales = obj.pixel_scales
            self.origin = obj.origin
        else:
            self.pixel_scales = None

    @property
    def pixel_scale(self) -> float:
        """
        For a mask with dimensions two or above check that are pixel scales are the same, and if so return this
        single value as a float.
        """
        return self.pixel_scales[0]

    @property
    def header_dict(self) -> Dict:
        """
        Returns the pixel scale of the mask as a header dictionary, which can be written to a .fits file.

        If the array has different pixel scales in 2 dimensions, the header will contain both pixel scales as separate
        y and x entries.

        Returns
        -------
        A dictionary containing the pixel scale of the mask, which can be output to a .fits file.
        """

    @property
    def dimensions(self) -> int:
        return len(self.shape)

    def output_to_fits(self, file_path, overwrite=False):
        """
        Write the Mask to a .fits file.

        Before outputting a 2D NumPy array mask, the array may be flipped upside-down using np.flipud depending on
        the project config files. This is for Astronomy projects so that structures appear the same orientation
        as `.fits` files loaded in DS9.

        Parameters
        ----------
        file_path
            The full path of the file that is output, including the file name and `.fits` extension.
        overwrite
            If `True` and a file already exists with the input file_path the .fits file is overwritten. If `False`, an
            error is raised.

        Returns
        -------
        None

        Examples
        --------
        mask = Mask2D(mask=np.full(shape=(5,5), fill_value=False))
        mask.output_to_fits(file_path='/path/to/file/filename.fits', overwrite=True)
        """
        output_to_fits(
            values=self.astype("float"),
            file_path=file_path,
            overwrite=overwrite,
            header_dict=self.header_dict,
            ext_name="mask",
        )

    @property
    def pixels_in_mask(self) -> int:
        """
        The total number of unmasked pixels (values are `False`) in the mask.
        """
        return (np.size(self._array) - np.sum(self._array)).astype(int)

    @property
    def is_all_true(self) -> bool:
        """
        Returns `True` if all pixels in a mask are `True`, else returns `False`.
        """
        return self.pixels_in_mask == 0

    @property
    def is_all_false(self) -> bool:
        """
        Returns `False` if all pixels in a mask are `False`, else returns `True`.
        """
        return self.pixels_in_mask == np.size(self._array)

    @property
    def shape_slim(self) -> int:
        """
        The 1D shape of the mask, which is equivalent to the total number of unmasked pixels in the mask.
        """
        return self.pixels_in_mask
