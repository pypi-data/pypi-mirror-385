# AI Agents Guide

This repository is designed to work seamlessly with AI agents and assistants. Here's how to interact with it effectively.

## Available Tools

### Core Commands
- `vigil run --cores 4` - Run the full pipeline locally
- `vigil promote` - Generate receipts for artifacts
- `uv run conformance` - Check against golden metrics
- `vigil url` - Generate shareable VigilURL
- `vigil doctor` - Run health checks

### AI Tool-Calling Verbs
The repository exposes these verbs for AI agents:

1. **preview_data** - Examine data handles and samples
2. **run_target** - Execute specific pipeline targets
3. **promote** - Generate receipts for completed runs

## Data Structure

### Inputs
- `app/data/handles/` - Typed data handles with S3 URIs and offline fallbacks
- `app/data/samples/` - Small sample datasets for offline development

### Outputs
- `app/code/artifacts/` - Pipeline outputs (gitignored)
- `app/code/receipts/` - Generated receipts with checksums (gitignored)

### Configuration
- `vigil.yaml` - Main configuration file
- `app/code/configs/params.yaml` - Pipeline parameters
- `app/code/configs/profiles/` - Environment-specific configs (cpu, gpu, slurm)

## Best Practices for AI Agents

1. **Use vigil CLI for core commands** - `vigil run`, `vigil promote`, `vigil doctor`
2. **Check conformance** - Run `uv run conformance` before promoting artifacts
3. **Generate receipts** - Use `vigil promote` for all meaningful outputs
4. **Respect offline mode** - Sample data allows development without S3 access
5. **Use typed data handles** - Leverage the dhandle.json format for data pointers

## Notebook Integration

- `app/notes/notebooks/` - Jupyter notebooks for exploration
- Use "Send selection to Notebook" feature for AI-generated code cells
- Notebooks are git-tracked for reproducibility

## CI/CD Integration

- GitHub Actions run conformance checks on PRs
- Vigil preview links are automatically generated
- All checks use `uv run` for consistency

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Run `uv sync` to install all dependencies
2. **GPU not detected**: Check with `vigil doctor` and ensure CUDA is properly installed
3. **S3 access issues**: Use sample data for offline development
4. **Pipeline errors**: Check Snakemake logs and use `vigil inspect` for debugging

### Getting Help

- Check `vigil doctor` for system diagnostics
- Use `vigil inspect` to examine artifacts and receipts
- Review pipeline logs in `app/code/logs/`
- Consult the Vigil documentation for advanced usage

## AI Integration Examples

### Basic Pipeline Execution
```bash
# Preview what will be executed
vigil ai preview_data

# Run specific targets
vigil ai run_target --target="filter_variants" --confirm=true

# Generate receipts
vigil ai promote
```

### Advanced Workflows
```bash
# Generate new pipeline from description
vigil ai create "Analyze protein-protein interactions" --template="genomics-starter"

# Get model recommendations
vigil ai recommend "predict protein structure"

# List available models
vigil ai list-models
```

## Security Considerations

- All AI operations respect local-only execution by default
- Receipts provide cryptographic verification of AI-generated outputs
- No sensitive data is sent to external AI services without explicit consent
- Use `vigil policy` to enforce AI usage policies
