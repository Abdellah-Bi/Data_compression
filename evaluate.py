import json
import os
import tempfile
from contextlib import redirect_stdout
from io import StringIO

from decoder import decompress
from encoder import compress


def gather_python_files(root_directory):
    python_files = []
    for root, _, files in os.walk(root_directory):
        for file_name in files:
            if file_name.endswith(".py"):
                python_files.append(os.path.join(root, file_name))
    return sorted(python_files)


def run_experiment(input_files, seed_file):
    total_input_bytes = 0
    total_compressed_bytes = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        for input_file in input_files:
            compressed_file = os.path.join(temp_dir, os.path.basename(input_file) + ".lzw")
            restored_file = os.path.join(temp_dir, os.path.basename(input_file) + ".restored")

            with redirect_stdout(StringIO()):
                compress(input_file, compressed_file, seed_file)
                decompress(compressed_file, restored_file, seed_file)

            with open(input_file, "r", encoding="utf-8", errors="ignore") as source_handle:
                original_text = source_handle.read()
            with open(restored_file, "r", encoding="utf-8") as restored_handle:
                restored_text = restored_handle.read()

            if restored_text != original_text:
                raise AssertionError(f"Round-trip mismatch for {input_file}")

            total_input_bytes += os.path.getsize(input_file)
            total_compressed_bytes += os.path.getsize(compressed_file)

    return {
        "file_count": len(input_files),
        "input_bytes": total_input_bytes,
        "compressed_bytes": total_compressed_bytes,
        "ratio": total_compressed_bytes / total_input_bytes if total_input_bytes else 0,
    }


def create_empty_seed_file(temp_dir):
    empty_seed_file = os.path.join(temp_dir, "empty_seed.json")
    with open(empty_seed_file, "w", encoding="utf-8") as handle:
        json.dump([], handle)
    return empty_seed_file


def format_result(label, result):
    ratio_percent = result["ratio"] * 100
    return (
        f"{label}: files={result['file_count']}, input={result['input_bytes']} bytes, "
        f"compressed={result['compressed_bytes']} bytes, ratio={ratio_percent:.2f}%"
    )


def main():
    corpus = gather_python_files("requests/src/requests")

    with tempfile.TemporaryDirectory() as temp_dir:
        empty_seed_file = create_empty_seed_file(temp_dir)
        baseline_result = run_experiment(corpus, empty_seed_file)

    seeded_result = run_experiment(corpus, "seed_dictionary.json")

    print(format_result("Baseline (byte-only start)", baseline_result))
    print(format_result("Seeded dictionary", seeded_result))

    difference = baseline_result["compressed_bytes"] - seeded_result["compressed_bytes"]
    relative_gain = 0.0
    if baseline_result["compressed_bytes"]:
        relative_gain = difference / baseline_result["compressed_bytes"] * 100

    print(
        f"Seeded dictionary saves {difference} bytes versus baseline "
        f"({relative_gain:.2f}% smaller compressed output)."
    )


if __name__ == "__main__":
    main()