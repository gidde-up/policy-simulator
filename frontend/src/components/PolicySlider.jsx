import React from 'react';

function PolicySlider({
  label,
  value,
  onChange,
  min = -30,
  max = 30,
  step = 1,
  unit = '%',
  description = '',
  color = 'blue',
}) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    orange: 'bg-orange-500',
    purple: 'bg-purple-500',
  };

  const isPositive = value > 0;
  const isNegative = value < 0;

  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-1">
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
        <span
          className={`
            text-sm font-bold px-2 py-0.5 rounded
            ${isPositive ? 'text-green-700 bg-green-100' : ''}
            ${isNegative ? 'text-red-700 bg-red-100' : ''}
            ${value === 0 ? 'text-gray-500 bg-gray-100' : ''}
          `}
        >
          {value > 0 ? '+' : ''}{value}{unit}
        </span>
      </div>

      {description && (
        <p className="text-xs text-gray-500 mb-2">{description}</p>
      )}

      <div className="relative">
        {/* Track background */}
        <div className="h-2 bg-gray-200 rounded-full">
          {/* Filled portion */}
          <div
            className={`h-full rounded-full transition-all ${colorClasses[color]}`}
            style={{
              width: `${((value - min) / (max - min)) * 100}%`,
              marginLeft: min < 0 ? `${(-min / (max - min)) * 100}%` : '0',
              transform: value < 0 ? `translateX(-100%)` : 'none',
            }}
          />
        </div>

        {/* Center marker for bipolar sliders */}
        {min < 0 && (
          <div
            className="absolute top-0 w-0.5 h-2 bg-gray-400"
            style={{ left: `${(-min / (max - min)) * 100}%` }}
          />
        )}

        {/* Actual slider input */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="absolute top-0 left-0 w-full h-2 opacity-0 cursor-pointer"
        />

        {/* Custom thumb */}
        <div
          className={`
            absolute top-1/2 -translate-y-1/2 w-4 h-4
            ${colorClasses[color]} rounded-full shadow-md
            border-2 border-white cursor-pointer
            transition-all hover:scale-110
          `}
          style={{
            left: `calc(${((value - min) / (max - min)) * 100}% - 8px)`,
          }}
        />
      </div>

      {/* Min/Max labels */}
      <div className="flex justify-between mt-1 text-xs text-gray-400">
        <span>{min}{unit}</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );
}

export default PolicySlider;
