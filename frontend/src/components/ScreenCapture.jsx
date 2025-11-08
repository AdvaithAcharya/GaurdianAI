import { useState, useRef } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// Default monitoring session
const MONITORING_SESSION_ID = 'screen-monitor-session';

export function ScreenCapture() {
  const [capturing, setCapturing] = useState(false);
  const [fps, setFps] = useState(10);
  const [stats, setStats] = useState({ framesSent: 0, alertsDetected: 0 });
  const [captureMode, setCaptureMode] = useState('window'); // 'screen' or 'window'
  const [monitorName, setMonitorName] = useState('CCTV Monitor');
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamIntervalRef = useRef(null);
  const mediaStreamRef = useRef(null);

  const startCapture = async () => {

    try {
      // Request screen/window capture
      const displayMediaOptions = {
        video: {
          cursor: 'never',
          displaySurface: captureMode === 'window' ? 'window' : 'monitor',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      mediaStreamRef.current = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions);
      videoRef.current.srcObject = mediaStreamRef.current;

      await new Promise(resolve => {
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          resolve();
        };
      });

      setCapturing(true);
      setStats({ framesSent: 0, alertsDetected: 0 });

      // Start sending frames
      const interval = 1000 / fps;
      streamIntervalRef.current = setInterval(() => {
        captureAndSendFrame();
      }, interval);

      // Handle user stopping the share
      mediaStreamRef.current.getVideoTracks()[0].addEventListener('ended', () => {
        stopCapture();
      });

    } catch (error) {
      console.error('Error starting screen capture:', error);
      if (error.name === 'NotAllowedError') {
        alert('Screen capture permission denied. Please allow screen sharing.');
      } else {
        alert('Failed to start screen capture: ' + error.message);
      }
    }
  };

  const stopCapture = () => {
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCapturing(false);
  };

  const captureAndSendFrame = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const frameData = canvas.toDataURL('image/jpeg', 0.8);

    try {
      const response = await axios.post(
        `${API_BASE}/api/streams/mobile/${MONITORING_SESSION_ID}/frame`,
        { frame: frameData },
        { timeout: 5000 }
      );

      setStats(prev => ({
        framesSent: prev.framesSent + 1,
        alertsDetected: prev.alertsDetected + (response.data.alerts_detected || 0)
      }));
    } catch (error) {
      // Silently continue on errors to not interrupt monitoring
      if (stats.framesSent % 100 === 0) {
        console.error('Error sending frame:', error);
      }
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2 text-gray-100">🖥️ CCTV Monitor Overlay</h2>
        <p className="text-gray-300">
          Capture your CCTV monitoring software screen to enable AI detection on existing camera feeds
        </p>
      </div>

      <div className="rounded-xl p-4 bg-white/5 backdrop-blur border border-white/10 text-gray-300">
        <h4 className="font-semibold text-gray-100 mb-2">📌 How it works:</h4>
        <ul className="text-sm space-y-1">
          <li>1. Open your CCTV monitoring app (shows all camera views)</li>
          <li>2. Click "Start Screen Capture" below</li>
          <li>3. Select the CCTV app window when prompted</li>
          <li>4. AI will monitor all visible cameras automatically!</li>
        </ul>
      </div>

      <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20 text-gray-100">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Monitor Name (optional)</label>
            <input
              type="text"
              value={monitorName}
              onChange={(e) => setMonitorName(e.target.value)}
              disabled={capturing}
              className="w-full px-3 py-2 rounded bg-white/5 border border-white/20 text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none disabled:opacity-50"
              placeholder="e.g., ICU Cameras, Ward Monitors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Capture Mode</label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="screen"
                      checked={captureMode === 'screen'}
                      onChange={(e) => setCaptureMode(e.target.value)}
                      disabled={capturing}
                      className="mr-2"
                    />
                    <span>Entire Screen</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="window"
                      checked={captureMode === 'window'}
                      onChange={(e) => setCaptureMode(e.target.value)}
                      disabled={capturing}
                      className="mr-2"
                    />
                    <span>Specific Window/Tab</span>
                  </label>
                </div>
                <p className="text-xs text-gray-300 mt-1">
                  {captureMode === 'screen' 
                    ? 'Monitor your entire screen - good for multiple CCTV views'
                    : 'Monitor a specific window - good for single CCTV app'
                  }
                </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
                  Frame Rate: {fps} FPS
                </label>
                <input
                  type="range"
                  min="5"
                  max="30"
                  value={fps}
                  onChange={(e) => setFps(parseInt(e.target.value))}
                  disabled={capturing}
                  className="w-full disabled:opacity-50 accent-emerald-500"
                />
                <p className="text-xs text-gray-300 mt-1">
                  Higher FPS = Better detection but more CPU usage
                </p>
          </div>

          <div className="flex space-x-3">
                {!capturing ? (
                  <button
                    onClick={startCapture}
                    className="px-6 py-3 bg-emerald-500/90 text-white rounded-lg hover:bg-emerald-500 font-medium"
                  >
                    🎥 Start Screen Capture
                  </button>
                ) : (
                  <button
                    onClick={stopCapture}
                    className="px-6 py-3 bg-red-500/90 text-white rounded-lg hover:bg-red-500 font-medium"
                  >
                    ⬛ Stop Capture
                  </button>
                )}
          </div>
        </div>
      </div>

      <div className="rounded-xl overflow-hidden bg-white/10 backdrop-blur border border-white/20 text-gray-100">
            <div className="bg-black/40 text-gray-100 px-4 py-2 flex justify-between items-center border-b border-white/10">
              <h3 className="font-semibold">Preview</h3>
              {capturing && (
                <span className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                  <span className="text-sm">CAPTURING</span>
                </span>
              )}
            </div>
            <div className="relative bg-black/40" style={{ aspectRatio: '16/9' }}>
              <video
                ref={videoRef}
                className="w-full h-full object-contain"
                autoPlay
                playsInline
                muted
              />
              {!capturing && (
                <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <svg className="w-16 h-16 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <p>No capture active</p>
                    <p className="text-sm mt-1">Click "Start Screen Capture" above</p>
                  </div>
                </div>
              )}
        </div>
      </div>

      {capturing && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm text-blue-600 mb-1">Frames Analyzed</div>
                  <div className="text-2xl font-bold text-blue-900">{stats.framesSent}</div>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <div className="text-sm text-red-600 mb-1">Alerts Detected</div>
                  <div className="text-2xl font-bold text-red-900">{stats.alertsDetected}</div>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2">💡 Tips</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Open your CCTV app/video player in another window</li>
                  <li>• The AI will analyze the captured video feed</li>
                  <li>• Gestures and falls will trigger alerts automatically</li>
                  <li>• Check the Alerts page to see detected events</li>
                </ul>
          </div>
        </>
      )}

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}

export default ScreenCapture;
