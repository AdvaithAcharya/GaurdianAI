import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export function MobileCamera() {
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [fps, setFps] = useState(10);
  const [stats, setStats] = useState({ framesSent: 0, alertsDetected: 0 });
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamIntervalRef = useRef(null);
  const mediaStreamRef = useRef(null);

  useEffect(() => {
    fetchMobileRooms();
    return () => {
      stopStreaming();
    };
  }, []);

  const fetchMobileRooms = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/rooms`);
      const mobileRooms = response.data.filter(r => r.camera_url === 'mobile');
      setRooms(mobileRooms);
      if (mobileRooms.length > 0) {
        setSelectedRoom(mobileRooms[0].id);
      }
    } catch (error) {
      console.error('Error fetching rooms:', error);
    }
  };

  const startStreaming = async () => {
    if (!selectedRoom) {
      alert('Please select a room first');
      return;
    }

    try {
      // Request camera access
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'user',
          width: { ideal: 640 },
          height: { ideal: 480 }
        },
        audio: false
      });

      mediaStreamRef.current = stream;
      videoRef.current.srcObject = stream;
      
      // Wait for video to be ready
      await new Promise((resolve) => {
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          resolve();
        };
      });

      setStreaming(true);
      setStats({ framesSent: 0, alertsDetected: 0 });

      // Start sending frames
      const interval = 1000 / fps;
      streamIntervalRef.current = setInterval(() => {
        captureAndSendFrame();
      }, interval);

    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Failed to access camera: ' + error.message);
    }
  };

  const stopStreaming = () => {
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

    setStreaming(false);
  };

  const captureAndSendFrame = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current frame
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    const frameData = canvas.toDataURL('image/jpeg', 0.8);

    try {
      const response = await axios.post(
        `${API_BASE}/api/streams/mobile/${selectedRoom}/frame`,
        { frame: frameData },
        { timeout: 5000 }
      );

      setStats(prev => ({
        framesSent: prev.framesSent + 1,
        alertsDetected: prev.alertsDetected + (response.data.alerts_detected || 0)
      }));
    } catch (error) {
      console.error('Error sending frame:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Mobile Camera Streaming</h2>
        <p className="text-gray-600">
          Use your device's camera to stream video to the monitoring system
        </p>
      </div>

      {rooms.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="font-semibold text-yellow-800 mb-2">No Mobile Rooms Configured</h3>
          <p className="text-yellow-700 mb-4">
            You need to create a room with "mobile" as the camera URL first.
          </p>
          <a 
            href="/rooms" 
            className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 inline-block"
          >
            Go to Rooms Management
          </a>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Select Room</label>
                <select
                  value={selectedRoom}
                  onChange={(e) => setSelectedRoom(e.target.value)}
                  disabled={streaming}
                  className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                >
                  {rooms.map(room => (
                    <option key={room.id} value={room.id}>
                      Room {room.room_number} {room.floor ? `(Floor ${room.floor})` : ''}
                    </option>
                  ))}
                </select>
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
                  disabled={streaming}
                  className="w-full disabled:opacity-50"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Higher FPS = Better detection but more data usage
                </p>
              </div>

              <div className="flex space-x-3">
                {!streaming ? (
                  <button
                    onClick={startStreaming}
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                  >
                    Start Streaming
                  </button>
                ) : (
                  <button
                    onClick={stopStreaming}
                    className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
                  >
                    Stop Streaming
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="bg-gray-800 text-white px-4 py-2 flex justify-between items-center">
              <h3 className="font-semibold">Camera Preview</h3>
              {streaming && (
                <span className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></span>
                  <span className="text-sm">STREAMING</span>
                </span>
              )}
            </div>
            <div className="relative bg-gray-900" style={{ aspectRatio: '4/3' }}>
              <video
                ref={videoRef}
                className="w-full h-full object-contain"
                autoPlay
                playsInline
                muted
              />
              {!streaming && (
                <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <svg className="w-16 h-16 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <p>Camera not active</p>
                    <p className="text-sm mt-1">Click "Start Streaming" above</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {streaming && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-sm text-blue-600 mb-1">Frames Sent</div>
                <div className="text-2xl font-bold text-blue-900">{stats.framesSent}</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <div className="text-sm text-red-600 mb-1">Alerts Detected</div>
                <div className="text-2xl font-bold text-red-900">{stats.alertsDetected}</div>
              </div>
            </div>
          )}

          <canvas ref={canvasRef} className="hidden" />
        </>
      )}
    </div>
  );
}

export default MobileCamera;
