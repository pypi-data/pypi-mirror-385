# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.7.2...v0.8.0) (2025-10-20)


### Features

* Add CLAUDE.md for repository guidance and performance optimization plan ([9638798](https://github.com/mkm29/cve-report-aggregator/commit/9638798874fb34a29dd0ffc7794a1d603ffc5df9))
* **config:** Add support for downloading SBOM reports from remote registry and configure max concurrent workers ([407382a](https://github.com/mkm29/cve-report-aggregator/commit/407382a3654a6ff139e152578773021bb309bcee))
* **downloader:** Implement parallel downloading of SBOM reports with thread safety and error handling ([407382a](https://github.com/mkm29/cve-report-aggregator/commit/407382a3654a6ff139e152578773021bb309bcee))
* enhanced type checking in report.py ([df8ee38](https://github.com/mkm29/cve-report-aggregator/commit/df8ee3882448de3e5164704f05d21db4472bedc6))
* parallel download packages ([400649b](https://github.com/mkm29/cve-report-aggregator/commit/400649b51711c23a47bc6ffea10c742fa1826fbe))
* parallelelize package downloads; improve type checking ([4ed6b90](https://github.com/mkm29/cve-report-aggregator/commit/4ed6b90140cb829fb9c933d30354e2ba62aac033))


### Bug Fixes

* **docker:** Set PYTHON_GIL environment variable to 0 for improved concurrency in Dockerfile ([407382a](https://github.com/mkm29/cve-report-aggregator/commit/407382a3654a6ff139e152578773021bb309bcee))
* increase fail severity to high ([726a5f6](https://github.com/mkm29/cve-report-aggregator/commit/726a5f65ab2991fb9666497bb32eb261df07a34d))


### Documentation

* **changelog:** Update CHANGELOG with new features and improvements related to SBOM downloading and parallel processing ([407382a](https://github.com/mkm29/cve-report-aggregator/commit/407382a3654a6ff139e152578773021bb309bcee))


### Code Refactoring

* enhance Grype scan workflow with improved triggers and deta… ([22b279a](https://github.com/mkm29/cve-report-aggregator/commit/22b279a7f7fbf6d47082dd35d2c1d20353a56ba9))
* enhance Grype scan workflow with improved triggers and detailed logging ([0e92cc9](https://github.com/mkm29/cve-report-aggregator/commit/0e92cc9e4851cf20662677caea2befb5979ca4eb))
* Improve formatting and readability in CLAUDE.md and PERFORMANCE_OPTIMIZATION.md; add Dockerfile for Python 3.14 with Free-Threading ([7cf751b](https://github.com/mkm29/cve-report-aggregator/commit/7cf751bad960eb0dc975c84d70d9b1ebd00580fb))
* improve type casting in image name extraction and update tests for clarity ([799ca94](https://github.com/mkm29/cve-report-aggregator/commit/799ca944d6f3ac49078479aa0c96f8e31318e3f1))
* Remove CLAUDE.md and PERFORMANCE_OPTIMIZATION.md documentation files ([a5070fd](https://github.com/mkm29/cve-report-aggregator/commit/a5070fd62ddbebf06a1a077bd6bc9bbff4a306ff))
* remove emoji from scan summary for clarity ([76fab17](https://github.com/mkm29/cve-report-aggregator/commit/76fab1760e2bed7296e36685306312b662648992))
* update Grype scan workflow to use outputs for image handling and improve summary reporting ([0029221](https://github.com/mkm29/cve-report-aggregator/commit/0029221868e23e8168c27398714b35aa1aab748e))
* update Python version to 3.14.0 and enhance image name extraction logic in reports ([ff9dc31](https://github.com/mkm29/cve-report-aggregator/commit/ff9dc31dfea111989f4e599cffdc96e721c18843))


### Tests

* **downloader:** Add comprehensive tests for parallel downloading functionality, including max workers configuration and error handling ([407382a](https://github.com/mkm29/cve-report-aggregator/commit/407382a3654a6ff139e152578773021bb309bcee))

## [0.7.2](https://github.com/mkm29/cve-report-aggregator/compare/v0.7.1...v0.7.2) (2025-10-20)


### Code Refactoring

* replace Semgrep scan with Grype vulnerability scan in workflow ([c763b51](https://github.com/mkm29/cve-report-aggregator/commit/c763b515a6085a6b458abb483db7b671805f62a7))
* replace Semgrep scan with Grype vulnerability scan in workflow ([70fa600](https://github.com/mkm29/cve-report-aggregator/commit/70fa600e5cabd9ba0f8bca86e50538d507ab4ea1))
* replace semgrep workflow with Grype scan ([8f20a87](https://github.com/mkm29/cve-report-aggregator/commit/8f20a8772eb69578a7066c8089c59c83dfe908af))

## [0.7.1](https://github.com/mkm29/cve-report-aggregator/compare/v0.7.0...v0.7.1) (2025-10-19)

### Bug Fixes

- added conditions to check for valid Docker auth
  ([5193b2b](https://github.com/mkm29/cve-report-aggregator/commit/5193b2b0ad5026e919ed667e4876e0783939fb52))
- improve Docker config validation and clarify authentication requirements in entrypoint script
  ([e7bd2df](https://github.com/mkm29/cve-report-aggregator/commit/e7bd2dfaf45f5d387e1df3b8813de6e08ab9ff20))
- improve Docker config validation and clarify authentication requirements in entrypoint script
  ([537e589](https://github.com/mkm29/cve-report-aggregator/commit/537e5899300ea54f1bd847fa5700a9bc3afaa8f0))

## [0.7.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.6.0...v0.7.0) (2025-10-19)

### Features

- add case-insensitive log level normalization and corresponding tests
  ([89e1f7b](https://github.com/mkm29/cve-report-aggregator/commit/89e1f7b5b7e33aca7d5802e9f689ef0455c0b635))
- enhance CLI logging by displaying configuration settings in DEBUG mode and local variables in CRITICAL mode
  ([9d05f62](https://github.com/mkm29/cve-report-aggregator/commit/9d05f628e8511fc1b601793f6a7504fc7b96dcf7))
- enhance SBOM handling by grouping reports by package and updating output file naming
  ([c69a2fe](https://github.com/mkm29/cve-report-aggregator/commit/c69a2fe37249c35115645871f9aa9b7b9e2fa45d))

### Bug Fixes

- correct severity breakdown count assignment in CLI
  ([7ac67d2](https://github.com/mkm29/cve-report-aggregator/commit/7ac67d2d62fb2bb41349116ac66e799e32c5e286))
- download package names
  ([4c422fe](https://github.com/mkm29/cve-report-aggregator/commit/4c422fefc022414c6789b99febdf8e4b200eb2d3))

### Code Refactoring

- remove unused command execution functions and update tests to use ExecutorManager
  ([3640af0](https://github.com/mkm29/cve-report-aggregator/commit/3640af00e0c46871c944c3de2f665c3a593004e8))

### Tests

- enhance case-insensitive log level tests with temporary input directory setup
  ([82300e6](https://github.com/mkm29/cve-report-aggregator/commit/82300e6087103c8c7bed2e0bd19e0f45cec2c93a))
- enhance output file validation in CLI tests to ensure correct naming patterns and existence
  ([15f5e7e](https://github.com/mkm29/cve-report-aggregator/commit/15f5e7e63015f5d914ae571663e5b19f51fbeca6))

## [0.6.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.5.2...v0.6.0) (2025-10-19)

### Features

- **docs:** enhance README with supply chain security details and image verification instructions
  ([b0bf1cd](https://github.com/mkm29/cve-report-aggregator/commit/b0bf1cdd77f167beee639f50d8f57956cb769d1d))
- enhance command execution safety and add markdown linting functionality
  ([8f4347c](https://github.com/mkm29/cve-report-aggregator/commit/8f4347c16934b185c28396b9e5897ec58f73f880))
- **workflows:** add container image security scan workflow
  ([4240453](https://github.com/mkm29/cve-report-aggregator/commit/4240453af71b4ccb2175f7ec35ad4d6b72fe2587))
- **workflows:** enhance Docker build and scan workflows with version tagging and security scan trigger
  ([591674c](https://github.com/mkm29/cve-report-aggregator/commit/591674cce74238c2bdb69c8be8951945712038f7))
- **workflows:** enhance security scanning workflows and artifact handling
  ([60f5122](https://github.com/mkm29/cve-report-aggregator/commit/60f51228778fa50e45555f66886622f66424db4d))

### Bug Fixes

- add SAST (grype scan) workflow
  ([65b4884](https://github.com/mkm29/cve-report-aggregator/commit/65b4884cc7d1c2606add35927b711ba2ab928c4f))
- implement SLSA level 3 in docker build workflow
  ([ef73efd](https://github.com/mkm29/cve-report-aggregator/commit/ef73efdd81cf260e280fc0b71aa4668feea76ed2))
- increase CI with SAST
  ([0f2ac1a](https://github.com/mkm29/cve-report-aggregator/commit/0f2ac1a0c5e2fe556ae701b219e1f665b9c791c9))
- remove \*.sarif from .gitignore
  ([13d96be](https://github.com/mkm29/cve-report-aggregator/commit/13d96be1d8e613a14a5ec42359f4cd8db4a6acce))
- update .gitignore to exclude SARIF files and remove semgrep.sarif
  ([6cad191](https://github.com/mkm29/cve-report-aggregator/commit/6cad19162c918de32d27bc5d1a38057edd5155e8))
- **workflows:** clean up branch triggers and add permissions for test jobs
  ([bb036ac](https://github.com/mkm29/cve-report-aggregator/commit/bb036acf5188cf519240c267d59501c2347579f0))
- **workflows:** comment out push tags configuration in Docker build workflow
  ([bd93541](https://github.com/mkm29/cve-report-aggregator/commit/bd93541caedd18ad924f94d76ccee17a1c6b2a81))
- **workflows:** enhance Docker build and release workflows with improved error handling and summary generation
  ([224d848](https://github.com/mkm29/cve-report-aggregator/commit/224d848a2c53db74af700cf0452dbac385b655f0))
- **workflows:** enhance image tag determination logic for scans triggered by Docker build workflow
  ([ce3248a](https://github.com/mkm29/cve-report-aggregator/commit/ce3248ae05cc7b571bd4966de8b9b2296ebd4885))
- **workflows:** remove pull_request trigger from Semgrep security scan workflow
  ([e095612](https://github.com/mkm29/cve-report-aggregator/commit/e095612b7e3f6457da924f97afd2010fecd4a3f5))
- **workflows:** update push event handling for feature branch and improve image tag determination
  ([b69bd84](https://github.com/mkm29/cve-report-aggregator/commit/b69bd844951b8d41b0941738d608900528a3ee03))
- **workflows:** update Semgrep security scan workflow and remove container image scanning
  ([08869d0](https://github.com/mkm29/cve-report-aggregator/commit/08869d08530510421c4b58b2e57e1cd78aaceb33))

## [0.5.2](https://github.com/mkm29/cve-report-aggregator/compare/v0.5.1...v0.5.2) (2025-10-19)

### Bug Fixes

- add missing permission docker build flow
  ([5d1e0fa](https://github.com/mkm29/cve-report-aggregator/commit/5d1e0fa877eec0592380b6555d118af7bd4a6c49))
- add missing permissions to docker build workflow
  ([82efe9d](https://github.com/mkm29/cve-report-aggregator/commit/82efe9dba7fc8103b79d1122a62723147ef03668))
- **release:** update permissions for trigger-docker-build job
  ([4c39f21](https://github.com/mkm29/cve-report-aggregator/commit/4c39f211f393f866cb35631c34902255b9e50f6a))

## [0.5.1](https://github.com/mkm29/cve-report-aggregator/compare/v0.5.0...v0.5.1) (2025-10-19)

### Bug Fixes

- moved pypi publish job to trigger
  ([9794a32](https://github.com/mkm29/cve-report-aggregator/commit/9794a32a11afcd773ee8a8c8dbc0221df4236175))

### Code Refactoring

- Simplify PyPI publication steps and adjust permissions in release workflow
  ([f0dad86](https://github.com/mkm29/cve-report-aggregator/commit/f0dad86edc17f571e3204ca276db6eab223c2bb1))
- Simplify PyPI publication steps and adjust permissions in release workflow
  ([459b40a](https://github.com/mkm29/cve-report-aggregator/commit/459b40a4d331a0643690acda2e32b66b53463ce7))

## [0.5.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.4.1...v0.5.0) (2025-10-19)

### Features

- centralized log manager with structlog
  ([3a27b4c](https://github.com/mkm29/cve-report-aggregator/commit/3a27b4cfe1accf9a8b17e594b51eb3d3a591e65e))
- **downloader:** Implement remote package downloading for SBOM reports
  ([9ab4bcb](https://github.com/mkm29/cve-report-aggregator/commit/9ab4bcb070727be18fe7e08d114cda0b9985c7d7))
- Enhance global configuration management and add usage examples
  ([c46d45b](https://github.com/mkm29/cve-report-aggregator/commit/c46d45bba7477c516e2fc391cb04f3513c35804b))
- implement command executor manager
  ([1682e1a](https://github.com/mkm29/cve-report-aggregator/commit/1682e1a237c19751a72dfbb4757aaf15fd59fb97))
- Implement CVE Report Aggregator processing modules
  ([6bd8081](https://github.com/mkm29/cve-report-aggregator/commit/6bd8081c3292ae2755baa450ebddcddfbdcfaf1a))
- **logging:** Implement centralized logging system using structlog
  ([24b1a4d](https://github.com/mkm29/cve-report-aggregator/commit/24b1a4d9c3e3408d72e161f3f0bd9699212869ba))
- Reorganize modules, add command executor module
  ([fca9045](https://github.com/mkm29/cve-report-aggregator/commit/fca90459734551b61255c0bfe5261ebf4cdaf01d))

### Bug Fixes

- Remove redundant import of Generator from typing
  ([bcf4aad](https://github.com/mkm29/cve-report-aggregator/commit/bcf4aad4fd927b30d38e8876fb7f15c5d39c393b))
- **tests:** Refactor sample and quiet configuration fixtures for improved path handling
  ([6902f2f](https://github.com/mkm29/cve-report-aggregator/commit/6902f2f7710086ee96a97a05a82b69f523f0e07e))

## [0.4.1](https://github.com/mkm29/cve-report-aggregator/compare/v0.4.0...v0.4.1) (2025-10-18)

### Code Refactoring

- Simplify Dockerfile by removing python-builder stage and optimizing package installation
  ([530aa73](https://github.com/mkm29/cve-report-aggregator/commit/530aa73e2d24f3936591813f94b6ad5ff8dd465e))
- Simplify Dockerfile by removing python-builder stage and optimizing package installation
  ([1f8f0d6](https://github.com/mkm29/cve-report-aggregator/commit/1f8f0d6cafc94427a4fd9082fecc1ba8c5df563a))

## [0.4.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.3.0...v0.4.0) (2025-10-18)

### Features

- Add Docker build trigger after successful release
  ([dfcf8f2](https://github.com/mkm29/cve-report-aggregator/commit/dfcf8f21b801bc3d6d51b713acdd612adbb7a576))
- Add Docker build trigger after successful release
  ([c8bc662](https://github.com/mkm29/cve-report-aggregator/commit/c8bc66269dd7ae870633c212685bc1d05872dc6d))

## [0.3.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.2.0...v0.3.0) (2025-10-18)

### Features

- Implement comprehensive configuration management using Pydantic Settings with YAML support
  ([4d62a3f](https://github.com/mkm29/cve-report-aggregator/commit/4d62a3fa19cb8713e17ddf37c6b8c0a59fcb50f7))
- implement pydantic app config and mkdocs site
  ([f699282](https://github.com/mkm29/cve-report-aggregator/commit/f6992826f79c91c5c424d1b8cef57cfb7ca65408))
- pydantic config and mkdocs site
  ([ff707ed](https://github.com/mkm29/cve-report-aggregator/commit/ff707eddf87de2612163dcc053e5a424f7af4974))

### Bug Fixes

- Update documentation links and improve .gitignore configuration
  ([ab0324e](https://github.com/mkm29/cve-report-aggregator/commit/ab0324e285d057376eeab69f2886dfc61934dc24))
- Update documentation links and improve .gitignore configuration
  ([a4c24a4](https://github.com/mkm29/cve-report-aggregator/commit/a4c24a4c698d623d8935a6b86680d98d86c1daf0))

### Code Refactoring

- Simplify Docker build workflow by removing unnecessary conditions and improving version handling
  ([6e8dc4f](https://github.com/mkm29/cve-report-aggregator/commit/6e8dc4f4785e6350529b379c1462736633a09efa))
- Simplify Docker build workflow by removing unnecessary conditions and improving version handling
  ([be41e7e](https://github.com/mkm29/cve-report-aggregator/commit/be41e7efb8b56cf563db262182440e8b3ec56af1))

## [0.2.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.1.0...v0.2.0) (2025-10-18)

### Features

- Add branch protection and CI workflows for Git Flow
  ([5db7c5d](https://github.com/mkm29/cve-report-aggregator/commit/5db7c5d00712764959632d9105aaecc747977351))
- Add branch protection and CI workflows for Git Flow
  ([bc7ac6a](https://github.com/mkm29/cve-report-aggregator/commit/bc7ac6a67c81fcab33b7d1523d7578df33cb9583))
- Add Codecov token and slug for unit test coverage uploads
  ([8ed43cc](https://github.com/mkm29/cve-report-aggregator/commit/8ed43cc52a35f4c7ce987a00751ed4d1f2ec78b6))
- Add comprehensive unit tests
  ([29e44da](https://github.com/mkm29/cve-report-aggregator/commit/29e44dab24b1748166b14ba12836f1f4c534702b))
- add Dockerfile and update README with Docker usage instructions
  ([9b5208a](https://github.com/mkm29/cve-report-aggregator/commit/9b5208a54658f649f23d90bb9e0e888968be237b))
- add Dockerfile and update README with Docker usage instructions
  ([63a18f2](https://github.com/mkm29/cve-report-aggregator/commit/63a18f282333153a39d0528d4c16eb6d71b71ad4))
- add highest severity selection for vulnerability deduplication
  ([745c231](https://github.com/mkm29/cve-report-aggregator/commit/745c2313e26f18b30652095feb5cfeff29b27035))
- add highest severity selection for vulnerability deduplication
  ([896053c](https://github.com/mkm29/cve-report-aggregator/commit/896053ca88df1626108862a8012b438a84bb869f))
- add scanner source tracking and update CLI options for highest score selection
  ([276f96e](https://github.com/mkm29/cve-report-aggregator/commit/276f96eb45d2abbcd652b2ee9203aa3b29e8d4b8))
- add scanner source tracking and update CLI options for highest score selection
  ([8620258](https://github.com/mkm29/cve-report-aggregator/commit/862025857fd7a1601d09ff8ba6db0d0a5dc8836f))
- Add unit and integration tests for vulnerability deduplication and severity scoring
  ([7e2b3dc](https://github.com/mkm29/cve-report-aggregator/commit/7e2b3dcfdbdb569f9bf2088077f12c41dacf4de6))
- configured pyproject.toml to use utils module
  ([18ed577](https://github.com/mkm29/cve-report-aggregator/commit/18ed577617a5cb193b240ee2314ccfc2eeb4bd01))
- configured pyproject.toml to use utils module
  ([8041b2f](https://github.com/mkm29/cve-report-aggregator/commit/8041b2fb5604a3bbb7ec4ad5ad2deeadad2be4f9))
- implement Docker credentials management and SOPS encryption support
  ([93fb183](https://github.com/mkm29/cve-report-aggregator/commit/93fb1837526bb9637a70ad58843e65dad6a993e8))
- implement Docker credentials management and SOPS encryption support
  ([6c20a1c](https://github.com/mkm29/cve-report-aggregator/commit/6c20a1c6a5a6750bb19394af10479db83e87a4be))

### Bug Fixes

- add contributing doc
  ([ca44c02](https://github.com/mkm29/cve-report-aggregator/commit/ca44c026a818d610c78ba9fe36acc1c68264fa7f))
- Enhance Dockerfile credential handling with fallback for missing secrets
  ([e2b0858](https://github.com/mkm29/cve-report-aggregator/commit/e2b0858a9bf0323cc0d6f51ee9af57039ce48b33))
- Enhance Dockerfile credential handling with fallback for missing secrets
  ([4dfcc58](https://github.com/mkm29/cve-report-aggregator/commit/4dfcc588f376a76fb2d1a713d3577972829e8bbd))
- Remove commented environment section from release workflow
  ([3bdbef1](https://github.com/mkm29/cve-report-aggregator/commit/3bdbef14a28508129ec48ed27311bf4583dd404d))
- Remove push trigger from Docker build workflow and refine versio…
  ([d948616](https://github.com/mkm29/cve-report-aggregator/commit/d94861645929706f78b1fc3ac049ebfb3265be8c))
- Remove push trigger from Docker build workflow and refine versioning logic for merged PRs
  ([bbbd140](https://github.com/mkm29/cve-report-aggregator/commit/bbbd140f12312b1fbed1bf8877c0162cb9bc5d84))
- tighten docker build workflow
  ([08b2540](https://github.com/mkm29/cve-report-aggregator/commit/08b25403c77b059f833e8e6a7b146bcbcd1316bb))
- Update conditions for Docker build job execution
  ([e049adf](https://github.com/mkm29/cve-report-aggregator/commit/e049adf0879b44279d205229e199877e215d7bd2))
- Update Docker build context and file path for image build
  ([a5a9049](https://github.com/mkm29/cve-report-aggregator/commit/a5a9049ededff89b62a345fcebc03cf03ca600ce))
- Update Docker build context and file path for image build
  ([056c010](https://github.com/mkm29/cve-report-aggregator/commit/056c0108046b533b36ab3b26ba6df9b19e7e2c3f))
- update logo image in README and add new logo file
  ([1a42b79](https://github.com/mkm29/cve-report-aggregator/commit/1a42b796e5e988079340541cc58f7ace284b0c4b))
- update logo image in README and replace old logo file
  ([fc3f532](https://github.com/mkm29/cve-report-aggregator/commit/fc3f53266fa329d23c301bf1c250742161f3e598))

### Documentation

- Update README to include additional badges for Python version, PyPI, CI, and Docker
  ([8f414a6](https://github.com/mkm29/cve-report-aggregator/commit/8f414a623dbdcf36d655b0a83c2b100c7e93cb94))
- Update README to include badges
  ([6872952](https://github.com/mkm29/cve-report-aggregator/commit/6872952b98c0ea653ed7ac29c86e3c7023d7f9b6))

### Code Refactoring

- add type annotations for improved type safety and clarity
  ([8d95f87](https://github.com/mkm29/cve-report-aggregator/commit/8d95f8765a0dbdd556c9ce314363e148e92a4bec))
- add type annotations for improved type safety and clarity
  ([3fb6bf1](https://github.com/mkm29/cve-report-aggregator/commit/3fb6bf1ea0810fa70adc38d9058bcef73aea1953))
- Clean up test files by removing unused imports and improving docstrings
  ([de32773](https://github.com/mkm29/cve-report-aggregator/commit/de32773f41b8cebfc7f9ca0ab54e5dd379273506))
- modify code structure for improved readability and maintainability
  ([bd0a813](https://github.com/mkm29/cve-report-aggregator/commit/bd0a813e84d64e1303a2359a31e7d03f2f036607))
- Remove disk space checks and cleanup steps from Docker build workflow
  ([bf4aa6f](https://github.com/mkm29/cve-report-aggregator/commit/bf4aa6f3a707fb44e395b84d95102ad1ef60607e))
- Remove disk space checks and cleanup steps from Docker build workflow
  ([8eb4d3b](https://github.com/mkm29/cve-report-aggregator/commit/8eb4d3b422d998a9dd904b6001da9db77caedbaa))
- update CLI entry point to conditionally display logo based on version flag
  ([c99ad17](https://github.com/mkm29/cve-report-aggregator/commit/c99ad17bb838d95b7112f67b6bf295a8199f296c))

### Miscellaneous Chores

- merge develop branch into main
  ([2316963](https://github.com/mkm29/cve-report-aggregator/commit/2316963e204977416f33b0a367c336e7142aba1b))
- removed background from logo and filled in Doug
  ([781f3af](https://github.com/mkm29/cve-report-aggregator/commit/781f3afb889600602ab0f978a8a1544ee5b39e9f))

## [Unreleased]

### Added

- Docker credentials management with two methods: build-time secrets and environment variables
- SOPS encryption support for credentials file (`docker/config.json`)
- Docker BuildKit secret mount for secure credential injection during build
- Entrypoint script with dual authentication support (config.json or env vars)
- Security best practices documentation for credential management
- `.sops.yaml` configuration for encrypting credentials with age key
- Multi-stage Docker build with Alpine Linux base
- Non-root user (cve-aggregator, UID 1001) for container security
- Pre-installed scanning tools in Docker image: Grype, Syft, Trivy, UDS CLI
- Rich terminal output with color-coded tables and progress indicators
- Multi-scanner support (Grype and Trivy)
- SBOM auto-detection and scanning with Grype
- Automatic conversion of Grype reports to CycloneDX format for Trivy
- CVE deduplication across multiple scan reports
- Automatic null CVSS filtering (removes invalid scores)
- CVSS 3.x-based severity selection with `--mode highest-score`
- Scanner source tracking to identify which scanner provided vulnerability data
- Occurrence tracking to count CVE appearances across images
- Click-based CLI with rich-click styling
- Comprehensive test suite with pytest
- Type annotations throughout codebase
- Package installation via pip/pipx
- Docker Compose support

### Changed

- Consolidated Docker credentials documentation into main README.md
- Updated credentials file format to JSON with `username`, `password`, and `registry` fields
- Removed volume mount references from documentation (focus on credential management)
- Simplified credential methods from 4 to 2 (build-time secrets and environment variables)
- Registry is now configurable via credentials file instead of hardcoded

### Removed

- Separate `docker/README.md` file (merged into main README)
- Docker Secrets method (Docker Swarm/Compose secrets)
- Volume-mounted credentials file method
- Support for multiple credential file locations

### Security

- Credentials must be encrypted with SOPS before committing to version control
- Decrypted credential files (\*.dec) are automatically cleaned up after build
- Build-time secrets never appear in Docker image layers
- Container runs as non-root user (UID 1001)
- System pip removed from final image to reduce attack surface
- All dependencies pinned to specific versions in Dockerfile

## [0.1.0] - 2025-01-17

### Added

- Initial release of CVE Report Aggregator
- Basic Grype report aggregation and deduplication
- Command-line interface with Click
- JSON output format with metadata, summary, and vulnerabilities
- Docker support with Dockerfile and docker-compose.yml
- MIT License
- README with usage examples and installation instructions

[0.1.0]: https://github.com/mkm29/cve-report-aggregator/releases/tag/v0.1.0
[unreleased]: https://github.com/mkm29/cve-report-aggregator/compare/v0.1.0...HEAD
