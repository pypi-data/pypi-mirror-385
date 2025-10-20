import dataclasses
import os

import numpy as np

from ._cosmology import ClassCosmology, SimpleCosmology
from ._parfile import read_par


@dataclasses.dataclass
class Simulation:
    path: str | os.PathLike[str]
    dir: str | os.PathLike[str] | None = None

    parameters: dict[str, object] = dataclasses.field(init=False, repr=False)
    cosmology: dict[str, object] = dataclasses.field(init=False, repr=False)

    outname: str | None = dataclasses.field(init=False, repr=False)
    nside: int | None = dataclasses.field(init=False, repr=False)

    redshifts: np.ndarray = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.path = os.path.realpath(os.path.expanduser(self.path))

        if self.dir is None:
            self.dir = os.path.dirname(self.path)

        self.parameters = read_par(self.path)

        if self.parameters.get("bClass", False):
            class_path = self.parameters["achClassFilename"]
            if not os.path.isabs(class_path):
                class_path = os.path.join(self.dir, class_path)
            self.cosmology = ClassCosmology(class_path)
        else:
            self.cosmology = SimpleCosmology(self.parameters)

        self.outname = self.parameters.get("achOutName")
        self.nside = self.parameters.get("nSideHealpix")

        # load redshifts from logfile
        z = np.loadtxt(os.path.join(self.dir, f"{self.outname}.log"), usecols=1)
        if z.shape != (self.parameters["nSteps"] + 1,):
            raise ValueError("inconsistent steps in .par and .log file")

        # replace nearly-zero final redshift by zero
        if np.fabs(z[-1]) < 1e-14:
            z[-1] = 0.0

        # reorder redshifts from latest to earliest
        self.redshifts = z[::-1]


def load(path: str | os.PathLike[str]) -> Simulation:
    return Simulation(path)
