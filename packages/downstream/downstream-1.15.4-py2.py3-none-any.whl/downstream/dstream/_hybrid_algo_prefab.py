from . import (
    steady_algo,
    stretched_algo,
    stretchedxtc_algo,
    tilted_algo,
    tiltedxtc_algo,
)
from ._hybrid_algo import hybrid_algo

for algo in (
    hybrid_algo(0, steady_algo, 1, stretched_algo, 2),
    hybrid_algo(0, steady_algo, 1, stretchedxtc_algo, 2),
    hybrid_algo(0, steady_algo, 1, tilted_algo, 2),
    hybrid_algo(0, steady_algo, 1, tiltedxtc_algo, 2),
):
    locals()[algo.__name__] = algo
