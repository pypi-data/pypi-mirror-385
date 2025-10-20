<div style="text-align: center;">
<pre>
oooooooooo.                                                                                   
`888'   `Y8b                                                                                  
 888      888  .ooooo.  oo.ooooo.  oooo    ooo  .ooooo oo  .ooooo.          oooo d8b  .oooo.o 
 888      888 d88' `88b  888' `88b  `88.  .8'  d88' `888  d88' `88b         `888""8P d88(  "8 
 888      888 888   888  888   888   `88..8'   888   888  888   888 8888888  888     `"Y88b.  
 888     d88' 888   888  888   888    `888'    888   888  888   888          888     o.  )88b 
o888bood8P'   `Y8bod8P'  888bod8P'     .8'     `V8bod888  `Y8bod8P'         d888b    8""888P' 
                         888       .o..P'            888.                                     
                        o888o      `Y8P'             8P'                                      
                                                     "                                        
&nbsp;
                      Many-body matrix elements calculation using Rust
</pre>
</div>

Code for calculating Ewald sums and matrix elements of norm-conserving pseudopotentials in the basis of Kohn-Sham orbitals, expressed in plane-waves.

# Installation as a python package
```bash
pip install dopyqo-rs
```

Make sure to have the following installed, otherwise errors will occur during installation:
- [Rust programming language](https://rustup.rs/)
- [GNU scientific library](https://www.gnu.org/software/gsl/). On a debian (or debian-derived) OS ask your admin to run `sudo apt install libgsl-dev`.



# Development environment instructions
Initilaizing PyO3 project
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install maturin
```

For crate versions see notes in [this section](#rust-crates-version-issues).

Building python package with `maturin develop --release`. This will build the package and install it into the Python virtualenv previously created and activated. The package is then ready to be used from python:
```bash
$ maturin develop --release
# lots of progress output as maturin runs the compilation...
$ python
>>> import dopyqo_rs
```

# Rust crates version issues
!Do not upgarde ndarray, ndarray-linalg, pyo3 and numpy crates!
pyo3 and numpy version 0.23.x depend on ndarray 0.16. ndarray-linalg does not yet support ndarray 0.16. This is also noted in the linalg example of the numpy crate (https://github.com/PyO3/rust-numpy/blob/main/examples/linalg/Cargo.lock).
To make pyo3/numpy 0.23.x work with ndarray-linalg you have to manually tweak the Cargo.lock file as they do in the numpy example for linalg (link above).
The fact that ndarray-linalg does not yet support ndarray 0.16 is discussed in the following issues on the ndarray-linalg github:
- https://github.com/rust-ndarray/ndarray-linalg/issues/387
- https://github.com/rust-ndarray/ndarray-linalg/issues/380
- https://github.com/rust-ndarray/ndarray-linalg/issues/381

Apperantly ndarray-linalg is not actively maintained as of the 20.12.2024.

Maybe switch to [nalgebra](https://github.com/dimforge/nalgebra) which seems to be actively maintained but seems less flexible than ndarray

This all means for now that you should use the following versions:
- pyo3 0.21.0
- numpy 0.21.0
- ndarray 0.15.6
- ndarray-linalg 16.0

Tested with Rust version 1.84.0

# Performance testing
To get in-depth information about all function calls in the rust code and also get a bit more performance add the following to the [Cargo.toml](./Cargo.toml):
```toml
[profile.release]
debug = true       # Debug symbols for our profiler to get in-depth function call information.
```
then install py-spy via pip (`pip install py-spy`) and run the following to generate a flamegraph in profile.svg
```bash
maturin develop --release
py-spy record -i -n -o profile.svg -- python script_using_dopyqo_rs.py 
```

## Authors
- Erik Schultheis

## Contact
Feel free to contact [David Melching](mailto:David.Melching@dlr.de) if you have any questions.

## Citation
If you use portions of this code please cite our [paper](https://arxiv.org/abs/-):
```bibtex
@misc{Schultheis2025ManyBody,
      title={Many-body post-processing of density functional calculations using the variational quantum eigensolver for Bader charge analysis}, 
      author={Erik Schultheis and Alexander Rehn and Gabriel Breuil},
      year={2025},
      eprint={-},
      archivePrefix={arXiv},
      primaryClass={quant-ph},
      url={https://arxiv.org/abs/-}, 
      doi={-}
}
```

## Acknowledgment
This project was made possible by the DLR Quantum Computing Initiative and the Federal Ministry for Economic Affairs and Climate Action; https://qci.dlr.de/quanticom.