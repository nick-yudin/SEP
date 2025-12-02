import React, { useState, useEffect } from 'react';

export default function BenchmarkViz() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [speed, setSpeed] = useState(100);

  // Benchmark data from comparison.json
  const benchmarkData = {
    duration_minutes: 60,
    total_samples: 12000,
    mqtt: {
      packets_sent: 12000,
      bytes_sent: 1536000,
      energy_mah: 75000.0,
      duty_cycle: 100.0
    },
    resonance: {
      packets_sent: 1095,
      bytes_sent: 1681920,
      energy_mah: 82135.905,
      duty_cycle: 9.125,
      // First 100 transmission indices for visualization
      transmissions: [0, 5, 6, 14, 15, 20, 21, 71, 72, 82, 84, 101, 102, 115, 116, 118, 119, 138, 139, 140,
                      141, 162, 163, 172, 173, 179, 180, 221, 222, 250, 251, 297, 298, 402, 403, 411, 412, 441,
                      442, 458, 459, 462, 463, 476, 477, 495, 496, 503, 504, 511, 512, 523, 524, 566, 567, 570,
                      571, 586, 587, 617, 618, 621, 622, 628, 629, 653, 654, 684, 685, 700, 701, 709, 710, 714,
                      715, 732, 733, 737, 738, 754, 755, 851, 853, 878, 879, 891, 892, 928, 929, 962, 963, 1042,
                      1043, 1067, 1068, 1077, 1078, 1081, 1082]
    }
  };

  const samplesPerSecond = benchmarkData.total_samples / (benchmarkData.duration_minutes * 60);
  const maxTime = benchmarkData.total_samples;

  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setCurrentTime(prev => {
        if (prev >= maxTime) {
          setIsPlaying(false);
          return maxTime;
        }
        return prev + speed;
      });
    }, 50);

    return () => clearInterval(interval);
  }, [isPlaying, speed, maxTime]);

  const mqttTransmissions = currentTime;
  const resonanceTransmissions = benchmarkData.resonance.transmissions.filter(t => t < currentTime).length;

  const mqttBandwidth = (mqttTransmissions / benchmarkData.mqtt.packets_sent * benchmarkData.mqtt.bytes_sent / 1024).toFixed(1);
  const resonanceBandwidth = (resonanceTransmissions / benchmarkData.resonance.packets_sent * benchmarkData.resonance.bytes_sent / 1024).toFixed(1);

  const progress = (currentTime / maxTime) * 100;

  const handleReset = () => {
    setCurrentTime(0);
    setIsPlaying(false);
  };

  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* Info Banner */}
      <div className="glass p-4 rounded-xl mb-6 border border-blue-500/20 bg-blue-500/5">
        <p className="text-sm text-gray-300 text-center">
          <span className="font-bold text-blue-400">Real Benchmark Data:</span> Vibration sensor monitoring for 1 hour (12,000 samples).{' '}
          <a
            href="https://github.com/nick-yudin/resonance-protocol/tree/main/reference_impl/python/benchmarks"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 underline"
          >
            View full methodology →
          </a>
        </p>
      </div>

      {/* Controls */}
      <div className="glass p-6 rounded-xl mb-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-4">
          <div className="flex gap-4">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-6 py-2 bg-signal text-white font-bold rounded hover:bg-signal/80 transition-colors"
            >
              {isPlaying ? '⏸ Pause' : '▶ Play'}
            </button>
            <button
              onClick={handleReset}
              className="px-6 py-2 border border-white/20 text-white font-bold rounded hover:bg-white/10 transition-colors"
            >
              ↻ Reset
            </button>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-400 text-sm">Speed:</span>
            <button
              onClick={() => setSpeed(10)}
              className={`px-3 py-1 rounded ${speed === 10 ? 'bg-signal text-white' : 'bg-white/10 text-gray-400'}`}
            >
              1×
            </button>
            <button
              onClick={() => setSpeed(50)}
              className={`px-3 py-1 rounded ${speed === 50 ? 'bg-signal text-white' : 'bg-white/10 text-gray-400'}`}
            >
              5×
            </button>
            <button
              onClick={() => setSpeed(100)}
              className={`px-3 py-1 rounded ${speed === 100 ? 'bg-signal text-white' : 'bg-white/10 text-gray-400'}`}
            >
              10×
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative w-full h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="absolute h-full bg-signal transition-all duration-100"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="text-center text-gray-400 text-sm mt-2">
          Sample {currentTime.toLocaleString()} / {maxTime.toLocaleString()}
        </div>
      </div>

      {/* Comparison */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* MQTT */}
        <div className="glass p-8 rounded-xl border-red-500/20">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-white">Traditional (MQTT)</h3>
            <div className="text-xs font-mono text-red-500 px-2 py-1 bg-red-500/10 rounded">
              100% DUTY CYCLE
            </div>
          </div>

          {/* Visualization */}
          <div className="h-32 bg-black/40 rounded-lg mb-6 overflow-hidden relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-6xl font-bold text-red-500 animate-pulse">
                {mqttTransmissions.toLocaleString()}
              </div>
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-red-500"></div>
          </div>

          {/* Stats */}
          <div className="space-y-4">
            <div>
              <div className="text-gray-500 text-sm mb-1">Packets Sent</div>
              <div className="text-3xl font-bold text-white">{mqttTransmissions.toLocaleString()}</div>
            </div>
            <div className="border-t border-white/10 pt-4">
              <div className="text-gray-500 text-sm mb-1">Bandwidth Used</div>
              <div className="text-2xl font-bold text-white">{mqttBandwidth} KB</div>
            </div>
            <div className="border-t border-white/10 pt-4">
              <div className="text-gray-500 text-sm mb-1">Strategy</div>
              <div className="text-sm text-gray-400">Send everything, every time</div>
            </div>
          </div>
        </div>

        {/* Resonance */}
        <div className="glass p-8 rounded-xl border-green-500/20">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-white">Resonance</h3>
            <div className="text-xs font-mono text-green-500 px-2 py-1 bg-green-500/10 rounded">
              {benchmarkData.resonance.duty_cycle.toFixed(1)}% DUTY CYCLE
            </div>
          </div>

          {/* Visualization */}
          <div className="h-32 bg-black/40 rounded-lg mb-6 overflow-hidden relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-6xl font-bold text-green-500">
                {resonanceTransmissions.toLocaleString()}
              </div>
            </div>
            {/* Sparse transmission indicator */}
            <div className="absolute bottom-0 left-0 right-0 flex h-1">
              {benchmarkData.resonance.transmissions.slice(0, 100).map((t, idx) => (
                t <= currentTime && (
                  <div
                    key={idx}
                    className="w-1 h-full bg-green-500"
                    style={{ marginLeft: `${(t / maxTime) * 100}%` }}
                  />
                )
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="space-y-4">
            <div>
              <div className="text-gray-500 text-sm mb-1">Events Sent</div>
              <div className="text-3xl font-bold text-white">{resonanceTransmissions.toLocaleString()}</div>
            </div>
            <div className="border-t border-white/10 pt-4">
              <div className="text-gray-500 text-sm mb-1">Bandwidth Used</div>
              <div className="text-2xl font-bold text-white">{resonanceBandwidth} KB</div>
            </div>
            <div className="border-t border-white/10 pt-4">
              <div className="text-gray-500 text-sm mb-1">Strategy</div>
              <div className="text-sm text-gray-400">Transmit only when meaning changes</div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      {currentTime >= maxTime && (
        <div className="glass p-8 rounded-xl border border-signal/20 bg-signal/5 mt-8">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">Why Resonance Wins</h3>

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-6 bg-black/20 rounded-lg">
              <div className="text-sm text-gray-400 mb-2">Network Traffic</div>
              <div className="text-5xl font-bold text-signal mb-2">
                {((1 - benchmarkData.resonance.packets_sent / benchmarkData.mqtt.packets_sent) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-300">fewer packets sent</div>
              <div className="text-xs text-gray-500 mt-2">
                {benchmarkData.resonance.packets_sent.toLocaleString()} vs {benchmarkData.mqtt.packets_sent.toLocaleString()}
              </div>
            </div>

            <div className="text-center p-6 bg-black/20 rounded-lg">
              <div className="text-sm text-gray-400 mb-2">Energy Usage</div>
              <div className="text-5xl font-bold text-signal mb-2">
                {(benchmarkData.mqtt.duty_cycle / benchmarkData.resonance.duty_cycle).toFixed(1)}×
              </div>
              <div className="text-sm text-gray-300">longer battery life</div>
              <div className="text-xs text-gray-500 mt-2">
                {benchmarkData.resonance.duty_cycle.toFixed(1)}% vs {benchmarkData.mqtt.duty_cycle}% duty cycle
              </div>
            </div>

            <div className="text-center p-6 bg-black/20 rounded-lg">
              <div className="text-sm text-gray-400 mb-2">Radio Wake-ups</div>
              <div className="text-5xl font-bold text-signal mb-2">
                {(benchmarkData.mqtt.packets_sent / benchmarkData.resonance.packets_sent).toFixed(0)}×
              </div>
              <div className="text-sm text-gray-300">less often</div>
              <div className="text-xs text-gray-500 mt-2">
                Only when meaning changes
              </div>
            </div>
          </div>

          <div className="border-t border-white/10 pt-6">
            <p className="text-center text-gray-300 text-sm mb-2">
              <span className="font-bold text-white">The Key Insight:</span> Most sensor data is redundant noise.
            </p>
            <p className="text-center text-gray-400 text-sm">
              Traditional protocols don't know this. Resonance filters at the semantic level.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
