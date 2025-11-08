import React from 'react';

export default function DashboardHome() {
  const Card = ({ title, desc, href, emoji }) => (
    <a href={href} className="group bg-white/5 border border-white/10 rounded-xl p-5 hover:bg-white/10 hover:border-white/20 transition">
      <div className="text-2xl mb-3">{emoji}</div>
      <div className="text-lg font-semibold text-white">{title}</div>
      <div className="text-sm text-gray-300 mt-1">{desc}</div>
      <div className="mt-4 text-sm text-blue-300 group-hover:text-blue-200">Open →</div>
    </a>
  );

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-extrabold">Dashboard</h2>
        <p className="text-gray-300">Select a module below to get started.</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card title="Alerts" desc="View and manage active alerts" href="/alerts" emoji="🚨" />
        <Card title="Contacts" desc="Manage nurse/doctor contacts" href="/contacts" emoji="👥" />
        <Card title="Screen Monitoring" desc="Monitor and capture screens" href="/screen-capture" emoji="🖥️" />
        <Card title="Analytics" desc="See alert trends and breakdowns" href="/analytics" emoji="📈" />
        {/* Add more modules as needed */}
      </div>
    </div>
  );
}
