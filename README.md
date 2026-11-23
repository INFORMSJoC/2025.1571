[![INFORMS Journal on Computing Logo](https://INFORMSJoC.github.io/logos/INFORMS_Journal_on_Computing_Header.jpg)](https://pubsonline.informs.org/journal/ijoc)

#  Novel exact solution methods for efficient parallel power system restoration

This archive is distributed in association with the [INFORMS Journal on
Computing](https://pubsonline.informs.org/journal/ijoc) under the [BSD 3-Clause License](LICENSE).

The software and data in this repository are a snapshot of the software and data
that were used in the research reported on in the paper 
[Novel exact solution methods for efficient parallel power system restoration](https://doi.org/10.1287/ijoc.2025.1571) by H. Çalık, D. Van Hertem and H. Yaman.
The snapshot is based on the Version 1.0.1 – Zenodo-linked release 
[in this development repository](https://github.com/HaticeCalik/RadiusFormulationsForParallelPowerSystemRestoration). 

In addition to the code implementations, five new PPSR instances are included in the input folders together with the previous benchmark instances from the [literature](https://pubsonline.informs.org/doi/abs/10.1287/ijoc.2022.1258). For details on the mathematical formulations, algorithms, and properties of the new instances, please refer to the associated scientific publication.

## Cite

To cite the contents of this repository, please cite both the paper and this repo, using their respective DOIs

https://doi.org/10.1287/ijoc.2025.1571

https://doi.org/10.1287/ijoc.2025.1571.cd

Below is the BibTex for citing this snapshot of the repository.

```
@misc{Calik2026,
  author =        {H. Çalık},
  publisher =     {INFORMS Journal on Computing},
  title =         {{ Novel exact solution methods for efficient parallel power system restoration}},
  year =          {2026},
  doi =           {10.1287/ijoc.2025.1571.cd},
  url =           {https://github.com/INFORMSJoC/2025.1571},  
  note =          {Available for download at https://github.com/INFORMSJoC/2025.1571},
} 
```

## Usage

### Instance and input file selection:

Multiple problem instances are included in the input folders. In addition to the eight instances available in the literature, this repository provides five new instances.

To select a specific instance, choose the corresponding `nodes` and `lines` files in `parametersAndSets.py`, along with any available lower bound (LB) and upper bound (UB).

For the single-radius PPSR implementations, LB and UB must be identical.

### To solve GSS, three method implementations can be run as main files: 

The radius formulation FGSS: FGSS.py

The binary search algorithm BSA: BSA.py

The binary search algorithm using the partial relaxation of FGSS: BSA_RFGSS_STAR.py

### To solve PPSR, the following method implementations can be run either for a single radius value or multiple radius values in one radius set:

The radius formulation SCF that can solve for multiple radius values: SCF-ALLRADIUS.py

Single-radius formulation SCF with or without network reduction rule: SINGLE-RADIUS-SCF-REDUCTION.py

Single-radius formulation SCF with variable elimination and with or without other reduction rules: SINGLE-RADIUS-SCF-ELIMINATION-DRAWSOLUTION.py, SINGLE-RADIUS-SCF-ELIMINATION-REDUCTION-DRAWSOLUTION.py, SINGLE-RADIUS-SCF-ELIMINATION-BOOKKEEPING-DRAWSOLUTION-.py

Single-radius partition cuts formulation within a Branch-and-Cut implementation:  SINGLERADIUS-PC-STRONG-BC.py

### Output files:

In order to extract log files, solution files or solution figures, use the output directories. The PPSR files provide sample code lines for exporting such files, though these are primarily commented in the initial release. 
