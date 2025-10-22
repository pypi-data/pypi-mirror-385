# vigil-ai

**AI-powered workflow generation with foundation models for reproducible science**

vigil-ai extends [Vigil](https://github.com/Science-Abundance/vigil) with AI capabilities, making scientific workflow creation accessible through natural language and specialized foundation models.

## Features

- **Natural language → Pipeline**: Generate Snakemake workflows from plain English descriptions
- **Foundation models**: 10+ specialized models for biology, chemistry, materials science
- **Domain-specific AI**: Auto-select the best model for your scientific domain
- **AI debugging**: Get intelligent suggestions for fixing pipeline errors
- **Workflow optimization**: Analyze and optimize for speed, cost, or resource usage
- **Task-based interface**: Simple, high-level API for common workflows
- **MCP integration**: Works with Claude Desktop and AI assistants

## Installation

**Basic (Claude models only):**
```bash
pip install vigil-ai
```

**With science models (ESM-2, BioGPT, ChemBERTa, etc.):**
```bash
pip install 'vigil-ai[science]'
```

**Or install with Vigil:**
```bash
pip install 'vigil[ai]'              # Basic
pip install 'vigil[ai,science]'      # With science models
```

## Requirements

- Python 3.11+
- Vigil >= 0.2.1
- Anthropic API key (get one at https://console.anthropic.com/)

## Setup

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or add to your `.env` file:

```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Generate Pipeline from Description

```bash
vigil ai create "Filter variants by quality >30, annotate with Ensembl, calculate Ti/Tv ratio"
```

Output:
```
✓ Pipeline created: app/code/pipelines/Snakefile

Next steps:
  1. Review the generated pipeline
  2. Create necessary step scripts
  3. vigil run --cores 4
```

### Debug Pipeline Errors

```bash
vigil ai debug

# Or specify error log
vigil ai debug --error-log .snakemake/log/error.log
```

Output:
```
Analyzing error...

Root Cause:
The rule 'filter_variants' failed because the input file 'variants.csv' was not found.

Suggested Fix:
1. Check that your data exists: ls app/data/samples/
2. Verify file name matches exactly (case-sensitive)
3. If file is missing, download or create it
4. Run: vigil doctor to check project health

Prevention:
Add input validation before running pipeline.
```

### Optimize Workflow

```bash
vigil ai optimize --focus speed

# Or optimize for cost
vigil ai optimize --focus cost
```

Output:
```
Optimization Suggestions:

Rule: filter_variants
Issue: Sequential processing
Suggestion: Add threads: 4 and use parallel processing
Impact: 4x faster with multi-core

Rule: annotate
Issue: Repeated API calls
Suggestion: Implement caching for Ensembl queries
Impact: 10x faster on reruns
```

## Quick Start (Task-Based Interface)

The simplest way to use vigil-ai is through the task-based interface:

```python
from vigil_ai.tasks import PipelineGenerator, ErrorDebugger, ModelSelector

# 1. Generate a pipeline for biology
bio_gen = PipelineGenerator(domain="biology")
pipeline = bio_gen.create("Filter variants >30, annotate, calculate Ti/Tv")
bio_gen.create_and_save(pipeline, "workflow.smk")

# 2. Debug errors when they occur
debugger = ErrorDebugger()
fix = debugger.analyze("FileNotFoundError: variants.csv not found")
print(fix)

# 3. Get model recommendations
selector = ModelSelector()
model, reason = selector.recommend("I need to analyze protein sequences")
print(reason)  # "Recommended biology model (ESM-2) for protein analysis"
```

## Foundation Models

vigil-ai supports 10+ specialized foundation models across scientific domains:

### Biology Models
- **ESM-2** (650M, 3B, 15B) - Protein language models from Meta AI
- **BioGPT** - Biomedical text generation
- **ProtGPT2** - Protein sequence generation

### Chemistry Models
- **ChemBERTa** - Molecular property prediction
- **MolFormer** - Chemical structure analysis

### Materials Science Models
- **MatBERT** - Materials property prediction

### General Models
- **Claude 3.5 Sonnet** (default) - General-purpose, most capable
- **Claude 3 Opus** - Most powerful
- **Galactica** - Scientific knowledge and reasoning

### Using Domain-Specific Models

```python
from vigil_ai import get_model, ModelDomain

# Automatically select best model for domain
bio_model = get_model(domain=ModelDomain.BIOLOGY)      # Returns ESM-2
chem_model = get_model(domain=ModelDomain.CHEMISTRY)   # Returns ChemBERTa
mat_model = get_model(domain=ModelDomain.MATERIALS)    # Returns MatBERT

# Use specific model by name
esm = get_model(name="esm-2-650m")
embedding = esm.embed("MKFLKFSLLTAVLLSVVFAFSSCGDDDDTGYLPPSQAIQDLL")

# Generate with domain-specific model
from vigil_ai import generate_pipeline
pipeline = generate_pipeline(
    "Analyze protein sequences and predict function",
    domain=ModelDomain.BIOLOGY  # Uses ESM-2
)
```

## Python API (Low-Level)

For more control, use the low-level API:

```python
from vigil_ai import generate_pipeline, ai_debug, ai_optimize

# Generate pipeline
pipeline = generate_pipeline(
    "Filter variants by quality >30, calculate Ti/Tv ratio",
    template="genomics-starter",
    model="claude-3-5-sonnet-20241022"  # Or specify domain
)
print(pipeline)

# Debug error
fix = ai_debug("FileNotFoundError: variants.csv not found")
print(fix)

# Optimize workflow
suggestions = ai_optimize(focus="speed")
print(suggestions)
```

## Examples

### Create Imaging Analysis Pipeline

```bash
vigil ai create "Segment cells from microscopy images, count cells per field, measure intensity"
```

Generates:
```python
rule segment_cells:
    input: "data/images/{sample}.tif"
    output: "artifacts/masks/{sample}_mask.png"
    script: "../lib/steps/segment.py"

rule count_cells:
    input: "artifacts/masks/{sample}_mask.png"
    output: "artifacts/counts/{sample}_counts.json"
    script: "../lib/steps/count.py"

rule measure_intensity:
    input:
        image="data/images/{sample}.tif",
        mask="artifacts/masks/{sample}_mask.png"
    output: "artifacts/intensity/{sample}_intensity.csv"
    script: "../lib/steps/measure.py"
```

### Interactive Mode

```bash
vigil ai chat
```

Starts interactive session:
```
> Create a pipeline to filter variants
✓ Pipeline generated

> Add a rule to calculate metrics
✓ Added metrics rule

> How can I make this faster?
Suggestions:
1. Add parallel processing
2. Cache intermediate results
...
```

## Configuration

Create `.vigil-ai.yaml` in your project:

```yaml
ai:
  model: claude-3-5-sonnet-20241022  # Claude model to use
  max_tokens: 4096                     # Max response length
  temperature: 0.7                     # Creativity (0-1)
  cache_responses: true                # Cache AI responses
```

## Advanced Usage

### Generate Step Script

```python
from vigil_ai.generator import generate_step_script

script = generate_step_script(
    rule_name="filter_variants",
    description="Filter variants by quality score >30",
    inputs=["variants.csv"],
    outputs=["filtered.parquet"],
    language="python"
)

with open("app/code/lib/steps/filter.py", "w") as f:
    f.write(script)
```

### Custom Prompts

```python
from vigil_ai import generate_pipeline

pipeline = generate_pipeline(
    description="""
    Create a multi-sample variant calling pipeline:
    1. Align reads with BWA
    2. Mark duplicates with Picard
    3. Call variants with GATK
    4. Filter and annotate
    """,
    template="genomics-starter"
)
```

## Architecture

vigil-ai is part of a **three-layer architecture** for reproducible science:

```
┌─────────────────────────────────────────────────────┐
│  Agents Layer: AI Assistants                        │
│  (Claude Desktop, custom agents)                    │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│  Application Layer: vigil-ai (THIS PACKAGE)         │
│  - MCP Server Integration                           │
│  - Foundation Models (Claude, ESM, BioGPT, etc.)    │
│  - Task Interface (PipelineGenerator, etc.)         │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│  Foundation Layer: Vigil Core                       │
│  - Snakemake pipelines                              │
│  - Artifact management                              │
│  - Receipt tracking                                 │
└─────────────────────────────────────────────────────┘
```

### MCP Integration

vigil-ai extends the Vigil MCP server with 5 AI-powered verbs:

- `ai_generate_pipeline` - Generate Snakemake workflow from description
- `ai_debug_error` - Analyze and fix pipeline errors
- `ai_optimize_workflow` - Suggest performance optimizations
- `ai_list_models` - List available foundation models
- `ai_get_model_info` - Get model metadata and capabilities

**Use with Claude Desktop:**

```json
{
  "mcpServers": {
    "vigil": {
      "command": "vigil",
      "args": ["mcp"]
    }
  }
}
```

Then ask Claude: *"Generate a pipeline to filter variants and calculate metrics"*

## All Supported Models

### General-Purpose (API-based)
- `claude-3-5-sonnet-20241022` (default, recommended)
- `claude-3-opus-20240229` (most powerful)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-haiku-20240307` (fastest, cheapest)

### Biology (requires `[science]` install)
- `esm-2-650m` - Meta AI protein model, 650M params
- `esm-2-3b` - Meta AI protein model, 3B params (GPU recommended)
- `esm-2-15b` - Meta AI protein model, 15B params (GPU required)
- `biogpt` - Microsoft biomedical text model
- `protgpt2` - Protein sequence generation

### Chemistry (requires `[science]` install)
- `chemberta-v2` - DeepChem molecular property model
- `molformer` - Molecular structure analysis

### Materials Science (requires `[science]` install)
- `matbert` - Materials property prediction

## Cost Estimates

**Claude models (API-based):**
- Pipeline generation: ~$0.02-0.05 per request
- Debugging: ~$0.01-0.03 per request
- Optimization: ~$0.03-0.07 per request

**Science models (local inference):**
- Free to use (runs on your hardware)
- Requires GPU for optimal performance (ESM-2, BioGPT)
- CPU inference possible but slower

**Cost optimization tips:**
- Enable response caching: `cache_responses: true` in `.vigil-ai.yaml`
- Use smaller models for simpler tasks (`claude-3-haiku` vs `claude-3-opus`)
- Use local science models when applicable (no API costs)

## Example Gallery

See the [`examples/`](examples/) directory for complete examples:

- **[task_based_workflow.py](examples/task_based_workflow.py)** - Complete workflow using task interface
- **[domain_specific_models.py](examples/domain_specific_models.py)** - Using biology/chemistry/materials models
- **[basic_pipeline_generation.py](examples/basic_pipeline_generation.py)** - Low-level API examples
- **[with_caching_and_config.py](examples/with_caching_and_config.py)** - Configuration and caching

Run any example:
```bash
python examples/task_based_workflow.py
```

## Limitations

**General:**
- Claude models require internet connection and API key
- Generated pipelines need review before use in production
- AI suggestions should be validated by domain experts
- Not a replacement for scientific expertise

**Science models:**
- Require `pip install vigil-ai[science]` and additional dependencies
- Large models (ESM-2 15B) require significant GPU memory (40GB+)
- Local inference slower than API-based models
- May require domain-specific preprocessing

## Development

```bash
# Clone repo
git clone https://github.com/Science-Abundance/vigil
cd vigil/packages/vigil-core-ai

# Install in dev mode with all dependencies
pip install -e '.[dev,science]'

# Run tests
pytest

# Run tests with science models (requires GPU)
pytest -m science

# Lint
ruff check .

# Type check
mypy src/

# Run examples
python examples/task_based_workflow.py
python examples/domain_specific_models.py
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## License

Apache-2.0

## Support

- GitHub Issues: https://github.com/Science-Abundance/vigil/issues
- Documentation: https://github.com/Science-Abundance/vigil
- Discord: [coming soon]

## Acknowledgments

Built with:
- [Anthropic Claude](https://www.anthropic.com/) - General-purpose AI capabilities
- [Vigil](https://github.com/Science-Abundance/vigil) - Reproducible science platform
- [HuggingFace Transformers](https://huggingface.co/transformers/) - Foundation model infrastructure

Foundation models:
- **ESM-2** - Meta AI ([paper](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v1))
- **BioGPT** - Microsoft Research ([paper](https://arxiv.org/abs/2210.10341))
- **ChemBERTa** - DeepChem ([paper](https://arxiv.org/abs/2010.09885))
- **MatBERT** - Materials Project ([paper](https://arxiv.org/abs/2109.15290))
- **Galactica** - Meta AI ([paper](https://arxiv.org/abs/2211.09085))
