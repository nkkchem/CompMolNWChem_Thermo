# CompMolNWChem_Thermo

We developed the first nonempirical high-throughput computational method, CompMolNWChem_Thermo, for estimating reaction and metabolite standard Gibbs energies using NWChem(1) Computational Chemistry Calculations.  We integrated our automated computational pipeline to calculate metabolic reaction free energy with the DOE Systems Biology Knowledgebase (KBase) module (2) to develop a QC based web accessible application (App). Our app integrates set of modules, each of which are selfcontained and independently validated. It uses benchmarked QC method and provide open source access as a ThermoCalculator to calculate reaction free energy (3). For this, we have used snakemake48 as an underlying package for workflow management to bind together different Python-based components ensuring scalability, portability, and fault tolerance. Within the app, ModelSEED database is used for describing the biochemical reactions that are used to construct a new genome scale model for a given organism. Our app takes ModelSEED reaction ID or reaction as an input and generates a metabolite list of ModelSEED compounds and returns QC predicted reaction free energy as well as Gibbs free energy of metabolites as an output. We have been still developing to calculate Underlying QC calculations are performed using integrated high-performance computing resources at PNNL outside the KBase app.

This is a [KBase](https://kbase.us) module generated by the [KBase Software Development Kit (SDK)](https://github.com/kbase/kb_sdk).

You will need to have the SDK installed to use this module. [Learn more about the SDK and how to use it](https://kbase.github.io/kb_sdk_docs/).

You can also learn more about the apps implemented in this module from its [catalog page](https://narrative.kbase.us/#catalog/modules/CompMolNWChem_Thermo) or its [spec file]($module_name.spec).

# Setup and test

Add your KBase developer token to `test_local/test.cfg` and run the following:

```bash
$ make
$ kb-sdk test
```

After making any additional changes to this repo, run `kb-sdk test` again to verify that everything still works.

# Installation from another module

To use this code in another SDK module, call `kb-sdk install CompMolNWChem_Thermo` in the other module's root directory.

# Reference

(1) Apr`a, E. et al. NWChem: Past, present, and future. The Journal of Chemical Physics
2020, 152, 184102.
(2)	Arkin, A. P. et al. The DOE Systems Biology Knowledgebase (KBase). bioRxiv 2016. 
(3) Joshi, R., McNaughton, A.D., Thomas, D.G., Henry, C., Canon, S., McCue, L., and Kumar, N. "Quantum Mechanical Methods Predict Accurate Thermodynamics of Biochemical Reactions" ACS Omega Omega. 2021 Apr 13; 6(14): 9948–9959. https://doi.org/10.1021/acsomega.1c00997 ![Uploading image.png…]()


# Help

You may find the answers to your questions in our [FAQ](https://kbase.github.io/kb_sdk_docs/references/questions_and_answers.html) or [Troubleshooting Guide](https://kbase.github.io/kb_sdk_docs/references/troubleshooting.html).

# Disclaimer

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the United States Government nor the United States Department of Energy, nor Battelle, nor any of their employees, nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe privately owned rights.
Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United States Government or any agency thereof, or Battelle Memorial Institute. The views and opinions of authors expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.
PACIFIC NORTHWEST NATIONAL LABORATORY operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY under Contract DE-AC05-76RL01830

