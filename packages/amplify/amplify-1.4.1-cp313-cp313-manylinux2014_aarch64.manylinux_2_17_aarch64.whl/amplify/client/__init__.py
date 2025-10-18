from __future__ import annotations

import warnings
from typing import NoReturn

from typing_extensions import deprecated

from .. import DWaveSamplerClient as _DWaveSamplerClient
from .. import FixstarsClient as _FixstarsClient
from .. import FujitsuDA4Client, NECVA2Client
from .. import GurobiClient as _GurobiClient
from .. import HitachiClient as _HitachiClient
from .. import LeapHybridSamplerClient as _LeapHybridSamplerClient
from .. import ToshibaSQBM2Client as _ToshibaSQBM2Client
from .._backward import _deprecation_warnings_msg, _NotImplemented, _obsolete_warnings_msg

warnings.warn(_deprecation_warnings_msg(f"{__name__} module"), DeprecationWarning, stacklevel=2)

__all__ = [
    "ABSClient",
    "DWaveSamplerClient",
    "FixstarsClient",
    "FujitsuDA2MixedModeSolverClient",
    "FujitsuDA2PTSolverClient",
    "FujitsuDA2SolverClient",
    "FujitsuDA2SolverExpertClient",
    "FujitsuDA3SolverClient",
    "FujitsuDA4SolverClient",
    "FujitsuDAMixedModeSolverClient",
    "FujitsuDAPTSolverClient",
    "FujitsuDASolverClient",
    "FujitsuDASolverExpertClient",
    "GurobiClient",
    "HitachiClient",
    "LeapHybridSamplerClient",
    "NECClient",
    "QiskitClient",
    "QulacsClient",
    "ToshibaClient",
    "ToshibaSQBM2Client",
]


class _FutureRelease:
    def __init__(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            f"{type(self).__name__} (or its alternative) will be implemented in the future release."
        )


@deprecated(_deprecation_warnings_msg("amplify.client.FixstarsClient", "amplify.FixstarsClient"))  # type: ignore
class FixstarsClient(_FixstarsClient):
    pass


@deprecated(_deprecation_warnings_msg("amplify.client.DWaveSamplerClient", "amplify.DWaveSamplerClient"))  # type: ignore
class DWaveSamplerClient(_DWaveSamplerClient):
    pass


@deprecated(_deprecation_warnings_msg("amplify.client.LeapHybridSamplerClient", "amplify.LeapHybridSamplerClient"))  # type: ignore
class LeapHybridSamplerClient(_LeapHybridSamplerClient):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDASolverClient"))  # type: ignore
class FujitsuDASolverClient(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDASolverExpertClient"))  # type: ignore
class FujitsuDASolverExpertClient(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDAPTSolverClient"))  # type: ignore
class FujitsuDAPTSolverClient(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDAMixedModeSolverClient"))  # type: ignore
class FujitsuDAMixedModeSolverClient(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDA2SolverClient"))  # type: ignore
class FujitsuDA2SolverClient(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDA2SolverExpertClient"))  # type: ignore
class FujitsuDA2SolverExpertClient(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDA2PTSolverClient"))  # type: ignore
class FujitsuDA2PTSolverClient(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDA2MixedModeSolverClient"))  # type: ignore
class FujitsuDA2MixedModeSolverClient(_NotImplemented):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.FujitsuDA3SolverClient"))  # type: ignore
class FujitsuDA3SolverClient(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("amplify.client.FujitsuDA4SolverClient", "amplify.FujitsuDA4Client"))  # type: ignore
class FujitsuDA4SolverClient(FujitsuDA4Client):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.ToshibaClient"))  # type: ignore
class ToshibaClient(_NotImplemented):
    pass


@deprecated(_deprecation_warnings_msg("amplify.client.ToshibaSQBM2Client", "amplify.ToshibaSQBM2Client"))  # type: ignore
class ToshibaSQBM2Client(_ToshibaSQBM2Client):
    pass


@deprecated(_deprecation_warnings_msg("amplify.client.HitachiClient", "amplify.HitachiClient"))  # type: ignore
class HitachiClient(_HitachiClient):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.ABSClient"))  # type: ignore
class ABSClient(_FutureRelease):
    pass


@deprecated(_deprecation_warnings_msg("amplify.client.GurobiClient", "amplify.GurobiClient"))  # type: ignore
class GurobiClient(_GurobiClient):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.QiskitClient"))  # type: ignore
class QiskitClient(_FutureRelease):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.QulacsClient"))  # type: ignore
class QulacsClient(_FutureRelease):
    pass


@deprecated(_obsolete_warnings_msg("amplify.client.NECClient", "amplify.NECVA2Client"))  # type: ignore
class NECClient(NECVA2Client):
    pass
