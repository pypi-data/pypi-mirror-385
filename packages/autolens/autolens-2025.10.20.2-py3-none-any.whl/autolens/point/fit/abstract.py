from abc import ABC
from functools import partial
from typing import Optional, Tuple

import autoarray as aa
import autogalaxy as ag

from autolens.point.solver import PointSolver
from autolens.lens.tracer import Tracer

from autolens import exc


class AbstractFitPoint(aa.AbstractFit, ABC):
    def __init__(
        self,
        name: str,
        data: aa.Grid2DIrregular,
        noise_map: aa.ArrayIrregular,
        tracer: Tracer,
        solver: PointSolver,
        profile: Optional[ag.ps.Point] = None,
    ):
        """
        Abstract class to fit a point source dataset using a `Tracer` object, including different components
        of the point source data like positions, fluxes and time delays.

        All sub-classes which fit specifc components of the point source data (e.g. positions, fluxes, time delays)
        inherit from this class, to provide them with general point-source functionality used in most
        calculations, for example the deflection angles and magnification of the point source.

        Point source fitting uses name pairing, whereby the `name` of the `Point` object is paired to the name of the
        point source dataset to ensure that point source datasets are fitted to the correct point source.

        This fit object is used in the `FitPointDataset` to perform fitting of a `PointDataset`, which may also fit
        the point dataset poisitions, fluxes and / or time delays.

        When performing a model-fit via an `AnalysisPoint` object the `figure_of_merit` of the child class
        is called and returned in the `log_likelihood_function`.

        Parameters
        ----------
        name
            The name of the point source dataset which is paired to a `Point` profile.
        data
            The positions of the point source in the image-plane which are fitted.
        noise_map
            The noise-map of the positions which are used to compute the log likelihood of the positions.
        tracer
            The tracer of galaxies whose point source profile are used to fit the positions.
        solver
            Solves the lens equation in order to determine the image-plane positions of a point source by ray-tracing
            triangles to and from the source-plane.
        profile
            Manually input the profile of the point source, which is used instead of the one extracted from the
            tracer via name pairing if that profile is not found.
        """

        self.name = name
        self._data = data
        self._noise_map = noise_map
        self.tracer = tracer
        self.solver = solver

        self.profile = profile or tracer.extract_profile(profile_name=name)

        if self.profile is None:
            raise exc.PointExtractionException(
                f"For the point-source named {name} there was no matching point source profile "
                f"in the tracer (make sure your tracer's point source name is the same the dataset name."
            )

    @property
    def data(self):
        return self._data

    @property
    def noise_map(self):
        return self._noise_map

    @property
    def deflections_func(self):
        """
        Returns the deflection angle function, which for example given input image-plane positions computes their
        deflection angles.

        The use of this specific `deflections_func` property is not typical, using the `partial` function to wrap
        a deflections method of the tracer. This is essentially a trick so that, depending on whether multi-plane
        ray-tracing is to be performed, a different deflection function is used. This function is then
        used in `magnifications_at_positions` to compute the magnification of the point source account for
        multi-plane ray-tracing.

        For multi-plane ray-tracing with more than 2 planes, the deflection function determines the index of the
        plane with the last mass profile such that the deflection function does not perform unnecessary computations
        beyond this plane.

        TODO: Simplify this property and calculation of the deflection angles, as this property is confusing.
        TODO: This could be done by allowing for the Hessian to receive planes as input.
        """

        if len(self.tracer.planes) > 2:
            upper_plane_index = self.tracer.extract_plane_index_of_profile(
                profile_name=self.name
            )

            return partial(
                self.tracer.deflections_between_planes_from,
                plane_i=0,
                plane_j=upper_plane_index,
            )

        return self.tracer.deflections_yx_2d_from

    @property
    def magnifications_at_positions(self) -> aa.ArrayIrregular:
        """
        The magnification of every observed position in the image-plane, which is computed from the tracer's deflection
        angle map via the Hessian.

        These magnifications are used for two purposes:

        1) For a source-plane chi-squared calculation, the residuals are multiplied by the magnification to account for
           how the noise in the image-plane positions is magnified to the source-plane, thus defining a
           better chi-squared.

        2) For fitting the fluxes of point sources, the magnification is used to scale the flux of the point source
           in the source-plane to the image-plane, thus computing the model image-plane fluxes.
        """
        return abs(
            self.tracer.magnification_2d_via_hessian_from(
                grid=self.positions, deflections_func=self.deflections_func
            )
        )

    @property
    def source_plane_coordinate(self) -> Tuple[float, float]:
        """
        Returns the centre of the point-source in the source-plane, which is used when computing the model
        image-plane positions from the tracer.

        Returns
        -------
        The (y,x) arc-second coordinates of the point-source in the source-plane.
        """
        return self.profile.centre

    @property
    def plane_index(self) -> int:
        """
        Returns the integer plane index containing the point source galaxy, which is used when computing the deflection
        angles of image-plane positions from the tracer.

        This index is used to ensure that if multi-plane tracing is used when solving the model image-plane positions,
        the correct source-plane is used to compute the model positions whilst accounting for multi-plane lensing.

        Returns
        -------
        The index of the plane containing the point-source galaxy.
        """
        return self.tracer.extract_plane_index_of_profile(profile_name=self.name)

    @property
    def plane_redshift(self) -> float:
        """
        Returns the redshift of the plane containing the point source galaxy, which is used when computing the
        deflection angles of image-plane positions from the tracer.

        This redshift is used to ensure that if multi-plane tracing is used when solving the model image-plane
        positions, the correct source-plane is used to compute the model positions whilst accounting for multi-plane
        lensing.

        Returns
        -------
        The redshift of the plane containing the point-source galaxy.
        """
        return self.tracer.planes[self.plane_index].redshift
