import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export function RoomsManager() {
  const [rooms, setRooms] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingRoom, setEditingRoom] = useState(null);
  const [formData, setFormData] = useState({
    room_number: '',
    floor: '',
    camera_url: '',
    camera_enabled: true,
    privacy_enabled: true
  });

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/rooms`);
      setRooms(response.data);
    } catch (error) {
      console.error('Error fetching rooms:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const payload = {
        ...formData,
        floor: formData.floor ? parseInt(formData.floor) : null
      };

      if (editingRoom) {
        await axios.put(`${API_BASE}/api/rooms/${editingRoom.id}`, payload);
      } else {
        await axios.post(`${API_BASE}/api/rooms`, payload);
      }
      
      fetchRooms();
      resetForm();
    } catch (error) {
      console.error('Error saving room:', error);
      alert('Failed to save room: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleEdit = (room) => {
    setEditingRoom(room);
    setFormData({
      room_number: room.room_number,
      floor: room.floor || '',
      camera_url: room.camera_url,
      camera_enabled: room.camera_enabled,
      privacy_enabled: room.privacy_enabled
    });
    setShowForm(true);
  };

  const handleDelete = async (roomId) => {
    if (!confirm('Are you sure you want to delete this room?')) return;
    
    try {
      await axios.delete(`${API_BASE}/api/rooms/${roomId}`);
      fetchRooms();
    } catch (error) {
      console.error('Error deleting room:', error);
      alert('Failed to delete room');
    }
  };

  const resetForm = () => {
    setFormData({
      room_number: '',
      floor: '',
      camera_url: '',
      camera_enabled: true,
      privacy_enabled: true
    });
    setEditingRoom(null);
    setShowForm(false);
  };

  const handleMobileRoom = () => {
    setFormData({
      ...formData,
      camera_url: 'mobile'
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Rooms Management</h2>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Add Room
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">
            {editingRoom ? 'Edit Room' : 'Add New Room'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Room Number *</label>
                <input
                  type="text"
                  required
                  value={formData.room_number}
                  onChange={(e) => setFormData({...formData, room_number: e.target.value})}
                  className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 101, A1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Floor</label>
                <input
                  type="number"
                  value={formData.floor}
                  onChange={(e) => setFormData({...formData, floor: e.target.value})}
                  className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 1, 2"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Camera URL *</label>
              <input
                type="text"
                required
                value={formData.camera_url}
                onChange={(e) => setFormData({...formData, camera_url: e.target.value})}
                className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., rtsp://192.168.1.100:554/stream or 0 for webcam"
              />
              <div className="mt-2 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setFormData({...formData, camera_url: '0'})}
                  className="text-xs px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                >
                  📷 Use Webcam (0)
                </button>
                <button
                  type="button"
                  onClick={handleMobileRoom}
                  className="text-xs px-3 py-1 bg-green-200 rounded hover:bg-green-300"
                >
                  📱 Use Mobile Camera
                </button>
                <button
                  type="button"
                  onClick={() => setFormData({...formData, camera_url: 'screen'})}
                  className="text-xs px-3 py-1 bg-blue-200 rounded hover:bg-blue-300"
                >
                  🖥️ Screen Capture
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.camera_enabled}
                  onChange={(e) => setFormData({...formData, camera_enabled: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm">Camera Enabled</span>
              </label>
              
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.privacy_enabled}
                  onChange={(e) => setFormData({...formData, privacy_enabled: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm">Privacy Filter (Face Blur)</span>
              </label>
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                {editingRoom ? 'Update' : 'Create'} Room
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Room</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Floor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Camera</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Privacy</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rooms.map((room) => (
              <tr key={room.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">{room.room_number}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {room.floor || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {room.camera_url === 'mobile' ? (
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Mobile</span>
                    ) : room.camera_url === '0' ? (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Webcam</span>
                    ) : (
                      <span className="text-xs text-gray-600 font-mono">{room.camera_url.substring(0, 30)}...</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded text-xs ${
                    room.camera_enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {room.camera_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded text-xs ${
                    room.privacy_enabled ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {room.privacy_enabled ? 'On' : 'Off'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(room)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(room.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {rooms.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No rooms configured yet. Click "Add Room" to get started.
          </div>
        )}
      </div>
    </div>
  );
}

export default RoomsManager;
