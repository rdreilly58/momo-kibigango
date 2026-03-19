import Head from "next/head";
import Link from "next/link";
import { trackExternalClick, trackGitHubAction, trackDiscordJoin } from "../lib/analytics";

export default function Home() {
  return (
    <>
      <Head>
        <title>momo-kiji – CUDA for Apple Neural Engine</title>
        <meta
          name="description"
          content="Open-source SDK for compiling models to Apple Neural Engine. Get 10x efficiency."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-200">
        <div className="container-wide flex justify-between items-center py-4">
          <div className="text-2xl font-bold text-peach-600">🍑 momo-kiji</div>
          <div className="flex gap-6">
            <a href="#why" className="text-gray-700 hover:text-peach-600 font-medium">
              Why
            </a>
            <a href="#features" className="text-gray-700 hover:text-peach-600 font-medium">
              Features
            </a>
            <a href="#docs" className="text-gray-700 hover:text-peach-600 font-medium">
              Docs
            </a>
            <a href="https://github.com/ReillyDesignStudio/momo-kiji" className="btn-primary">
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-gradient-to-br from-peach-50 to-white py-24">
        <div className="container-wide">
          <div className="max-w-3xl">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              CUDA for Apple Neural Engine
            </h1>
            <p className="text-xl text-gray-700 mb-8">
              Stop letting ANE go unused. Compile any model, target ANE directly, get 10x efficiency.
            </p>
            <div className="flex gap-4">
              <a href="https://github.com/ReillyDesignStudio/momo-kiji#readme" className="btn-primary">
                Get Started →
              </a>
              <a href="https://github.com/ReillyDesignStudio/momo-kiji" className="btn-secondary">
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section id="why" className="py-20 bg-white">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">Why momo-kiji?</h2>
          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">The Problem</h3>
              <p className="text-gray-700 leading-relaxed">
                Apple Neural Engine is on every Apple device. Yet most developers ignore it. Why?
              </p>
              <ul className="mt-6 space-y-3 text-gray-700">
                <li>✗ CoreML is limited and locked</li>
                <li>✗ No direct ANE access</li>
                <li>✗ Can't compile your own models</li>
                <li>✗ Efficiency left on the table</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">The Solution</h3>
              <p className="text-gray-700 leading-relaxed">
                momo-kiji brings ANE into the open. Compile any model, target ANE directly.
              </p>
              <ul className="mt-6 space-y-3 text-gray-700">
                <li>✓ Direct ANE compilation</li>
                <li>✓ Bring your own models</li>
                <li>✓ 10x better efficiency</li>
                <li>✓ Open source, MIT licensed</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: "🎯",
                title: "Direct ANE",
                desc: "Bypass CoreML. Compile directly to ANE.",
              },
              {
                icon: "⚡",
                title: "10x Efficiency",
                desc: "Specialized hardware acceleration on every Apple device.",
              },
              {
                icon: "📱",
                title: "macOS & iOS",
                desc: "Target both platforms with a single toolchain.",
              },
              {
                icon: "🔄",
                title: "Multi-Format",
                desc: "ONNX, PyTorch, TensorFlow input support.",
              },
              {
                icon: "📊",
                title: "Auto Quantization",
                desc: "Automatic INT8 and FP16 quantization.",
              },
              {
                icon: "🛠",
                title: "Python API",
                desc: "Simple, intuitive Python interface.",
              },
            ].map((feature, i) => (
              <div key={i} className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-700">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Start / Docs */}
      <section id="docs" className="py-20 bg-white">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Quick Start</h2>
          <div className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto">
            <pre className="font-mono text-sm">
{`# Install
pip install momo-kiji

# Compile a model
momo-kiji compile model.onnx \\
  --target ane \\
  --output model_ane.mlmodel

# Use in your app
import momo_kiji as mk
model = mk.load("model_ane.mlmodel")
output = model.predict(input_data)`}
            </pre>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-peach-600">
        <div className="container-wide text-center text-white">
          <h2 className="text-4xl font-bold mb-6">Ready to compile for ANE?</h2>
          <p className="text-xl mb-8 opacity-90">
            Start with the documentation or jump into the GitHub repository.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <a
              href="https://github.com/ReillyDesignStudio/momo-kiji/blob/main/docs/source/index.rst"
              className="px-6 py-3 bg-white text-peach-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Read Docs →
            </a>
            <a
              href="https://github.com/ReillyDesignStudio/momo-kiji"
              className="px-6 py-3 border-2 border-white text-white rounded-lg font-semibold hover:bg-peach-700 transition-colors"
            >
              View GitHub
            </a>
            <a
              href="https://discord.gg/DHRbKbzr"
              className="px-6 py-3 border-2 border-white text-white rounded-lg font-semibold hover:bg-peach-700 transition-colors"
            >
              Join Discord
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container-wide">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-semibold text-white mb-4">🍑 momo-kiji</h4>
              <p className="text-sm">CUDA for Apple Neural Engine</p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Links</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="https://github.com/ReillyDesignStudio/momo-kiji" className="hover:text-white">
                    GitHub
                  </a>
                </li>
                <li>
                  <a href="https://github.com/ReillyDesignStudio/momo-kiji#readme" className="hover:text-white">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="https://discord.gg/DHRbKbzr" className="hover:text-white">
                    Discord
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Community</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="https://github.com/ReillyDesignStudio/momo-kiji/issues" className="hover:text-white">
                    Issues
                  </a>
                </li>
                <li>
                  <a href="https://discord.gg/DHRbKbzr" className="hover:text-white">
                    Community (Discord)
                  </a>
                </li>
                <li>
                  <a href="https://github.com/ReillyDesignStudio/momo-kiji/blob/main/CONTRIBUTING.md" className="hover:text-white">
                    Contributing
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="https://reillydesignstudio.com" className="hover:text-white">
                    Reilly Design Studio
                  </a>
                </li>
                <li>
                  <a href="https://github.com/ReillyDesignStudio" className="hover:text-white">
                    GitHub Org
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-sm text-center">
            <p>© 2026 Reilly Design Studio. MIT Licensed.</p>
          </div>
        </div>
      </footer>
    </>
  );
}
