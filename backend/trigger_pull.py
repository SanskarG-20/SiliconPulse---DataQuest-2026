from app.sources.perplexity_source import pull_perplexity_signals
from app.sources.x_source import pull_x_signals

print("Pulling from Perplexity...")
count1 = pull_perplexity_signals()
print(f"Added {count1} Perplexity events")

print("Pulling from X...")
count2 = pull_x_signals()
print(f"Added {count2} X events")

print(f"Total: {count1 + count2} events added to stream")
