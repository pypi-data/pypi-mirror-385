import numpy as np
from dataclasses import dataclass
from typing import Optional

# Security level constants
MIN = 128
BAL = 192
MAX = 256

@dataclass
class CLWEParameters:
    security_level: int
    lattice_dimension: int
    modulus: int
    error_bound: int
    color_transform_entropy: float
    optimized: bool = False

def get_params(security_level, optimized: bool = False) -> CLWEParameters:
    # Handle string security levels
    if isinstance(security_level, str):
        if security_level == "MIN":
            if optimized:
                return CLWEParameters(
                    security_level=MIN,
                    lattice_dimension=256,
                    modulus=3329,
                    error_bound=6,
                    color_transform_entropy=4096.0,
                    optimized=True
                )
            else:
                return CLWEParameters(
                    security_level=MIN,
                    lattice_dimension=256,
                    modulus=3329,
                    error_bound=8,
                    color_transform_entropy=2048.0,
                    optimized=False
                )
        elif security_level == "BAL":
            if optimized:
                return CLWEParameters(
                    security_level=BAL,
                    lattice_dimension=384,
                    modulus=7681,
                    error_bound=8,
                    color_transform_entropy=8192.0,
                    optimized=True
                )
            else:
                return CLWEParameters(
                    security_level=BAL,
                    lattice_dimension=384,
                    modulus=7681,
                    error_bound=12,
                    color_transform_entropy=4096.0,
                    optimized=False
                )
        elif security_level == "MAX":
            if optimized:
                return CLWEParameters(
                    security_level=MAX,
                    lattice_dimension=512,
                    modulus=12289,
                    error_bound=10,
                    color_transform_entropy=16384.0,
                    optimized=True
                )
            else:
                return CLWEParameters(
                    security_level=MAX,
                    lattice_dimension=512,
                    modulus=12289,
                    error_bound=16,
                    color_transform_entropy=8192.0,
                    optimized=False
                )
        else:
            raise ValueError(f"Unsupported security level: {security_level}")

    # Handle numeric security levels (backward compatibility)
    if security_level == MIN:
        if optimized:
            return CLWEParameters(
                security_level=MIN,
                lattice_dimension=256,
                modulus=3329,
                error_bound=6,
                color_transform_entropy=4096.0,
                optimized=True
            )
        else:
            return CLWEParameters(
                security_level=MIN,
                lattice_dimension=256,
                modulus=3329,
                error_bound=8,
                color_transform_entropy=2048.0,
                optimized=False
            )
    elif security_level == BAL:
        if optimized:
            return CLWEParameters(
                security_level=BAL,
                lattice_dimension=384,
                modulus=7681,
                error_bound=8,
                color_transform_entropy=8192.0,
                optimized=True
            )
        else:
            return CLWEParameters(
                security_level=BAL,
                lattice_dimension=384,
                modulus=7681,
                error_bound=12,
                color_transform_entropy=4096.0,
                optimized=False
            )
    elif security_level == MAX:
        if optimized:
            return CLWEParameters(
                security_level=MAX,
                lattice_dimension=512,
                modulus=12289,
                error_bound=10,
                color_transform_entropy=16384.0,
                optimized=True
            )
        else:
            return CLWEParameters(
                security_level=MAX,
                lattice_dimension=512,
                modulus=12289,
                error_bound=16,
                color_transform_entropy=8192.0,
                optimized=False
            )
    else:
        raise ValueError(f"Unsupported security level: {security_level}")

def validate_parameters(params: CLWEParameters) -> bool:
    if params.lattice_dimension <= 0:
        return False
    if params.modulus <= 0:
        return False
    if params.error_bound <= 0:
        return False
    if params.color_transform_entropy <= 0:
        return False
    return True