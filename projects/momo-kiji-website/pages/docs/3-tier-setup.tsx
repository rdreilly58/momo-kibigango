import Head from "next/head";
import Link from "next/link";

export default function ThreeTierSetup() {
  return (
    <>
      <Head>
        <title>3-Tier Setup Guide – momo-kiji</title>
        <meta name="description" content="Complete guide to setting up 3-tier speculative decoding with momo-kiji" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-200">
        <div className="container-wide flex justify-between items-center py-4">
          <Link href="/" className="text-2xl font-bold text-peach-600">
            🍑 momo-kiji
          </Link>
          <div className="flex gap-6">
            <Link href="/#features" className="text-gray-700 hover:text-peach-600 font-medium">
              Features
            </Link>
            <Link href="/docs" className="text-gray-700 hover:text-peach-600 font-medium">
              Docs
            </Link>
            <a href="https://github.com/ReillyDesignStudio/momo-kiji" className="btn-primary">
              GitHub
            </a>
          </div>
        </div>
      </nav>

      <section className="py-16">
        <div className="container-wide max-w-4xl">
          <div className="mb-8">
            <Link href="/docs" className="text-peach-600 hover:text-peach-700 font-medium">
              ← Back to Docs
            </Link>
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-8">3-Tier Setup Guide</h1>

          <div className="prose prose-lg max-w-none">
            <p className="lead text-xl text-gray-700 mb-8">
              Set up production-ready 3-tier speculative decoding in minutes. This guide walks you through 
              configuring the pyramid architecture for 92% quality at just $5-10/month.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Prerequisites</h2>
            <ul className="space-y-2 mb-8">
              <li>macOS 14+ with Apple Silicon (M1/M2/M3)</li>
              <li>Python 3.9 or higher</li>
              <li>momo-kiji installed (<code className="text-peach-600">pip install momo-kiji</code>)</li>
              <li>OpenRouter API key (for cloud fallback)</li>
            </ul>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Step 1: Install Dependencies</h2>
            <div className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto mb-8">
              <pre className="font-mono text-sm">
{`# Install momo-kiji with 3-tier support
pip install momo-kiji[3tier]

# Download required models
momo-kiji download-models --preset 3tier

# This downloads:
# - Llama 2B (draft model)
# - Llama 8B (qualifier model)
# - Configuration files`}</pre>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Step 2: Configure API Keys</h2>
            <div className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto mb-8">
              <pre className="font-mono text-sm">
{`# Set OpenRouter API key for cloud fallback
export OPENROUTER_API_KEY="your-key-here"

# Or add to your .env file
echo "OPENROUTER_API_KEY=your-key-here" >> .env`}</pre>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Step 3: Initialize 3-Tier Configuration</h2>
            <div className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto mb-8">
              <pre className="font-mono text-sm">
{`import momo_kiji as mk

# Initialize with Hybrid Config 4
config = mk.ThreeTierConfig(
    # Tier 1: Draft model on ANE
    draft_model="llama-2b-ane",
    draft_device="ane",
    
    # Tier 2: Qualifier on GPU
    qualifier_model="llama-8b",
    qualifier_device="gpu",
    
    # Tier 3: Cloud fallback
    cloud_provider="openrouter",
    cloud_model="anthropic/claude-3-opus",
    
    # Performance settings
    max_draft_tokens=256,
    qualification_threshold=0.85,
    cloud_fallback_threshold=0.7
)

# Create the 3-tier pipeline
pipeline = mk.SpeculativePipeline(config)`}</pre>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Step 4: Use the Pipeline</h2>
            <div className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto mb-8">
              <pre className="font-mono text-sm">
{`# Simple generation
response = pipeline.generate("Explain quantum computing")

# With streaming
for chunk in pipeline.stream("Write a story about AI"):
    print(chunk, end="", flush=True)

# Check tier usage
stats = pipeline.get_stats()
print(f"Draft accepted: {'{stats.draft_acceptance_rate:.1%}'}")
print(f"Cloud usage: {'{stats.cloud_usage_rate:.1%}'}")
print(f"Estimated cost: ${'{stats.estimated_cost:.2f}'}")`}</pre>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Step 5: Production Deployment</h2>
            <div className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto mb-8">
              <pre className="font-mono text-sm">
{`# server.py
from momo_kiji import create_app

app = create_app(
    config_file="3tier.yaml",
    enable_monitoring=True,
    enable_caching=True
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)`}</pre>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Configuration Reference</h2>
            <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">3tier.yaml</h3>
              <div className="bg-gray-50 p-4 rounded font-mono text-sm">
                <pre>{`version: 1.0
tiers:
  draft:
    model: llama-2b-ane
    device: ane
    max_tokens: 256
    temperature: 0.7
  
  qualifier:
    model: llama-8b
    device: gpu
    threshold: 0.85
    
  cloud:
    provider: openrouter
    model: anthropic/claude-3-opus
    fallback_threshold: 0.7
    budget_limit: 10.00  # Monthly USD

monitoring:
  enable: true
  webhook: https://your-webhook.com/alerts
  
caching:
  enable: true
  ttl: 3600  # 1 hour`}</pre>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Performance Tuning</h2>
            
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-peach-50 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">For Lower Latency</h3>
                <ul className="text-sm space-y-1 text-gray-700">
                  <li>• Reduce max_draft_tokens to 128</li>
                  <li>• Increase qualification_threshold to 0.9</li>
                  <li>• Use smaller draft model (1B params)</li>
                </ul>
              </div>
              
              <div className="bg-peach-50 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">For Lower Cost</h3>
                <ul className="text-sm space-y-1 text-gray-700">
                  <li>• Decrease qualification_threshold to 0.8</li>
                  <li>• Enable aggressive caching</li>
                  <li>• Use smaller cloud model for fallback</li>
                </ul>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Monitoring & Observability</h2>
            <p className="mb-4">
              The 3-tier system includes built-in monitoring to track performance and costs:
            </p>
            <div className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto mb-8">
              <pre className="font-mono text-sm">
{`# Enable detailed logging
pipeline.enable_logging(level="DEBUG")

# Get real-time metrics
metrics = pipeline.get_metrics()
print(f"Avg latency: {'{metrics.avg_latency_ms}'}ms")
print(f"P95 latency: {'{metrics.p95_latency_ms}'}ms")
print(f"Tier distribution: {'{metrics.tier_distribution}'}")

# Export to monitoring service
pipeline.export_metrics(format="prometheus")`}</pre>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mt-12 mb-4">Troubleshooting</h2>
            
            <div className="space-y-4">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">High cloud usage?</h4>
                <p className="text-gray-700">
                  Check your qualification threshold. Too high means more cloud fallbacks. 
                  Start with 0.85 and adjust based on quality requirements.
                </p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Slow startup?</h4>
                <p className="text-gray-700">
                  Use model preloading: <code className="text-peach-600">pipeline.preload_models()</code> 
                  at application start to avoid cold starts.
                </p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">ANE not available?</h4>
                <p className="text-gray-700">
                  The system automatically falls back to GPU. Check ANE availability with 
                  <code className="text-peach-600">mk.check_ane_status()</code>.
                </p>
              </div>
            </div>

            <div className="mt-12 p-6 bg-peach-50 rounded-lg border border-peach-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to deploy?</h3>
              <p className="text-gray-700 mb-4">
                Join our Discord for help with production deployments and performance optimization.
              </p>
              <Link href="/features/3-tier" className="text-peach-600 hover:text-peach-700 font-medium">
                Learn more about 3-tier architecture →
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}