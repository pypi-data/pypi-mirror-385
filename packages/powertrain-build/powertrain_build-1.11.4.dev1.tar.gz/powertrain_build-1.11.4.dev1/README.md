# powertrain-build

A Continuous Integration (CI) build system, testing all configurations where a TargetLink model is used.

## General Information about powertrain-build

- powertrain-build is fast.
  - More parallelization of jobs in the CI system makes it faster.
  - Code generation is moved to the developer's PC.
  - Code generation is done once for all projects using pre-processor directives.
  - C code reviews are now possible in Gerrit.
- powertrain-build adds signal consistency checks.
- Unit tests of the build system are introduced.
  - Its quality is assured.
- powertrain-build creates new variable classes with unique code decorations.
  - Post-processing C code is not necessary.
  - ASIL-classed variables get declared at the source.
  - Memory can be optimized at compilation through short addressing different variable classes.
  - The same models can be used in more than two different suppliers, for instance, SPA2's Core System Platform (CSP).
  - powertrain-build fixes incorrect handling of NVM variables.

## Project Structure

- `docs/`: This directory holds all the extra documentation about the project.
- `playbooks/`: Directory where we keep Ansible playbooks that are executed in the jobs we use in this project.
- `powertrain_build/`: Main directory of the project. All the application source code is kept here.
  - `interface/`
  - `lib/`
  - `zone_controller/`
  - `templates/`: Template `.html` files.
  - `matlab_scripts/`: Collection of m-scripts which can be used for generating powertrain-build compatible source code from Simulink models.
- `roles/`: Directory where we keep Ansible roles that are executed in the jobs we use in this project.
- `test_data/`: Directory where we keep test data for the unit tests.
- `tests/`: Directory where we keep the unit tests for our application source code. The tests are structured in a similar way to what we have inside the `powertrain_build/` directory. Tests for the `interface`, `lib`, and `zone_controller` modules are split into `tests/interface/`, `tests/lib/`, and `tests/zone_controller/`, respectively. Other tests are kept inside the `tests/powertrain_build/` directory.
- `zuul.d/`: Directory where we keep our Zuul jobs.

## How to use powertrain-build

See [powertrain-build introduction](./docs/powertrain_build_introduction.md)

## Contributing

We would love to see you contribute to this project. No matter if it is fixing a bug, adding some tests, improving documentation, or implementing new features. See our [contribution guidelines](./CONTRIBUTING.md) so you can have a better understanding of the whole process.

## Code of Conduct

We are trying to create a healthy community that thrives on the desire to improve, learn, and share knowledge. See our [code of conduct guidelines](./CODE_OF_CONDUCT.md) to check our behavioral rules on this project.
