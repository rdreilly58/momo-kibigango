import { useState } from 'react';

interface TierInfo {
  name: string;
  description: string;
  specs: string[];
  color: string;
}

const tiers: TierInfo[] = [
  {
    name: 'Tier 1: Draft Model',
    description: 'Local Llama 2B running on Apple Neural Engine',
    specs: ['2B parameters', '50ms latency', 'Instant response', 'Always available'],
    color: '#FB923C',
  },
  {
    name: 'Tier 2: Qualification', 
    description: 'Local Llama 8B validates draft quality',
    specs: ['8B parameters', '100ms validation', 'Quality control', 'Rejects bad drafts'],
    color: '#FDBA74',
  },
  {
    name: 'Tier 3: Cloud Fallback',
    description: 'OpenRouter Opus for complex queries',
    specs: ['Top-tier model', 'Only when needed', 'Pay per use', 'Highest quality'],
    color: '#FED7AA',
  },
];

export default function PyramidArchitecture() {
  const [hoveredTier, setHoveredTier] = useState<number | null>(null);

  return (
    <div className="relative bg-white rounded-lg shadow-xl p-8">
      <svg 
        viewBox="0 0 400 300" 
        className="w-full h-auto"
        onMouseLeave={() => setHoveredTier(null)}
      >
        {/* Pyramid layers with hover interaction */}
        <g>
          {/* Tier 3 (top) */}
          <path 
            d="M200,50 L280,150 L120,150 Z" 
            fill={hoveredTier === 2 ? '#FBBF24' : tiers[2].color}
            stroke="#FB923C" 
            strokeWidth="2"
            className="cursor-pointer transition-all"
            onMouseEnter={() => setHoveredTier(2)}
          />
          
          {/* Tier 2 (middle) */}
          <path 
            d="M120,150 L280,150 L320,220 L80,220 Z" 
            fill={hoveredTier === 1 ? '#F59E0B' : tiers[1].color}
            stroke="#FB923C" 
            strokeWidth="2"
            className="cursor-pointer transition-all"
            onMouseEnter={() => setHoveredTier(1)}
          />
          
          {/* Tier 1 (base) */}
          <path 
            d="M80,220 L320,220 L360,290 L40,290 Z" 
            fill={hoveredTier === 0 ? '#EA580C' : tiers[0].color}
            stroke="#F97316" 
            strokeWidth="2"
            className="cursor-pointer transition-all"
            onMouseEnter={() => setHoveredTier(0)}
          />
        </g>
        
        {/* Labels */}
        <text x="200" y="110" textAnchor="middle" className="fill-gray-800 font-semibold text-sm pointer-events-none">
          Tier 3: Cloud
        </text>
        <text x="200" y="190" textAnchor="middle" className="fill-gray-800 font-semibold text-sm pointer-events-none">
          Tier 2: Qualify
        </text>
        <text x="200" y="260" textAnchor="middle" className="fill-white font-semibold text-sm pointer-events-none">
          Tier 1: Draft
        </text>
      </svg>

      {/* Tooltip/Info Box */}
      {hoveredTier !== null && (
        <div className="absolute top-0 right-0 bg-gray-900 text-white p-4 rounded-lg shadow-lg max-w-xs animate-fade-in">
          <h4 className="font-semibold mb-2">{tiers[hoveredTier].name}</h4>
          <p className="text-sm mb-3 text-gray-200">{tiers[hoveredTier].description}</p>
          <ul className="text-xs space-y-1">
            {tiers[hoveredTier].specs.map((spec, i) => (
              <li key={i} className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span>{spec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600 font-medium">
          Hybrid Config 4: Local draft + qualifier with cloud fallback
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Hover over pyramid layers to learn more
        </p>
      </div>
    </div>
  );
}