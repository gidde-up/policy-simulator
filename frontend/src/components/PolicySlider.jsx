import React from 'react';

function clamp(v, min, max) {
  if (Number.isNaN(v)) return 0;
  return Math.min(max, Math.max(min, v));
}

function PolicySlider({
  label,
  value,
  onChange,
  min = 0,
  max = 30,
  step = 1,
  unit = '%',
  description = '',
  color = 'blue',
  disabled = false,
  disabledNote = '',
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
    <div className={`mb-4 ${disabled ? 'opacity-50' : ''}`}
         title={disabled ? disabledNote : undefined}>
      <div className="flex justify-between items-center mb-1">
        <label className="text-sm font-medium text-gray-700">
          {label}
          {disabled && (
            <span className="ml-2 text-xs text-gray-600 font-normal">
              ({disabledNote})
            </span>
          )}
        </label>
        {/* Numeric input beside the slider */}
        <span className="flex items-center space-x-1">
          <input
            type="number"
            min={min}
            max={max}
            step={step}
            value={value}
            disabled={disabled}
            onChange={(e) => onChange(clamp(parseFloat(e.target.value), min, max))}
            aria-label={`${label} value`}
            className={`
              w-16 text-sm font-bold text-right px-1 py-0.5 rounded border
              focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600
              ${isPositive ? 'text-green-800 bg-green-50 border-green-200' : ''}
              ${isNegative ? 'text-red-800 bg-red-50 border-red-200' : ''}
              ${value === 0 ? 'text-gray-600 bg-gray-50 border-gray-200' : ''}
              ${disabled ? 'cursor-not-allowed' : ''}
            `}
          />
          <span className="text-xs text-gray-600">{unit}</span>
        </span>
      </div>

      {description && (
        <p className="text-xs text-gray-600 mb-2">{description}</p>
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

        {/* Actual slider input: visible keyboard focus ring on the track */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          aria-label={label}
          className={`
            absolute top-0 left-0 w-full h-2 opacity-0
            focus:outline-none focus-visible:opacity-100
            focus-visible:accent-blue-600
            ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
          `}
        />

        {/* Custom thumb (decorative: pointer-events-none so the real
            input underneath receives all mouse events) */}
        <div
          className={`
            absolute top-1/2 -translate-y-1/2 w-4 h-4
            ${colorClasses[color]} rounded-full shadow-md
            border-2 border-white pointer-events-none
            transition-all
          `}
          style={{
            left: `calc(${((value - min) / (max - min)) * 100}% - 8px)`,
          }}
        />
      </div>

      {/* Min/Max labels */}
      <div className="flex justify-between mt-1 text-xs text-gray-500">
        <span>{min}{unit}</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );
}

export default PolicySlider;
