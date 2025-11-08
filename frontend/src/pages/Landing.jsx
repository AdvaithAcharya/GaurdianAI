import React from 'react';
import DarkVeil from './DarkVeil';

export default function Landing({ alerts }) {
  const active = alerts.filter(a => a.status === 'active').length;

  const enter = (path) => {
    try { sessionStorage.setItem('visitedLanding', '1'); } catch {}
    window.location.href = path;
  };

  return (
    <div className="space-y-8">
      <div style={{ width: '100%', height: '600px', position: 'relative' }} className="rounded-2xl overflow-hidden border border-white/20">
        <DarkVeil />
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
          <h2 className="text-5xl md:text-6xl font-extrabold tracking-tight text-gray-100">GuardianAI</h2>
          <p className="max-w-2xl text-gray-300 mx-auto mt-4">
            Privacy-first, multi-modal AI monitoring for patient safety. Real-time gesture, fall and distress detection with immediate escalation.
          </p>
          <div className="flex flex-wrap gap-4 justify-center mt-8">
            <button onClick={()=>enter('/dashboard')} className="px-6 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition">Enter Dashboard</button>
            <button onClick={()=>enter('/alerts')} className="px-6 py-3 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 transition">Manage Alerts</button>
            <button onClick={()=>enter('/analytics')} className="px-6 py-3 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 transition">View Analytics</button>
          </div>
        </div>
      </div>
      <div className="text-sm text-gray-300 text-center">Active alerts now: <span className="font-semibold text-gray-100">{active}</span></div>
    </div>
  );
}
