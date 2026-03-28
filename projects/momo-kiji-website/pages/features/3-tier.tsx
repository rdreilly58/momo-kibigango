import Head from "next/head";
import Link from "next/link";
import { useState } from "react";
import { trackExternalClick, trackGitHubAction } from "../../lib/analytics";

export default function ThreeTierFeature() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <>
      <Head>
        <title>3-Tier Speculative Decoding – momo-kiji</title>
        <meta
          name="description"
          content="Revolutionary 3-tier pyramid architecture for 92% quality at $5-10/month. Get production-ready inference on Apple Silicon."
        />
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
            <a 
              href="https://github.com/ReillyDesignStudio/momo-kiji" 
              className="btn-primary"
              onClick={() => trackGitHubAction('3-tier-page')}
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-peach-50 to-white py-16">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              3-Tier Speculative Decoding
            </h1>
            <p className="text-xl text-gray-700 mb-8">
              Revolutionary pyramid architecture achieves 92% quality at just $5-10/month.
              Production-ready inference that scales with your needs.
            </p>
            <div className="flex gap-4 justify-center">
              <Link href="/docs/3-tier-setup" className="btn-primary">
                Get Started →
              </Link>
              <a href="#architecture" className="btn-secondary">
                Learn More
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Performance Metrics */}
      <section className="py-16 bg-white">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">
            Performance That Delivers
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-peach-600 mb-2">6s</div>
              <div className="text-gray-700 font-medium">Startup Time</div>
              <div className="text-sm text-gray-500">vs 30s traditional</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-peach-600 mb-2">92%</div>
              <div className="text-gray-700 font-medium">Quality Score</div>
              <div className="text-sm text-gray-500">Opus-level quality</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-peach-600 mb-2">$5-10</div>
              <div className="text-gray-700 font-medium">Monthly Cost</div>
              <div className="text-sm text-gray-500">80% cost reduction</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-peach-600 mb-2">2.1x</div>
              <div className="text-gray-700 font-medium">Speed Boost</div>
              <div className="text-sm text-gray-500">Real-time inference</div>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-16 bg-gray-50">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">
            Revolutionary Pyramid Architecture
          </h2>
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-lg text-gray-700 leading-relaxed mb-6">
                Our 3-tier pyramid architecture combines local and cloud models for optimal performance:
              </p>
              <div className="space-y-4">
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <h3 className="font-semibold text-gray-900 mb-2">Tier 1: Draft Model</h3>
                  <p className="text-gray-700">Local Llama 2B on Apple Neural Engine for instant response</p>
                </div>
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <h3 className="font-semibold text-gray-900 mb-2">Tier 2: Qualification</h3>
                  <p className="text-gray-700">Local Llama 8B validates draft quality in real-time</p>
                </div>
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <h3 className="font-semibold text-gray-900 mb-2">Tier 3: Cloud Fallback</h3>
                  <p className="text-gray-700">OpenRouter Opus for complex queries when needed</p>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="bg-white rounded-lg shadow-xl p-8">
                {/* Pyramid Visualization */}
                <svg viewBox="0 0 400 300" className="w-full h-auto">
                  <defs>
                    <linearGradient id="pyramidGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#FED7AA" />
                      <stop offset="100%" stopColor="#FB923C" />
                    </linearGradient>
                  </defs>
                  
                  {/* Pyramid layers */}
                  <path d="M200,50 L280,150 L120,150 Z" fill="#FED7AA" stroke="#FB923C" strokeWidth="2"/>
                  <path d="M120,150 L280,150 L320,220 L80,220 Z" fill="#FDBA74" stroke="#FB923C" strokeWidth="2"/>
                  <path d="M80,220 L320,220 L360,290 L40,290 Z" fill="#FB923C" stroke="#F97316" strokeWidth="2"/>
                  
                  {/* Labels */}
                  <text x="200" y="110" textAnchor="middle" className="fill-gray-800 font-semibold text-sm">
                    Tier 3: Cloud
                  </text>
                  <text x="200" y="190" textAnchor="middle" className="fill-gray-800 font-semibold text-sm">
                    Tier 2: Qualify
                  </text>
                  <text x="200" y="260" textAnchor="middle" className="fill-white font-semibold text-sm">
                    Tier 1: Draft
                  </text>
                </svg>
                <p className="text-center text-sm text-gray-600 mt-4">
                  Hybrid Config 4: Local draft + qualifier with cloud fallback
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-16 bg-white">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">Perfect For</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gray-50 rounded-lg p-8">
              <div className="text-3xl mb-4">🚀</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Startups</h3>
              <p className="text-gray-700">
                Launch AI features without breaking the bank. Scale from prototype to production seamlessly.
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-8">
              <div className="text-3xl mb-4">🏢</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Enterprises</h3>
              <p className="text-gray-700">
                Reduce inference costs by 80% while maintaining quality. Perfect for high-volume applications.
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-8">
              <div className="text-3xl mb-4">👨‍💻</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Developers</h3>
              <p className="text-gray-700">
                Build responsive AI apps with local-first architecture. Ship features faster with lower latency.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Comparison */}
      <section className="py-16 bg-gray-50">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">
            Cost Comparison
          </h2>
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-left text-gray-700 font-semibold">Solution</th>
                    <th className="px-6 py-4 text-center text-gray-700 font-semibold">Monthly Cost</th>
                    <th className="px-6 py-4 text-center text-gray-700 font-semibold">Quality</th>
                    <th className="px-6 py-4 text-center text-gray-700 font-semibold">Latency</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="px-6 py-4 font-medium">Traditional Cloud API</td>
                    <td className="px-6 py-4 text-center text-gray-700">$50-200</td>
                    <td className="px-6 py-4 text-center text-gray-700">95%</td>
                    <td className="px-6 py-4 text-center text-gray-700">200-500ms</td>
                  </tr>
                  <tr className="border-b">
                    <td className="px-6 py-4 font-medium">Local-Only (70B)</td>
                    <td className="px-6 py-4 text-center text-gray-700">$0</td>
                    <td className="px-6 py-4 text-center text-gray-700">85%</td>
                    <td className="px-6 py-4 text-center text-gray-700">2-5s</td>
                  </tr>
                  <tr className="bg-peach-50">
                    <td className="px-6 py-4 font-semibold text-peach-600">momo-kiji 3-Tier</td>
                    <td className="px-6 py-4 text-center font-semibold text-peach-600">$5-10</td>
                    <td className="px-6 py-4 text-center font-semibold text-peach-600">92%</td>
                    <td className="px-6 py-4 text-center font-semibold text-peach-600">50-100ms</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-peach-100 to-peach-50">
        <div className="container-wide text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Ready for Production-Grade AI?
          </h2>
          <p className="text-xl text-gray-700 mb-8 max-w-2xl mx-auto">
            Join developers using 3-tier speculative decoding for faster, cheaper, better AI inference.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/docs/3-tier-setup" className="btn-primary">
              Get Started with 3-Tier →
            </Link>
            <a 
              href="https://github.com/ReillyDesignStudio/momo-kiji/tree/main/examples/3-tier" 
              className="btn-secondary"
              onClick={() => trackExternalClick('https://github.com/ReillyDesignStudio/momo-kiji/tree/main/examples/3-tier', '3-tier-examples')}
            >
              View Examples
            </a>
          </div>
        </div>
      </section>
    </>
  );
}