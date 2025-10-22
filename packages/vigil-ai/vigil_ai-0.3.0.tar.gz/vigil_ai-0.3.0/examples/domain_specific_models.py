"""Example: Using domain-specific foundation models.

This example demonstrates how to use different foundation models
for different scientific domains (biology, chemistry, materials).
"""

from vigil_ai import ModelDomain, get_model
from vigil_ai.tasks import ModelSelector, PipelineGenerator

# Set API key first
# export ANTHROPIC_API_KEY='your-api-key'

print("=" * 70)
print("DOMAIN-SPECIFIC MODEL USAGE")
print("=" * 70)

# ═══════════════════════════════════════════════════════════
# 1. BIOLOGY: Protein Analysis with ESM-2
# ═══════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("1. BIOLOGY - Protein Analysis")
print("─" * 70)

# Get biology model (automatically selects ESM-2)
bio_model = get_model(domain=ModelDomain.BIOLOGY)
print(f"Model: {bio_model.get_metadata().display_name}")
print(f"Capabilities: {[str(c) for c in bio_model.get_metadata().capabilities]}")

# Generate pipeline for protein analysis
bio_generator = PipelineGenerator(domain="biology")
protein_pipeline = bio_generator.preview(
    """
    Analyze protein sequences:
    1. Load FASTA files
    2. Generate sequence embeddings
    3. Predict secondary structure
    4. Classify protein families
    """
)

print("\n✓ Biology pipeline generated")
print("  Model: ESM-2 650M (protein language model)")
print("  Domain: Biology")
print("  Use case: Protein sequence analysis")

# Example: Get protein embeddings (if science extras installed)
try:
    # This requires: pip install vigil-ai[science]
    embedding = bio_model.embed("MKFLKFSLLTAVLLSVVFAFSSCGDDDDTGYLPPSQAIQDLL")
    print(f"  Embedding dimension: {len(embedding)}")
except NotImplementedError:
    print("  (Embedding requires science models: pip install vigil-ai[science])")

# ═══════════════════════════════════════════════════════════
# 2. CHEMISTRY: Molecular Analysis with ChemBERTa
# ═══════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("2. CHEMISTRY - Molecular Analysis")
print("─" * 70)

# Get chemistry model (automatically selects ChemBERTa)
chem_model = get_model(domain=ModelDomain.CHEMISTRY)
print(f"Model: {chem_model.get_metadata().display_name}")
print(f"Capabilities: {[str(c) for c in chem_model.get_metadata().capabilities]}")

# Generate pipeline for chemical analysis
chem_generator = PipelineGenerator(domain="chemistry")
chemical_pipeline = chem_generator.preview(
    """
    Screen drug candidates:
    1. Load SMILES structures
    2. Calculate molecular properties
    3. Predict bioactivity
    4. Rank by binding affinity
    """
)

print("\n✓ Chemistry pipeline generated")
print("  Model: ChemBERTa (molecular language model)")
print("  Domain: Chemistry")
print("  Use case: Drug screening, molecular property prediction")

# ═══════════════════════════════════════════════════════════
# 3. MATERIALS SCIENCE: MatBERT
# ═══════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("3. MATERIALS SCIENCE - Materials Analysis")
print("─" * 70)

# Get materials model (automatically selects MatBERT)
materials_model = get_model(domain=ModelDomain.MATERIALS)
print(f"Model: {materials_model.get_metadata().display_name}")
print(f"Capabilities: {[str(c) for c in materials_model.get_metadata().capabilities]}")

# Generate pipeline for materials analysis
materials_generator = PipelineGenerator(domain="materials")
materials_pipeline = materials_generator.preview(
    """
    Analyze crystal structures:
    1. Load crystallographic data
    2. Calculate formation energies
    3. Predict mechanical properties
    4. Identify stable phases
    """
)

print("\n✓ Materials pipeline generated")
print("  Model: MatBERT (materials science model)")
print("  Domain: Materials Science")
print("  Use case: Crystal structure analysis, property prediction")

# ═══════════════════════════════════════════════════════════
# 4. GENERAL SCIENCE: Claude or Galactica
# ═══════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("4. GENERAL SCIENCE - Multi-domain Analysis")
print("─" * 70)

# Get general-purpose model (Claude by default)
general_model = get_model(domain=ModelDomain.GENERAL)
print(f"Model: {general_model.get_metadata().display_name}")
print(f"Capabilities: {[str(c) for c in general_model.get_metadata().capabilities]}")

# Generate multi-domain pipeline
general_generator = PipelineGenerator(domain="general")
general_pipeline = general_generator.preview(
    """
    Multi-omics analysis:
    1. Integrate genomic, proteomic, and metabolomic data
    2. Perform pathway analysis
    3. Generate visualizations
    4. Write scientific report
    """
)

print("\n✓ General science pipeline generated")
print("  Model: Claude 3.5 Sonnet (general-purpose)")
print("  Domain: General / Multi-domain")
print("  Use case: Complex analyses, scientific writing")

# ═══════════════════════════════════════════════════════════
# 5. MODEL COMPARISON
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("MODEL COMPARISON BY DOMAIN")
print("=" * 70)

selector = ModelSelector()

domains = [
    ModelDomain.BIOLOGY,
    ModelDomain.CHEMISTRY,
    ModelDomain.MATERIALS,
    ModelDomain.GENERAL,
]

for domain in domains:
    models = selector.list_by_domain(domain)
    print(f"\n{domain.value.upper()} Models:")
    for model_name in models:
        print(f"  - {model_name}")

# ═══════════════════════════════════════════════════════════
# 6. CHOOSING THE RIGHT MODEL
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("CHOOSING THE RIGHT MODEL")
print("=" * 70)

recommendations = [
    ("I need to analyze protein sequences", ModelDomain.BIOLOGY),
    ("I want to screen drug compounds", ModelDomain.CHEMISTRY),
    ("I'm studying crystal structures", ModelDomain.MATERIALS),
    ("I need to write a scientific report", ModelDomain.GENERAL),
]

for task, expected_domain in recommendations:
    model, reason = selector.recommend(task)
    print(f"\nTask: '{task}'")
    print(f"→ {reason}")

print("\n" + "=" * 70)
print("\n✓ Domain-specific models ready for scientific workflows!")
print("\nInstallation:")
print("  pip install vigil-ai              # Basic (Claude only)")
print("  pip install vigil-ai[science]     # +Science models (ESM, BioGPT, etc.)")
print("  pip install vigil-ai[all]         # Everything")
