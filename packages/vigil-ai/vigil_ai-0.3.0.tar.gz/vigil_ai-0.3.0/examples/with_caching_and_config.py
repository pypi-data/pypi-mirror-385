"""Example: Using configuration and caching.

This example shows how to configure vigil-ai and use caching
to reduce API costs.
"""

from vigil_ai import generate_pipeline
from vigil_ai.cache import clear_cache, get_cache_dir
from vigil_ai.config import Config, get_config

# Load configuration
config = get_config()

print("Current configuration:")
print(f"  Model: {config.model}")
print(f"  Max tokens: {config.max_tokens}")
print(f"  Cache enabled: {config.cache_responses}")
print(f"  Cache directory: {config.cache_dir}")

# Customize configuration
config.model = "claude-3-5-sonnet-20241022"
config.cache_responses = True
config.max_tokens = 2048

# Save configuration
config.save()
print("\n✓ Configuration saved to .vigil-ai.yaml")

# Generate pipeline (will be cached)
description = "Filter variants >30, calculate metrics"

print(f"\n📊 First call (will hit API)...")
pipeline1 = generate_pipeline(description)

print(f"\n📊 Second call (will use cache)...")
pipeline2 = generate_pipeline(description)

# Verify caching worked
assert pipeline1 == pipeline2
print("✓ Cache working! Same result returned.")

# Check cache
cache_dir = get_cache_dir()
cache_files = list(cache_dir.glob("*.json"))
print(f"\n✓ Cache contains {len(cache_files)} responses")

# Clear cache when done
# deleted = clear_cache()
# print(f"\n✓ Cleared {deleted} cached responses")
