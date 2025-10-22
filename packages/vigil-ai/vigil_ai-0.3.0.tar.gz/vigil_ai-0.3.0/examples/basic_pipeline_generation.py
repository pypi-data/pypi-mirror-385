"""Example: Basic pipeline generation with vigil-ai.

This example shows how to generate a simple Snakemake pipeline
from a natural language description.
"""

from vigil_ai import generate_pipeline

# Set your API key first:
# export ANTHROPIC_API_KEY='your-api-key'

# Generate a genomics pipeline
description = """
Filter variants by quality score greater than 30,
annotate with Ensembl gene database,
calculate Ti/Tv ratio and Het/Hom ratio.
"""

pipeline = generate_pipeline(description, template="genomics-starter")

print("Generated Pipeline:")
print("=" * 60)
print(pipeline)
print("=" * 60)

# Save to file
with open("Snakefile", "w") as f:
    f.write(pipeline)

print("\n✓ Pipeline saved to Snakefile")
print("\nNext steps:")
print("  1. Review the generated pipeline")
print("  2. Create step scripts in app/code/lib/steps/")
print("  3. Run: vigil run --cores 4")
