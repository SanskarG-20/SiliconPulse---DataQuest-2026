
"""
Central dictionary for company intelligence.
Used for:
1. Source ingestion (generating queries/keywords)
2. Retrieval (synonym expansion)
3. Demo generation (ensuring coverage)
"""

COMPANY_DICT = {
  "NVIDIA": {
    "aliases": ["nvidia", "nvda", "geforce", "cuda", "h100", "b100", "h200", "blackwell", "jensen huang"],
    "topics": ["AI GPU supply", "TSMC capacity", "CoWoS", "HBM", "DGX", "Blackwell architecture"]
  },
  "Apple": {
    "aliases": ["apple", "aapl", "iphone", "mac", "m-series", "vision pro", "tsmc", "tim cook"],
    "topics": ["chip supply chain", "M4", "manufacturing", "acquisition", "AI features"]
  },
  "Google": {
    "aliases": ["google", "alphabet", "deepmind", "gemini", "gcp", "vertex ai", "tpu", "waymo", "sundar pichai"],
    "topics": ["AI models", "TPU roadmap", "cloud infra", "AI startup acquisition", "search updates"]
  },
  "Microsoft": {
    "aliases": ["microsoft", "msft", "azure", "openai", "copilot", "satya nadella", "github"],
    "topics": ["Azure AI infra", "datacenter chips", "OpenAI partnership", "Copilot integration"]
  },
  "Meta": {
    "aliases": ["meta", "facebook", "instagram", "whatsapp", "llama", "zuck", "mark zuckerberg"],
    "topics": ["AI infra", "Llama releases", "datacenter expansion", "AR/VR"]
  },
  "Amazon": {
    "aliases": ["amazon", "aws", "amzn", "anthropic", "trainium", "inferentia", "andy jassy"],
    "topics": ["AWS AI infra", "chips", "cloud expansion", "Bedrock"]
  },
  "Intel": {
    "aliases": ["intel", "intc", "18a", "ifs", "foundry", "gaudi", "pat gelsinger"],
    "topics": ["foundry wins", "node progress", "CHIPS act", "cost cutting"]
  },
  "AMD": {
    "aliases": ["amd", "mi300", "epyc", "xilinx", "lisa su"],
    "topics": ["AI accelerators", "datacenter chips", "partnerships", "ROCm"]
  },
  "TSMC": {
    "aliases": ["tsmc", "taiwan semiconductor", "n2", "n3", "cowoS", "fabs", "cc wei"],
    "topics": ["yield improvements", "capacity deals", "fab expansion", "pricing"]
  },
  "Samsung": {
    "aliases": ["samsung", "hbm3e", "exynos", "foundry", "galaxy"],
    "topics": ["HBM supply", "foundry progress", "yield", "memory chips"]
  }
}
