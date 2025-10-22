"""Example: Using task-based interface for common workflows.

This example shows how to use the high-level task interface for
vigil-ai, which provides simple APIs for common scientific workflows.
"""

from vigil_ai.tasks import (
    ErrorDebugger,
    ModelSelector,
    PipelineGenerator,
    WorkflowOptimizer,
)

# ═══════════════════════════════════════════════════════════
# 1. PIPELINE GENERATION
# ═══════════════════════════════════════════════════════════

print("=" * 60)
print("1. PIPELINE GENERATION")
print("=" * 60)

# Create a generator for biology
bio_generator = PipelineGenerator(domain="biology")

# Generate a genomics pipeline
pipeline = bio_generator.create(
    "Filter variants by quality >30, annotate with Ensembl, calculate Ti/Tv ratio"
)

print("\nGenerated Pipeline (first 500 chars):")
print(pipeline[:500] + "...")

# Save to file
bio_generator.create_and_save(
    "Process protein sequences and predict function",
    output="protein_workflow.smk",
    dry_run=True,  # Don't actually save (for demo)
)

print("\n✓ Pipeline generated successfully")

# ═══════════════════════════════════════════════════════════
# 2. ERROR DEBUGGING
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("2. ERROR DEBUGGING")
print("=" * 60)

# Create debugger
debugger = ErrorDebugger()

# Analyze an error
fix = debugger.analyze(
    error="FileNotFoundError: data/samples/variants.csv not found",
    context={"snakefile": "rule filter:\n  input: 'data/samples/variants.csv'"},
)

print("\nDebug Suggestions (first 500 chars):")
print(fix[:500] + "...")

# Quick fix for common errors
quick_fix = debugger.quick_fix("Rule 'annotate' failed: missing input files")
print("\n✓ Debug analysis complete")

# ═══════════════════════════════════════════════════════════
# 3. WORKFLOW OPTIMIZATION
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("3. WORKFLOW OPTIMIZATION")
print("=" * 60)

# Create optimizer
optimizer = WorkflowOptimizer()

# Optimize for speed
speed_suggestions = optimizer.optimize_for_speed("workflow.smk")
print("\nSpeed Optimization (placeholder):")
print("  - Enable parallel execution with --cores")
print("  - Cache intermediate results")
print("  - Use faster file formats (parquet vs CSV)")

# Optimize for memory
memory_suggestions = optimizer.optimize_for_memory("workflow.smk")

# Optimize for cost
cost_suggestions = optimizer.optimize_for_cost("workflow.smk")

print("\n✓ Optimization analysis complete")

# ═══════════════════════════════════════════════════════════
# 4. MODEL SELECTION
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("4. MODEL SELECTION")
print("=" * 60)

# Create selector
selector = ModelSelector()

# List all available models
all_models = selector.list_all()
print(f"\nAvailable models ({len(all_models)} total):")
for model in all_models[:5]:
    print(f"  - {model}")
print("  ...")

# Get model for specific domain
bio_model = selector.for_domain("biology")
print(f"\nBiology model: {bio_model.get_metadata().display_name}")

# Get model info
esm_info = selector.get_info("esm-2-650m")
print(f"\nESM-2 650M Info:")
print(f"  Domain: {esm_info['domain']}")
print(f"  Capabilities: {', '.join(esm_info['capabilities'])}")
print(f"  Description: {esm_info['description']}")

# Recommend model based on task description
model, reasoning = selector.recommend(
    "I need to analyze protein sequences and predict their function"
)
print(f"\nRecommendation: {reasoning}")

print("\n✓ Model selection complete")

# ═══════════════════════════════════════════════════════════
# COMPLETE WORKFLOW EXAMPLE
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("COMPLETE WORKFLOW EXAMPLE")
print("=" * 60)

# 1. Select appropriate model
selector = ModelSelector()
model, reason = selector.recommend("genomic variant analysis")
print(f"\n1. Model Selected: {reason}")

# 2. Generate pipeline
generator = PipelineGenerator(domain="biology")
pipeline = generator.create("Filter variants >30, calculate metrics")
print("2. Pipeline Generated ✓")

# 3. If errors occur, debug them
debugger = ErrorDebugger()
print("3. Debugger Ready ✓")

# 4. Optimize the workflow
optimizer = WorkflowOptimizer()
print("4. Optimizer Ready ✓")

print("\n✓ Complete workflow ready!")
print("\nNext steps:")
print("  1. Review the generated pipeline")
print("  2. Run: vigil run --cores 4")
print("  3. If errors occur, use ErrorDebugger")
print("  4. Optimize with WorkflowOptimizer")
print("  5. Promote results: vigil promote")
