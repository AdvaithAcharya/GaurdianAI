import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AlertsPanel } from './components/index';
import ContactsManager from './components/ContactsManager';
import ScreenCapture from './components/ScreenCapture';
import Landing from './pages/Landing';
import DashboardHome from './pages/DashboardHome';
import Analytics from './pages/Analytics';

function InnerApp() {
  const [alerts, setAlerts] = useState([]);
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [toast, setToast] = useState(null); // { title, message }
  const location = useLocation();

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const websocket = new WebSocket('ws://localhost:8000/ws');

      websocket.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setTimeout(connectWebSocket, 3000);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      setWs(websocket);
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (data) => {
    if (data.type && data.type.includes('alert')) {
      // Refresh alerts list
      fetchAlerts();
      // Show toast for new alert
      if (data.type === 'alert_created') {
        const msg = `New ${data.alert_type || 'alert'} for patient ${data.patient_id || ''}`.trim();
        setToast({ title: 'Distress Detected', message: msg });
        // Auto-hide after 5s
        setTimeout(() => setToast(null), 5000);
      }
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/alerts');
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);


  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black text-gray-100">
      {/* Top header hidden on Landing */}
      {location.pathname !== '/' && (
        <header className="sticky top-0 z-10 backdrop-blur bg-white/0 border-b border-white/10">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button onClick={() => window.history.back()} className="px-3 py-1 rounded bg-white/10 border border-white/20 hover:bg-white/20 transition">
                ← Back
              </button>
              <h1 className="text-xl font-bold">GuardianAI</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${isConnected ? 'bg-green-700 text-green-100' : 'bg-red-700 text-red-100'}`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-300' : 'bg-red-300'}`}></div>
                <span className="text-sm font-medium">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              {alerts.filter(a => a.status === 'active').length > 0 && (
                <div className="flex items-center space-x-2 px-3 py-1 bg-red-700 text-red-100 rounded-full">
                  <span className="text-sm font-medium">
                    {alerts.filter(a => a.status === 'active').length} Active Alerts
                  </span>
                </div>
              )}
            </div>
          </div>
        </header>
      )}

      {/* Toast notification */}
      {toast && (
        <div className="fixed right-6 top-6 z-50">
          <div className="bg-white text-gray-900 shadow-lg rounded border-l-4 border-red-500 px-5 py-4 w-80">
            <div className="font-semibold mb-1">{toast.title}</div>
            <div className="text-sm">{toast.message}</div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-6 py-10">
        <Routes>
          {/* Landing page (creative hero) */}
          <Route path="/" element={<Landing alerts={alerts} />} />
          {/* Dashboard hub with feature menu */}
          <Route path="/dashboard" element={<RequireLanding><DashboardHome /></RequireLanding>} />
          {/* Feature pages */}
          <Route path="/alerts" element={<RequireLanding><AlertsPanel alerts={alerts} onAlertsUpdate={fetchAlerts} /></RequireLanding>} />
          <Route path="/contacts" element={<RequireLanding><ContactsManager /></RequireLanding>} />
          <Route path="/screen-capture" element={<RequireLanding><ScreenCapture /></RequireLanding>} />
          <Route path="/analytics" element={<RequireLanding><Analytics alerts={alerts} /></RequireLanding>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

// Require users to visit Landing before accessing app sections (session-based)
function RequireLanding({ children }) {
  const visited = typeof window !== 'undefined' && sessionStorage.getItem('visitedLanding') === '1';
  if (!visited) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <Router>
      <InnerApp />
    </Router>
  );
}
