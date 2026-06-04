# Data_compression

This repository contains the source code for my seeded LZW compression project.


## Main Files

1. `analyzer.py`: mines frequent Python patterns and creates `seed_dictionary.json`.
2. `encoder.py`: compresses input using a 12-bit seeded LZW dictionary.
3. `decoder.py`: restores the original file from the compressed output.
4. `bit_io.py`: handles 12-bit packing and unpacking.
5. `evaluate.py`: compares byte-only baseline against seeded mode on the full `requests/src/requests` corpus.
6. `tests/test_compression.py`: project-level validation tests for this repository.
7. `generate_plots.py`: generates the figures used in the report.

## Notes For Review

1. The vendored `requests/tests/` directory belongs to the upstream Requests project and is not the test suite for this project.
2. The project-specific tests are in `tests/test_compression.py`.
3. The main comparison requested in the feedback is implemented in `evaluate.py`.
4. The generated figures used in the report are saved in the `figures/` directory.

## Verification Commands

```bash
python -m unittest tests.test_compression
python evaluate.py
python generate_plots.py
python encoder.py
python decoder.py
```