// Sidebar.jsx
export function Sidebar() {
  return (
    <aside className="w-64 bg-white shadow-md">
      <div className="p-6">
        <h2 className="text-xl font-bold text-gray-800">GuardianAI</h2>
        <p className="text-xs text-gray-500 mt-1">Patient Monitoring</p>
      </div>
      <nav className="mt-6">
        <a href="/" className="flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100">
          <span>📊 Dashboard</span>
        </a>
        <a href="/alerts" className="flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100">
          <span>🚨 Alerts</span>
        </a>
        <a href="/contacts" className="flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100">
          <span>👥 Contacts</span>
        </a>
        <div className="border-t border-gray-200 my-2"></div>
        <a href="/screen-capture" className="flex items-center px-6 py-3 text-blue-700 hover:bg-blue-50">
          <span>🖥️ Screen Monitoring</span>
        </a>
      </nav>
    </aside>
  );
}

// Dashboard.jsx
export function Dashboard({ alerts }) {
  const activeAlerts = alerts.filter(a => a.status === 'active');
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20 text-gray-100">
          <h3 className="text-lg font-semibold mb-2 text-gray-100">Total Alerts</h3>
          <p className="text-3xl font-bold">{alerts.length}</p>
        </div>
        <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20 text-gray-100">
          <h3 className="text-lg font-semibold mb-2 text-gray-100">Active Alerts</h3>
          <p className="text-3xl font-bold text-red-300">{activeAlerts.length}</p>
        </div>
        <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20 text-gray-100">
          <h3 className="text-lg font-semibold mb-2 text-gray-100">System Status</h3>
          <p className="text-3xl font-bold text-emerald-300">Online</p>
        </div>
      </div>
      
      <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20">
        <h2 className="text-xl font-bold mb-4 text-gray-100">Recent Alerts</h2>
        <div className="space-y-2">
          {alerts.slice(0, 5).map(alert => (
            <div key={alert.id} className="flex justify-between items-center p-3 rounded bg-white/5 border border-white/10">
              <div>
                <p className="font-medium text-gray-100">{alert.description}</p>
                <p className="text-sm text-gray-300">Room: {alert.room_id}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm ${
                alert.status === 'active' ? 'bg-red-500/20 text-red-200' : 'bg-emerald-500/20 text-emerald-200'
              }`}>
                {alert.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// AlertsPanel.jsx
export function AlertsPanel({ alerts, onAlertsUpdate }) {
  const acknowledgeAlert = async (alert) => {
    // Use _id field from API (backend returns _id, not id)
    const alertId = alert._id || alert.id;
    if (!alertId) {
      console.error('No alert ID found', alert);
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/api/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ acknowledged_by: 'Nurse Admin' })
      });
      if (response.ok) {
        onAlertsUpdate();
        alert('Alert acknowledged successfully!');
      } else {
        const error = await response.text();
        alert(`Failed to acknowledge: ${error}`);
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error);
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20 text-gray-100">
      <h2 className="text-2xl font-bold mb-6 text-gray-100">Alert Management</h2>
      <div className="space-y-4">
        {alerts.map(alert => (
          <div key={alert.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    alert.alert_type === 'gesture' ? 'bg-blue-100 text-blue-800' :
                    alert.alert_type === 'fall' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {alert.alert_type}
                  </span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    alert.status === 'active' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {alert.status}
                  </span>
                </div>
                <h3 className="font-semibold text-lg mb-1 text-gray-100">{alert.description}</h3>
                <p className="text-gray-300">Room: {alert.room_id}</p>
                <p className="text-sm text-gray-400">
                  {new Date(alert.timestamp).toLocaleString()}
                </p>
              </div>
              {alert.status === 'active' && (
                <button
                  onClick={() => acknowledgeAlert(alert)}
                  className="bg-emerald-500/90 text-white px-4 py-2 rounded hover:bg-emerald-500"
                >
                  Acknowledge
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// VideoGrid.jsx
export function VideoGrid() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-100">Video Feeds</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[1, 2, 3, 4].map(room => (
          <div key={room} className="rounded-xl p-4 bg-white/10 backdrop-blur border border-white/20">
            <h3 className="font-semibold mb-2 text-gray-100">Room {room}</h3>
            <div className="bg-white/5 border border-white/10 aspect-video rounded flex items-center justify-center">
              <p className="text-gray-300">Camera feed would appear here</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ContactsManager.jsx
export function ContactsManager() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6">Contacts Management</h2>
      <div className="space-y-4">
        <p className="text-gray-600">Manage nurse and doctor contacts here.</p>
      </div>
    </div>
  );
}

export default { Sidebar, Dashboard, AlertsPanel, VideoGrid, ContactsManager };
