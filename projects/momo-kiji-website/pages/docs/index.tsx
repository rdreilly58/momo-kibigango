import Head from "next/head";
import Link from "next/link";

export default function Docs() {
  return (
    <>
      <Head>
        <title>Documentation – momo-kiji</title>
        <meta name="description" content="momo-kiji documentation, guides, and API reference" />
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
        <div className="container-wide">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Documentation</h1>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Getting Started */}
            <Link href="/docs/getting-started" className="block bg-white p-6 rounded-lg border border-gray-200 hover:border-peach-400 hover:shadow-md transition-all">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Getting Started</h3>
              <p className="text-gray-700">Installation, setup, and your first ANE compilation.</p>
            </Link>

            {/* 3-Tier Setup */}
            <Link href="/docs/3-tier-setup" className="block bg-white p-6 rounded-lg border border-gray-200 hover:border-peach-400 hover:shadow-md transition-all">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-xl font-semibold text-gray-900">3-Tier Setup</h3>
                <span className="text-xs bg-peach-100 text-peach-700 px-2 py-1 rounded-full font-medium">NEW</span>
              </div>
              <p className="text-gray-700">Configure the revolutionary 3-tier speculative decoding.</p>
            </Link>

            {/* API Reference */}
            <Link href="/docs/api" className="block bg-white p-6 rounded-lg border border-gray-200 hover:border-peach-400 hover:shadow-md transition-all">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">API Reference</h3>
              <p className="text-gray-700">Complete Python API documentation and examples.</p>
            </Link>

            {/* Model Support */}
            <Link href="/docs/models" className="block bg-white p-6 rounded-lg border border-gray-200 hover:border-peach-400 hover:shadow-md transition-all">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Model Support</h3>
              <p className="text-gray-700">Supported model formats and conversion guides.</p>
            </Link>

            {/* Performance */}
            <Link href="/docs/performance" className="block bg-white p-6 rounded-lg border border-gray-200 hover:border-peach-400 hover:shadow-md transition-all">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Performance Tuning</h3>
              <p className="text-gray-700">Optimize your models for maximum ANE efficiency.</p>
            </Link>

            {/* Examples */}
            <Link href="https://github.com/ReillyDesignStudio/momo-kiji/tree/main/examples" className="block bg-white p-6 rounded-lg border border-gray-200 hover:border-peach-400 hover:shadow-md transition-all">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Examples</h3>
              <p className="text-gray-700">Real-world examples and sample applications.</p>
            </Link>
          </div>

          <div className="mt-12 bg-peach-50 rounded-lg p-8 border border-peach-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Need help?</h2>
            <p className="text-gray-700 mb-4">
              Join our community for support, discussions, and updates.
            </p>
            <div className="flex gap-4">
              <a href="https://discord.gg/momo-kiji" className="btn-primary">
                Discord Community
              </a>
              <a href="https://github.com/ReillyDesignStudio/momo-kiji/issues" className="btn-secondary">
                GitHub Issues
              </a>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}