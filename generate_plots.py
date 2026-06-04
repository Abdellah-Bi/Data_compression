import argparse
import json
import os
import tempfile
from contextlib import redirect_stdout
from io import StringIO

import matplotlib.pyplot as plt

from decoder import decompress
from encoder import compress


def gather_python_files(root_directory):
    python_files = []
    for root, _, files in os.walk(root_directory):
        for file_name in files:
            if file_name.endswith(".py"):
                python_files.append(os.path.join(root, file_name))
    return sorted(python_files)


def run_experiment(input_files, seed_patterns):
    total_input_bytes = 0
    total_compressed_bytes = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        seed_file = os.path.join(temp_dir, "seed.json")
        with open(seed_file, "w", encoding="utf-8") as handle:
            json.dump(seed_patterns, handle)

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

    ratio = (total_compressed_bytes / total_input_bytes) if total_input_bytes else 0
    return {
        "files": len(input_files),
        "input_bytes": total_input_bytes,
        "compressed_bytes": total_compressed_bytes,
        "ratio": ratio,
    }


def save_baseline_vs_seeded_plot(output_dir, baseline_result, seeded_result):
    labels = ["Baseline", "Seeded"]
    values = [baseline_result["compressed_bytes"], seeded_result["compressed_bytes"]]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#6c757d", "#1f77b4"])
    plt.title("Compressed Size: Baseline vs Seeded")
    plt.ylabel("Compressed Bytes")

    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 300, f"{value}", ha="center")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "baseline_vs_seeded_bytes.png"), dpi=220)
    plt.close()


def save_ratio_plot(output_dir, baseline_result, seeded_result):
    labels = ["Baseline", "Seeded"]
    values = [baseline_result["ratio"] * 100, seeded_result["ratio"] * 100]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#9aa0a6", "#2a9d8f"])
    plt.title("Compression Ratio Comparison")
    plt.ylabel("Ratio (%)")

    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 0.2, f"{value:.2f}%", ha="center")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "baseline_vs_seeded_ratio.png"), dpi=220)
    plt.close()


def save_seed_ablation_plot(output_dir, input_files, all_patterns):
    seed_sizes = [0, 128, 256, 512, 768]
    compressed_sizes = []

    for size in seed_sizes:
        result = run_experiment(input_files, all_patterns[:size])
        compressed_sizes.append(result["compressed_bytes"])

    plt.figure(figsize=(8, 5))
    plt.plot(seed_sizes, compressed_sizes, marker="o", linewidth=2, color="#e76f51")
    plt.title("Seed Size Ablation")
    plt.xlabel("Number of Prefilled Patterns")
    plt.ylabel("Compressed Bytes")
    plt.grid(alpha=0.3)

    for x_value, y_value in zip(seed_sizes, compressed_sizes):
        plt.text(x_value, y_value + 300, str(y_value), ha="center")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "seed_size_ablation.png"), dpi=220)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate report figures for compression experiments.")
    parser.add_argument(
        "--corpus",
        default="requests/src/requests",
        help="Directory containing Python source files to evaluate.",
    )
    parser.add_argument(
        "--seed-file",
        default="seed_dictionary.json",
        help="JSON file containing mined seed patterns.",
    )
    parser.add_argument(
        "--output-dir",
        default="figures",
        help="Directory where plots will be saved.",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.seed_file, "r", encoding="utf-8") as handle:
        all_patterns = json.load(handle)

    input_files = gather_python_files(args.corpus)
    baseline_result = run_experiment(input_files, [])
    seeded_result = run_experiment(input_files, all_patterns)

    save_baseline_vs_seeded_plot(args.output_dir, baseline_result, seeded_result)
    save_ratio_plot(args.output_dir, baseline_result, seeded_result)
    save_seed_ablation_plot(args.output_dir, input_files, all_patterns)

    print("Saved plots:")
    print(f"- {os.path.join(args.output_dir, 'baseline_vs_seeded_bytes.png')}")
    print(f"- {os.path.join(args.output_dir, 'baseline_vs_seeded_ratio.png')}")
    print(f"- {os.path.join(args.output_dir, 'seed_size_ablation.png')}")


if __name__ == "__main__":
    main()