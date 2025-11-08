import React, { useMemo } from 'react';

function groupBy(arr, key) {
  return arr.reduce((acc, cur) => {
    const k = cur[key] || 'unknown';
    acc[k] = (acc[k] || 0) + 1;
    return acc;
  }, {});
}

export default function Analytics({ alerts }) {
  const stats = useMemo(() => {
    const total = alerts.length;
    const byStatus = groupBy(alerts, 'status');
    const byType = groupBy(alerts, 'alert_type');
    // per-day counts (local date string)
    const byDay = alerts.reduce((acc, a) => {
      const d = a.timestamp ? new Date(a.timestamp) : null;
      const k = d ? d.toLocaleDateString() : 'unknown';
      acc[k] = (acc[k] || 0) + 1;
      return acc;
    }, {});
    return { total, byStatus, byType, byDay };
  }, [alerts]);

  const Pill = ({ label, value, color }) => (
    <div className={`px-4 py-3 rounded-lg bg-white/10 backdrop-blur border border-white/20 ${color || ''}`}>
      <div className="text-sm text-gray-300">{label}</div>
      <div className="text-2xl font-bold text-gray-100">{value}</div>
    </div>
  );

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-100">Analytics</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Pill label="Total Alerts" value={stats.total} />
        <Pill label="Active" value={stats.byStatus['active'] || 0} color="bg-red-500/10 border-red-400/30" />
        <Pill label="Acknowledged" value={stats.byStatus['acknowledged'] || 0} color="bg-yellow-500/10 border-yellow-400/30" />
        <Pill label="Resolved" value={stats.byStatus['resolved'] || 0} color="bg-green-500/10 border-green-400/30" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20 text-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-100">Alerts by Type</h3>
          <div className="space-y-2">
            {Object.entries(stats.byType).map(([t, n]) => (
              <div key={t} className="flex items-center justify-between py-2 border-b border-white/10 last:border-0">
                <span className="capitalize">{t}</span>
                <span className="font-semibold">{n}</span>
              </div>
            ))}
            {Object.keys(stats.byType).length === 0 && <div className="text-gray-300">No data</div>}
          </div>
        </div>

        <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20 text-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-100">Alerts per Day</h3>
          <div className="space-y-2">
            {Object.entries(stats.byDay).map(([d, n]) => (
              <div key={d} className="flex items-center justify-between py-2 border-b border-white/10 last:border-0">
                <span>{d}</span>
                <span className="font-semibold">{n}</span>
              </div>
            ))}
            {Object.keys(stats.byDay).length === 0 && <div className="text-gray-300">No data</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
