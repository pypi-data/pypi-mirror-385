# InceptBench

Educational question evaluation CLI tool with comprehensive AI-powered assessment. Evaluates questions locally using multiple evaluation modules including quality_evaluator, answer_verification, reading_question_qc, and EduBench tasks.

[![PyPI version](https://badge.fury.io/py/inceptbench.svg)](https://badge.fury.io/py/inceptbench)
[![Python Version](https://img.shields.io/pypi/pyversions/inceptbench.svg)](https://pypi.org/project/inceptbench/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Repository**: [https://github.com/trilogy-group/inceptbench](https://github.com/trilogy-group/inceptbench)

## Features

🎯 **Comprehensive Evaluation**
- **Internal Evaluator** - Scaffolding quality and DI compliance scoring (0-1 scale)
- **Answer Verification** - GPT-4o powered correctness checking
- **Reading Question QC** - MCQ distractor and question quality checks
- **EduBench Tasks** - Educational benchmarks (QA, EC, IP, AG, QG, TMG) (0-10 scale)

📊 **Flexible Output**
- Simplified mode (default) for quick score viewing - ~95% smaller output
- Full mode (`--full`) with all detailed metrics, issues, strengths, and reasoning
- Append mode (`-a`) for collecting multiple evaluations
- JSON output for easy integration

🚀 **Easy to Use**
- Simple CLI interface
- Runs locally with OpenAI and Anthropic API integrations
- Batch processing support
- High-throughput benchmark mode for parallel evaluation
- Only evaluates requested modules (configurable via `submodules_to_run`)

## Installation

```bash
pip install inceptbench

# Or upgrade to latest version
pip install inceptbench --upgrade --no-cache-dir
```

## Quick Start

### 1. Set up API Keys

Create a `.env` file in your working directory:

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
HUGGINGFACE_TOKEN=your_hf_token  # Optional for EduBench tasks
```

### 2. Generate Sample File

```bash
inceptbench example
```

This creates `qs.json` with a complete example question including the `submodules_to_run` configuration.

### 3. Evaluate

```bash
# Simplified output (default)
inceptbench evaluate qs.json

# With progress messages
inceptbench evaluate qs.json --verbose

# Full detailed output
inceptbench evaluate qs.json --full --verbose
```

## Usage

### Commands

#### `evaluate` - Evaluate questions from JSON file

```bash
# Basic evaluation (simplified scores - default)
inceptbench evaluate questions.json

# Verbose output with progress messages
inceptbench evaluate questions.json --verbose

# Full detailed evaluation results
inceptbench evaluate questions.json --full

# Save results to file (overwrite)
inceptbench evaluate questions.json -o results.json

# Append results to file (creates if not exists)
inceptbench evaluate questions.json -a all_evaluations.json --verbose

# Full detailed results to file
inceptbench evaluate questions.json --full -o detailed_results.json --verbose
```

#### `example` - Generate sample input file

```bash
# Generate qs.json (default)
inceptbench example

# Save to custom filename
inceptbench example -o sample.json
```

#### `benchmark` - High-throughput parallel evaluation

Process many questions in parallel for maximum throughput. Perfect for evaluating large datasets.

```bash
# Basic benchmark (100 parallel workers by default)
inceptbench benchmark questions.json

# Custom worker count
inceptbench benchmark questions.json --workers 50

# Save results with verbose output
inceptbench benchmark questions.json -o results.json --verbose

# With custom settings
inceptbench benchmark questions.json --workers 200 -o benchmark_results.json --verbose
```

**Benchmark Output:**
```json
{
  "request_id": "uuid",
  "total_questions": 100,
  "successful": 98,
  "failed": 2,
  "scores": [
    {
      "id": "q1",
      "final_score": 0.91,
      "scores": {
        "quality_evaluator": {"overall": 0.93},
        "answer_verification": {"is_correct": true},
        "reading_question_qc": {"overall_score": 0.8}
      }
    }
  ],
  "failed_ids": ["q42", "q87"],
  "evaluation_time_seconds": 45.3,
  "avg_score": 0.89
}
```

#### `help` - Show detailed help

```bash
inceptbench help
```

## Input Format

The input JSON file must contain:
- `submodules_to_run`: List of evaluation modules to run
- `generated_questions`: Array of questions to evaluate

**Available Modules:**
- `quality_evaluator` - Internal evaluator (scaffolding + DI compliance)
- `answer_verification` - GPT-4o answer correctness checking
- `reading_question_qc` - MCQ distractor quality checks
- `external_edubench` - EduBench educational tasks (QA, EC, IP, etc.)

**Example:**

```json
{
  "submodules_to_run": [
    "quality_evaluator",
    "answer_verification",
    "reading_question_qc"
  ],
  "generated_questions": [
    {
      "id": "q1",
      "type": "mcq",
      "question": "إذا كان ثمن 2 قلم هو 14 ريالًا، فما ثمن 5 أقلام بنفس المعدل؟",
      "answer": "35 ريالًا",
      "answer_explanation": "الخطوة 1: تحليل المسألة — لدينا ثمن 2 قلم وهو 14 ريالًا. نحتاج إلى معرفة ثمن 5 أقلام بنفس المعدل. يجب التفكير في العلاقة بين عدد الأقلام والسعر وكيفية تحويل عدد الأقلام بمعدل ثابت.\nالخطوة 2: تطوير الاستراتيجية — يمكننا أولًا إيجاد ثمن قلم واحد بقسمة 14 ÷ 2 = 7 ريال، ثم ضربه في 5 لإيجاد ثمن 5 أقلام: 7 × 5 = 35 ريالًا.\nالخطوة 3: التطبيق والتحقق — نتحقق من منطقية الإجابة بمقارنة السعر بعدد الأقلام. السعر يتناسب طرديًا مع العدد، وبالتالي 35 ريالًا هي الإجابة الصحيحة والمنطقية.",
      "answer_options": {
        "A": "28 ريالًا",
        "B": "70 ريالًا",
        "C": "30 ريالًا",
        "D": "35 ريالًا"
      },
      "skill": {
        "title": "Grade 6 Mid-Year Comprehensive Assessment",
        "grade": "6",
        "subject": "mathematics",
        "difficulty": "medium",
        "description": "Apply proportional reasoning, rational number operations, algebraic thinking, geometric measurement, and statistical analysis to solve multi-step real-world problems",
        "language": "ar"
      },
      "image_url": null,
      "additional_details": "🔹 **Question generation logic:**\nThis question targets proportional reasoning for Grade 6 students, testing their ability to apply ratios and unit rates to real-world problems. It follows a classic proportionality structure — starting with a known ratio (2 items for 14 riyals) and scaling it up to 5 items. The stepwise reasoning develops algebraic thinking and promotes estimation checks to confirm logical correctness.\n\n🔹 **Personalized insight examples:**\n- Choosing 28 ريالًا shows a misunderstanding by doubling instead of proportionally scaling.\n- Choosing 7 ريالًا indicates the learner found the unit rate but didn't scale it up to 5.\n- Choosing 14 ريالًا confuses the given 2-item cost with the required 5-item cost.\n\n🔹 **Instructional design & DI integration:**\nThe question aligns with *Percent, Ratio, and Probability* learning targets. In DI format 15.7, it models how equivalent fractions and proportional relationships can predict outcomes across different scales. This builds foundational understanding for probability and proportional reasoning. By using a simple, relatable context (price of pens), it connects mathematical ratios to practical real-world applications, supporting concept transfer and cognitive engagement."
    }
  ]
}
```

Use `inceptbench example` to generate this file automatically.

## Authentication

**Required API Keys:**

The tool integrates with OpenAI and Anthropic APIs for running evaluations. Create a `.env` file in your working directory:

```bash
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
HUGGINGFACE_TOKEN=your_hf_token  # Optional, for EduBench tasks
```

The tool will automatically load these from the `.env` file when you run evaluations.

## Output Examples

### Example 1: Evaluate Command - Simplified Mode (Default)

**Command:**
```bash
inceptbench evaluate questions.json
```

**Output:** Returns only essential scores - **~95% smaller output**

```json
{
  "request_id": "c7bce978-66e9-4f8f-ac52-5468340fde8f",
  "evaluations": {
    "q1": {
      "quality_evaluator": {
        "overall": 0.9333333333333333
      },
      "answer_verification": {
        "is_correct": true
      },
      "reading_question_qc": {
        "overall_score": 0.8
      },
      "final_score": 0.9111111111111111
    },
    "q2": {
      "quality_evaluator": {
        "overall": 0.8777777777777778
      },
      "answer_verification": {
        "is_correct": false
      },
      "reading_question_qc": {
        "overall_score": 0.7
      },
      "final_score": 0.5259259259259259
    }
  },
  "evaluation_time_seconds": 12.15
}
```

**Note:** Only requested modules (specified in `submodules_to_run`) will be included in the output. Unrequested modules will not appear.

---

### Example 2: Evaluate Command - Full Mode

**Command:**
```bash
inceptbench evaluate questions.json --full
```

**Output:** Complete evaluation details with all scores, issues, strengths, reasoning, and recommendations:

```json
{
  "request_id": "a8d3f2e1-9c4b-4a7e-b5d6-1f2a3b4c5d6e",
  "evaluations": {
    "q1": {
      "quality_evaluator": {
        "overall": 0.9333333333333333,
        "scores": {
          "correctness": 1.0,
          "grade_alignment": 0.9,
          "difficulty_alignment": 0.9,
          "language_quality": 0.9,
          "pedagogical_value": 1.0,
          "explanation_quality": 0.9,
          "instruction_adherence": 1.0,
          "format_compliance": 1.0,
          "query_relevance": 1.0,
          "di_compliance": 0.9
        },
        "issues": [],
        "strengths": [
          "Excellent three-step scaffolding structure (Analyze → Strategy → Apply)",
          "Strong Direct Instruction compliance with clear modeling",
          "Grade-appropriate proportional reasoning for Grade 6",
          "Clear real-world context with pens and pricing"
        ],
        "recommendation": "accept",
        "suggested_improvements": [
          "Consider adding a visual diagram to support the proportional reasoning",
          "Could strengthen connection to DI Format 15.7 principles"
        ],
        "di_scores": {
          "overall": 0.9,
          "general_principles": 0.95,
          "format_alignment": 0.85,
          "grade_language": 0.9
        },
        "section_evaluations": {
          "question": {
            "section_score": 0.95,
            "issues": [],
            "strengths": [
              "Clear proportional reasoning problem",
              "Grade-appropriate difficulty"
            ],
            "recommendation": "accept"
          },
          "scaffolding": {
            "section_score": 0.92,
            "issues": [
              "Could include more explicit connection to prior knowledge"
            ],
            "strengths": [
              "Three-step structure follows best practices",
              "Verification step included"
            ],
            "recommendation": "accept"
          }
        }
      },
      "answer_verification": {
        "is_correct": true,
        "correct_answer": "35 riyals",
        "confidence": 10,
        "reasoning": "The answer is mathematically correct. To find the price of 5 pens when 2 pens cost 14 riyals: First find unit price: 14 ÷ 2 = 7 riyals per pen. Then multiply by 5: 7 × 5 = 35 riyals. The provided answer matches this calculation."
      },
      "reading_question_qc": {
        "overall_score": 0.8,
        "distractor_checks": {
          "plausibility": {
            "passed": true,
            "score": 0.9,
            "details": "All distractors represent common student errors",
            "category": "distractor"
          },
          "homogeneity": {
            "passed": true,
            "score": 0.85,
            "details": "Distractors have similar format and length",
            "category": "distractor"
          },
          "independence": {
            "passed": true,
            "score": 0.8,
            "details": "Each distractor represents a distinct error pattern",
            "category": "distractor"
          }
        },
        "question_checks": {
          "clarity": {
            "passed": true,
            "score": 0.9,
            "details": "Question is clear and unambiguous",
            "category": "question"
          },
          "complexity": {
            "passed": true,
            "score": 0.75,
            "details": "Appropriate complexity for grade level",
            "category": "question"
          }
        },
        "passed": true
      },
      "final_score": 0.9111111111111111
    }
  },
  "evaluation_time_seconds": 18.42
}
```

---

### Example 3: Benchmark Command - High-Throughput Parallel Mode

**Command:**
```bash
inceptbench benchmark questions.json --workers 100 --verbose
```

**Console Output:**
```
📂 Loading: questions.json
🚀 Benchmark mode: 10 questions with 100 workers
Evaluating questions: 100%|██████████| 10/10 [00:41<00:00,  4.12s/it]
✅ Saved to: benchmark_results.json
📊 Results: 10/10 successful
⏱️  Time: 41.23s
📈 Avg Score: 0.911
```

**Output File (benchmark_results.json):**
```json
{
  "request_id": "312d0684-49ed-4cc8-8ec3-9252daac89aa",
  "total_questions": 10,
  "successful": 10,
  "failed": 0,
  "scores": [
    {
      "id": "q1",
      "final_score": 0.9111111111111111,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9333333333333333
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    },
    {
      "id": "q2",
      "final_score": 0.9074074074074074,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9222222222222223
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    },
    {
      "id": "q3",
      "final_score": 0.9074074074074074,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9222222222222223
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    },
    {
      "id": "q4",
      "final_score": 0.9148148148148149,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9444444444444444
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    },
    {
      "id": "q5",
      "final_score": 0.9259259259259259,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9777777777777779
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    },
    {
      "id": "q6",
      "final_score": 0.9185185185185185,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9555555555555555
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    },
    {
      "id": "q7",
      "final_score": 0.9148148148148149,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9444444444444444
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    },
    {
      "id": "q8",
      "final_score": 0.8814814814814814,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9444444444444444
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.7
        }
      }
    },
    {
      "id": "q9",
      "final_score": 0.9148148148148149,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9444444444444444
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    },
    {
      "id": "q10",
      "final_score": 0.9111111111111111,
      "scores": {
        "quality_evaluator": {
          "overall": 0.9333333333333333
        },
        "answer_verification": {
          "is_correct": true
        },
        "reading_question_qc": {
          "overall_score": 0.8
        }
      }
    }
  ],
  "failed_ids": [],
  "evaluation_time_seconds": 41.23,
  "avg_score": 0.9107407407407407
}
```

**Key differences in benchmark mode:**
- Returns all questions at once with summary statistics
- Includes `total_questions`, `successful`, `failed` counts
- Lists `failed_ids` for easy debugging
- Shows `avg_score` across all questions
- Always uses simplified mode (no detailed scores)
- Optimized for high throughput with parallel processing

## Command Reference

| Command | Description |
|---------|-------------|
| `evaluate` | Evaluate questions from JSON file |
| `benchmark` | High-throughput parallel evaluation for large datasets |
| `example` | Generate sample input file |
| `help` | Show detailed help and usage examples |

### Evaluate Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output PATH` | `-o` | Save results to file (overwrites) |
| `--append PATH` | `-a` | Append results to file (creates if not exists) |
| `--full` | `-f` | Return full detailed evaluation results (default: simplified scores only) |
| `--verbose` | `-v` | Show progress messages |
| `--timeout SECS` | `-t` | Request timeout in seconds (default: 600) |

### Benchmark Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output PATH` | `-o` | Save results to file |
| `--workers NUM` | `-w` | Number of parallel workers (default: 100) |
| `--verbose` | `-v` | Show progress messages |

## Examples

### Basic Evaluation

```bash
# Evaluate with default settings (simplified scores)
inceptbench evaluate questions.json

# With progress messages
inceptbench evaluate questions.json --verbose
```

### Full Detailed Evaluation

```bash
# Get complete evaluation with all details
inceptbench evaluate questions.json --full --verbose

# Save full results to file
inceptbench evaluate questions.json --full -o detailed_results.json
```

### Collecting Multiple Evaluations

```bash
# Append multiple evaluations to one file
inceptbench evaluate test1.json -a all_results.json --verbose
inceptbench evaluate test2.json -a all_results.json --verbose
inceptbench evaluate test3.json -a all_results.json --verbose

# Result: all_results.json contains an array of all 3 evaluations
```

### Batch Processing

```bash
# Evaluate all files and append to one results file
for file in questions/*.json; do
  inceptbench evaluate "$file" -a batch_results.json --verbose
done
```

### Benchmark Mode (High-Throughput Parallel Processing)

For large-scale evaluations, use benchmark mode to process hundreds of questions in parallel:

```bash
# Evaluate 100 questions with 100 parallel workers
inceptbench benchmark large_dataset.json --verbose

# Process 1000 questions with 200 workers, save results
inceptbench benchmark dataset_1000.json --workers 200 -o benchmark_results.json --verbose

# Results include: success rate, avg score, timing, and failed question IDs
```

**When to use benchmark mode:**
- Large datasets (100+ questions)
- Need for maximum throughput
- Want simplified scores only (no detailed output)
- Need to identify failed questions quickly

**Output includes:**
- Total questions processed
- Success/failure counts
- Failed question IDs for easy debugging
- Average score across all questions
- Total evaluation time
- One simplified score per question

## Evaluation Modules

### quality_evaluator (Internal Evaluator)
- Scaffolding quality assessment (answer_explanation structure)
- Direct Instruction (DI) compliance checking
- Pedagogical structure validation
- Language quality scoring
- Grade and difficulty alignment
- Returns scores on 0-1 scale

### answer_verification
- GPT-4o powered correctness checking
- Mathematical accuracy validation
- Confidence scoring (0-10)
- Reasoning explanation

### reading_question_qc
- MCQ distractor quality checks
- Question clarity validation
- Overall quality scoring

### external_edubench
- **QA**: Question Answering - Can the model answer the question?
- **EC**: Error Correction - Can the model identify and correct errors?
- **IP**: Instructional Planning - Can the model provide step-by-step solutions?
- **AG**: Answer Generation - Can the model generate correct answers?
- **QG**: Question Generation - Question quality assessment
- **TMG**: Test Making Generation - Test design quality
- Returns scores on 0-10 scale

All modules are optional and configurable via `submodules_to_run` in the input JSON.

## Requirements

- Python >= 3.11
- OpenAI API key
- Anthropic API key
- Hugging Face token (optional, for EduBench tasks)

## Support

- **Repository**: [https://github.com/trilogy-group/inceptbench](https://github.com/trilogy-group/inceptbench)
- **Issues**: [GitHub Issues](https://github.com/trilogy-group/inceptbench/issues)
- **Help**: Run `inceptbench help` for detailed documentation

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made by the Incept Team**
