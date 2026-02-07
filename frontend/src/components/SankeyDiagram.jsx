import React, { useMemo } from 'react';

/**
 * Simple Sankey-style flow diagram for policy transmission visualization
 * Shows: Policy -> Sector -> Effect Type -> Demographics
 */

function SankeyDiagram({ transmissionPaths }) {
  if (!transmissionPaths || transmissionPaths.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="font-bold text-gray-800 mb-4">Policy Transmission</h3>
        <p className="text-gray-500 text-center py-8">
          Run a simulation to see how policies transmit to employment effects
        </p>
      </div>
    );
  }

  // Process paths into layers
  const { policies, sectors, effects, demographics, links } = useMemo(() => {
    const policies = new Set();
    const sectors = new Set();
    const effects = new Set();
    const demographics = new Set();
    const linkMap = new Map();

    transmissionPaths.forEach(path => {
      const key = `${path.source}-${path.target}`;
      const existing = linkMap.get(key) || { ...path, value: 0 };
      existing.value += path.value;
      linkMap.set(key, existing);

      if (path.type === 'policy_to_sector') {
        policies.add(path.source);
        sectors.add(path.target);
      } else if (path.type === 'sector_to_effect') {
        sectors.add(path.source);
        effects.add(path.target);
      } else if (path.type === 'effect_to_demo') {
        effects.add(path.source);
        demographics.add(path.target);
      }
    });

    return {
      policies: Array.from(policies),
      sectors: Array.from(sectors).slice(0, 6), // Limit for visibility
      effects: Array.from(effects),
      demographics: Array.from(demographics),
      links: Array.from(linkMap.values()),
    };
  }, [transmissionPaths]);

  // Color schemes
  const colors = {
    policy: '#3B82F6',    // Blue
    sector: '#10B981',    // Green
    effect: '#F59E0B',    // Amber
    demographic: '#8B5CF6', // Purple
  };

  // Calculate positions
  const width = 700;
  const height = 400;
  const nodeWidth = 120;
  const nodeHeight = 30;
  const layerGap = (width - nodeWidth * 4) / 3;

  const getLayerX = (layer) => {
    const positions = { policy: 0, sector: 1, effect: 2, demographic: 3 };
    return positions[layer] * (nodeWidth + layerGap);
  };

  const getNodeY = (items, index, totalHeight = height) => {
    const spacing = totalHeight / (items.length + 1);
    return spacing * (index + 1) - nodeHeight / 2;
  };

  // Build node positions
  const nodePositions = useMemo(() => {
    const positions = {};

    policies.forEach((name, i) => {
      positions[name] = { x: getLayerX('policy'), y: getNodeY(policies, i), layer: 'policy' };
    });
    sectors.forEach((name, i) => {
      positions[name] = { x: getLayerX('sector'), y: getNodeY(sectors, i), layer: 'sector' };
    });
    effects.forEach((name, i) => {
      positions[name] = { x: getLayerX('effect'), y: getNodeY(effects, i), layer: 'effect' };
    });
    demographics.forEach((name, i) => {
      positions[name] = { x: getLayerX('demographic'), y: getNodeY(demographics, i), layer: 'demographic' };
    });

    return positions;
  }, [policies, sectors, effects, demographics]);

  // Calculate max value for scaling
  const maxValue = Math.max(...links.map(l => l.value), 1);

  // Generate curved path between nodes
  const generatePath = (source, target, value) => {
    const sourcePos = nodePositions[source];
    const targetPos = nodePositions[target];

    if (!sourcePos || !targetPos) return null;

    const x1 = sourcePos.x + nodeWidth;
    const y1 = sourcePos.y + nodeHeight / 2;
    const x2 = targetPos.x;
    const y2 = targetPos.y + nodeHeight / 2;

    const midX = (x1 + x2) / 2;
    const strokeWidth = Math.max(2, (value / maxValue) * 15);

    return {
      d: `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`,
      strokeWidth,
      sourceLayer: sourcePos.layer,
    };
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h3 className="font-bold text-gray-800 mb-4">Policy Transmission Flow</h3>
      <p className="text-sm text-gray-500 mb-4">
        See how policy changes flow through the economy to create employment effects
      </p>

      <div className="overflow-x-auto">
        <svg width={width} height={height} className="mx-auto">
          {/* Layer labels */}
          <text x={getLayerX('policy') + nodeWidth / 2} y={20} textAnchor="middle" className="text-xs font-medium fill-gray-500">
            Policy
          </text>
          <text x={getLayerX('sector') + nodeWidth / 2} y={20} textAnchor="middle" className="text-xs font-medium fill-gray-500">
            Sector
          </text>
          <text x={getLayerX('effect') + nodeWidth / 2} y={20} textAnchor="middle" className="text-xs font-medium fill-gray-500">
            Effect Type
          </text>
          <text x={getLayerX('demographic') + nodeWidth / 2} y={20} textAnchor="middle" className="text-xs font-medium fill-gray-500">
            Demographics
          </text>

          {/* Links */}
          <g className="links">
            {links.map((link, i) => {
              const path = generatePath(link.source, link.target, link.value);
              if (!path) return null;

              const color = colors[path.sourceLayer] || colors.policy;

              return (
                <path
                  key={i}
                  d={path.d}
                  fill="none"
                  stroke={color}
                  strokeWidth={path.strokeWidth}
                  strokeOpacity={0.4}
                  className="transition-all hover:stroke-opacity-80"
                />
              );
            })}
          </g>

          {/* Nodes */}
          <g className="nodes">
            {Object.entries(nodePositions).map(([name, pos]) => (
              <g key={name} transform={`translate(${pos.x}, ${pos.y})`}>
                <rect
                  width={nodeWidth}
                  height={nodeHeight}
                  rx={4}
                  fill={colors[pos.layer]}
                  className="transition-all hover:opacity-80"
                />
                <text
                  x={nodeWidth / 2}
                  y={nodeHeight / 2 + 4}
                  textAnchor="middle"
                  fill="white"
                  fontSize={10}
                  fontWeight="500"
                >
                  {name.length > 14 ? name.substring(0, 12) + '...' : name}
                </text>
              </g>
            ))}
          </g>
        </svg>
      </div>

      {/* Legend */}
      <div className="flex justify-center space-x-6 mt-4 text-xs">
        <span className="flex items-center">
          <span className="w-3 h-3 rounded mr-1" style={{ backgroundColor: colors.policy }} />
          Policy Actions
        </span>
        <span className="flex items-center">
          <span className="w-3 h-3 rounded mr-1" style={{ backgroundColor: colors.sector }} />
          Economic Sectors
        </span>
        <span className="flex items-center">
          <span className="w-3 h-3 rounded mr-1" style={{ backgroundColor: colors.effect }} />
          Job Effects
        </span>
        <span className="flex items-center">
          <span className="w-3 h-3 rounded mr-1" style={{ backgroundColor: colors.demographic }} />
          Demographics
        </span>
      </div>
    </div>
  );
}

export default SankeyDiagram;
