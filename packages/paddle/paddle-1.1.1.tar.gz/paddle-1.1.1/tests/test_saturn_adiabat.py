from importlib import resources
from paddle import (
        setup_profile,
        write_profile,
        find_init_params,
        )
from snapy import (
        MeshBlockOptions,
        MeshBlock,
        )
from kintera import ThermoX

def setup_saturn_profile():
    path = resources.files("paddle") / "data" / "saturn1d.yaml"
    print(f"Reading input file: {path}")

    op_block = MeshBlockOptions.from_yaml(str(path))
    block = MeshBlock(op_block)

    param = {
        "Ts": 600.,
        "Ps": 100.e5,
        "Tmin": 85.,
        "xH2O": 8.91e-3,
        "xNH3": 3.52e-4,
        "xH2S": 8.08e-5,
        "grav": 10.44,
    }

    #method = "pseudo-adiabat"
    #method = "moist-adiabat"
    method = "dry-adiabat"

    param = find_init_params(
            block,
            param,
            target_T=134.,
            target_P=1.e5,
            method=method,
            max_iter=50,
            ftol=1.e-2,
            verbose=True)

    w = setup_profile(block, param, method=method)

    thermo_y = block.module("hydro.eos.thermo")
    thermo_x = ThermoX(thermo_y.options)
    thermo_x.to(dtype=w.dtype, device=w.device)

    write_profile("saturn_profile.txt", w, block)
    return w

if __name__ == "__main__":
    w = setup_saturn_profile()
