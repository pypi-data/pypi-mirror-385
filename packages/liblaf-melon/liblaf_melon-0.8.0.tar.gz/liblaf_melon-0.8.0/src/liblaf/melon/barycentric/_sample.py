import numpy as np
from jaxtyping import Float


def sample_barycentric_coords(
    shape: tuple[int, int], generator: np.random.Generator | None = None
) -> Float[np.ndarray, "N D"]:
    if generator is None:
        generator = np.random.default_rng()
    n_samples: int = shape[0]
    dim: int = shape[1]
    coords: Float[np.ndarray, "N D-1"] = generator.uniform(0, 1, (n_samples, dim - 1))
    coords: Float[np.ndarray, "N D-1"] = np.sort(coords, axis=1)
    coords: Float[np.ndarray, "N D"] = np.diff(coords, axis=1, prepend=0, append=1)
    return coords
