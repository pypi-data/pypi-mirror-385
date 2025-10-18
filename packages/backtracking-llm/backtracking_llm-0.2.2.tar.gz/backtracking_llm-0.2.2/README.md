# Backtracking LLM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/backtracking-llm.svg)](https://badge.fury.io/py/backtracking-llm)
[![Build Status](https://github.com/matee8/backtracking_llm/actions/workflows/python.yml/badge.svg)](https://github.com/matee8/backtracking_llm/actions/workflows/python.yml)

A Python library for running large language models with a backtracking
mechanism, allowing the model to dynamically revise and "undo" its own generated
tokens to improve output quality.

This project is the official implementation accompanying the research presented
at AI conferences.

## Core Concepts

Standard autoregressive language models generate text one token at a time, and
each token is chosen irreversibly. This can lead to compounding errors, where a
single poor token choice results in a low-quality or nonsensical completion.

**Backtracking LLM** introduces a "self-correction" step into the generation
loop. After a token is sampled, a decision function (an `Operator`) evaluates
the choice. If the choice is deemed low-quality (e.g., it's a repetitive token
or the model's confidence was too low), the generator can "backtrack,"
effectively erasing the last N tokens and attempting a different generation
path.

This is managed by two primary components:

-   `Generator`: The core engine that wraps a `transformers` model and
    tokenizer. It manages the token-by-token generation loop, including the
    stateful KV cache, and executes the backtracking logic when instructed.
-   `Operator`: A pluggable rule that decides when to backtrack. The library
    provides a suite of operators based on different heuristics, such as token
    probability, distribution entropy, and repetition.

## Features

-   Backtracking Mechanism: A simple yet powerful way to add a self-correction
    loop to standard LLM inference.
-   Pluggable Decision Operators: A collection of built-in rules for controlling
    backtracking, from simple probability thresholds to n-gram overlap detection.
-   High-Level Chat Pipeline: A stateless `ChatPipeline` that correctly handles
    multi-turn conversations using model-specific chat templates.
-   Robust Benchmarking Suite: A complete, configuration-driven pipeline for
    evaluating backtracking performance.

    -   Integrates with `lm-evaluation-harness` to run on standard NLP tasks.
    -   Includes hyperparameter optimization with `optuna` to find the best
        `Operator` settings.

-   Interactive CLI: A user-friendly command-line interface (`backtracking-llm`)
    for interactively chatting with any Hugging Face model, with full support
    for configuring backtracking.
-   Built on `transformers`: Fully compatible with the Hugging Face ecosystem,
    allowing you to use thousands of pretrained models.

## Installation

This library requires Python 3.9+.

### Standard Installation

For using the generation and chat features in your projects.

```bash
pip install backtracking-llm
```

### For Benchmarking and Development

To run the benchmarking suite, you must install the `[benchmark]` extra, which
includes `lm-evaluation-harness`, `optuna`, and other necessary dependencies.

```bash
pip install "backtracking-llm[benchmark]"
```

## Quickstart

### 1. Interactive Chat (CLI)

The easiest way to get started is with the built-in interactive CLI. Simply
provide a model name from the Hugging Face Hub.

**Basic Usage:**

```bash
backtracking-llm "Qwen/Qwen2.5-0.5B-Instruct"
```

**Usage with a Backtracking Operator:**

This example will load the model and use the `Repetition` operator to prevent
the model from repeating the same token more than twice.

```bash
backtracking-llm "Qwen/Qwen2.5-0.5B-Instruct" --operator repetition
```

### 2. Library Usage in Python

You can easily integrate the `Generator` into your own Python projects.

```python
import logging
from backtracking_llm.generation import Generator
from backtracking_llm.decision import Repetition

logging.basicConfig(level=logging.INFO)

generator = Generator.from_pretrained('gpt2')

repetition_operator = Repetition(max_repetitions=2)

prompt = ('The best thing about AI is its ability to learn and adapt. For '
          'example, AI can learn to play games, write stories, and even create'
          'art. This is because AI is constantly learning, learning, learning')

completion = generator.generate(
    prompt,
    operator=repetition_operator,
    max_new_tokens=50,
    backtrack_every_n=1
)

print(f"\nPrompt: {prompt}")
print(f"Completion: {completion}")
```

## Benchmarking

The library includes a powerful command-line script for running reproducible
benchmarks. The entire process is controlled by a single YAML configuration
file.

**1. Create a Configuration File**

Create a file, e.g., `experiment.yaml`, to define your benchmark run.

```yaml
# experiment.yaml
model_name_or_path: "Qwen/Qwen2-0.5B-Instruct"
device: "cpu"

run_baseline: true

operator_to_tune: "ProbabilityThreshold"

evaluation:
  tasks: ["gsm8k"]
  limit: 50
  output_dir: "benchmark_results/gsm8k_qwen"

generation:
  max_new_tokens: 256
  temperature: 0.7

hpo:
  n_trials: 20
  search_space:
    min_probability: [0.01, 0.3]
    backtrack_count:
```

**2. Run the Benchmark**

Execute the benchmarking script from your terminal, pointing it to your
configuration file.

```bash
backtracking-llm-benchmark --config experiment.yaml --verbose
```

The runner will execute the pipeline as defined: run the baseline, then run the
20-trial hyperparameter search. All results will be saved as JSON files in the
`benchmark_results/gsm8k_qwen` directory.

For an example of how to configure and run the pipeline programmatically in a
Python script, see the `basic_benchmarking.py` file in the `examples/`
directory.

## Available Backtracking Operators

You can pass any of these operators to the `Generator` or select them in the CLI
via the `--operator` flag.

| Operator                  | Description                                                                  |
| ------------------------- | ---------------------------------------------------------------------------- |
| `ProbabilityThreshold`    | Backtracks if a chosen token's probability is below a threshold.             |
| `EntropyThreshold`        | Backtracks if the probability distribution is too uncertain (high entropy).  |
| `ProbabilityMargin`       | Backtracks if the confidence margin between the top two tokens is too small. |
| `ProbabilityDrop`         | Backtracks if the probability drops sharply compared to the previous token.  |
| `ProbabilityTrend`        | Backtracks if probability drops below a moving average of recent tokens.     |
| `Repetition`              | Backtracks on excessive consecutive token repetitions.                       |
| `NGramOverlap`            | Backtracks when a sequence of N tokens is repeated.                          |
| `LogitThreshold`          | Backtracks if a chosen token's raw logit value is below a threshold.         |

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md)
file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
