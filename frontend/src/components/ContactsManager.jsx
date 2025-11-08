import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export function ContactsManager() {
  const [contacts, setContacts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [phoneError, setPhoneError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    role: 'nurse',
    phone_number: '',
    email: '',
    firebase_token: '',
    priority: 1,
    active: true
  });

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/contacts`);
      setContacts(response.data);
    } catch (error) {
      console.error('Error fetching contacts:', error);
    }
  };

  const E164 = /^\+[1-9]\d{7,14}$/;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!E164.test(formData.phone_number)) {
      setPhoneError('Phone must be E.164 format, e.g., +15551234567. For Twilio trial, it must be verified.');
      return;
    } else {
      setPhoneError('');
    }
    
    try {
      const payload = {
        ...formData,
        priority: parseInt(formData.priority)
      };

      if (editingContact) {
        await axios.put(`${API_BASE}/api/contacts/${editingContact.id}`, payload);
      } else {
        await axios.post(`${API_BASE}/api/contacts`, payload);
      }
      
      fetchContacts();
      resetForm();
      alert(`Contact ${editingContact ? 'updated' : 'added'} successfully!`);
    } catch (error) {
      console.error('Error saving contact:', error);
      alert('Failed to save contact: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleEdit = (contact) => {
    setEditingContact(contact);
    setFormData({
      name: contact.name,
      role: contact.role,
      phone_number: contact.phone_number,
      email: contact.email || '',
      firebase_token: contact.firebase_token || '',
      priority: contact.priority,
      active: contact.active
    });
    setShowForm(true);
  };

  const handleDelete = async (contactId) => {
    if (!confirm('Are you sure you want to delete this contact?')) return;
    
    try {
      await axios.delete(`${API_BASE}/api/contacts/${contactId}`);
      fetchContacts();
      alert('Contact deleted successfully!');
    } catch (error) {
      console.error('Error deleting contact:', error);
      alert('Failed to delete contact');
    }
  };

  const toggleActive = async (contact) => {
    try {
      await axios.put(`${API_BASE}/api/contacts/${contact.id}`, {
        ...contact,
        active: !contact.active
      });
      fetchContacts();
    } catch (error) {
      console.error('Error toggling contact status:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      role: 'nurse',
      phone_number: '',
      email: '',
      firebase_token: '',
      priority: 1,
      active: true
    });
    setEditingContact(null);
    setShowForm(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">👥 Contact Management</h2>
          <p className="text-gray-300 text-sm">Manage nurses and doctors for alert notifications</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-emerald-500/90 text-white rounded hover:bg-emerald-500"
        >
          ➕ Add Contact
        </button>
      </div>

      {showForm && (
        <div className="rounded-xl p-6 bg-white/10 backdrop-blur border border-white/20 text-gray-100">
          <h3 className="text-xl font-semibold mb-4 text-gray-100">
            {editingContact ? 'Edit Contact' : 'Add New Contact'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2 rounded bg-white/5 border border-white/20 text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  placeholder="e.g., Dr. Jane Smith"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Role *</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  className="w-full px-3 py-2 rounded bg-white/5 border border-white/20 text-gray-100 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                >
                  <option value="nurse">Nurse</option>
                  <option value="doctor">Doctor</option>
                  <option value="emergency">Emergency Contact</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Phone Number *</label>
                <input
                  type="tel"
                  required
                  value={formData.phone_number}
                  onChange={(e) => {
                    setFormData({...formData, phone_number: e.target.value});
                    setPhoneError('');
                  }}
                  className={`w-full px-3 py-2 rounded bg-white/5 border ${phoneError ? 'border-red-500' : 'border-white/20'} text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none`}
                  placeholder="+15551234567"
                />
                <p className={`text-xs mt-1 ${phoneError ? 'text-red-400' : 'text-gray-300'}`}>
                  {phoneError || 'Enter exact E.164 number (e.g., +15551234567). Trial accounts can call only verified numbers.'}
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-3 py-2 rounded bg-white/5 border border-white/20 text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  placeholder="email@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Firebase Token (Optional)</label>
              <input
                type="text"
                value={formData.firebase_token}
                onChange={(e) => setFormData({...formData, firebase_token: e.target.value})}
                className="w-full px-3 py-2 rounded bg-white/5 border border-white/20 text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                placeholder="For push notifications"
              />
              <p className="text-xs text-gray-300 mt-1">Used for mobile app push notifications</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Priority: {formData.priority} {formData.priority === 1 ? '(Highest)' : ''}
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={formData.priority}
                onChange={(e) => setFormData({...formData, priority: e.target.value})}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-300">
                <span>1 - Highest</span>
                <span>5 - Lowest</span>
              </div>
              <p className="text-xs text-gray-300 mt-1">
                Lower priority contacts receive alerts first. Alerts escalate to higher priority if not acknowledged.
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="active"
                checked={formData.active}
                onChange={(e) => setFormData({...formData, active: e.target.checked})}
                className="w-4 h-4"
              />
              <label htmlFor="active" className="text-sm">
                Active (receives alert notifications)
              </label>
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                className="px-4 py-2 bg-emerald-500/90 text-white rounded hover:bg-emerald-500"
              >
                {editingContact ? 'Update' : 'Create'} Contact
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 bg-white/10 text-gray-200 rounded hover:bg-white/20 border border-white/20"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="rounded-xl overflow-hidden bg-white/10 backdrop-blur border border-white/20 text-gray-100">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-white/10">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Phone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Priority</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-transparent divide-y divide-white/10">
              {contacts.map((contact) => (
                <tr key={contact.id} className={!contact.active ? 'bg-white/5' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-100">{contact.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      contact.role === 'doctor' ? 'bg-purple-500/20 text-purple-200' :
                      contact.role === 'nurse' ? 'bg-blue-500/20 text-blue-200' :
                      contact.role === 'emergency' ? 'bg-red-500/20 text-red-200' :
                      'bg-white/10 text-gray-200'
                    }`}>
                      {contact.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-100">
                    {contact.phone_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {contact.email || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs ${
                      contact.priority === 1 ? 'bg-red-500/20 text-red-200' :
                      contact.priority === 2 ? 'bg-orange-500/20 text-orange-200' :
                      'bg-white/10 text-gray-200'
                    }`}>
                      Priority {contact.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => toggleActive(contact)}
                      className={`px-3 py-1 rounded text-xs font-medium ${
                        contact.active 
                          ? 'bg-green-500/20 text-green-100 hover:bg-green-500/30' 
                          : 'bg-white/10 text-gray-200 hover:bg-white/20'
                      }`}
                    >
                      {contact.active ? '✓ Active' : '✗ Inactive'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(contact)}
                      className="text-emerald-300 hover:text-emerald-200 mr-4"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(contact.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {contacts.length === 0 && (
          <div className="text-center py-12">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p className="text-gray-300 mb-4">No contacts configured yet</p>
            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-emerald-500/90 text-white rounded hover:bg-emerald-500"
            >
              Add Your First Contact
            </button>
          </div>
        )}
      </div>

      {contacts.length > 0 && (
        <div className="rounded-xl p-4 bg-white/5 backdrop-blur border border-white/10 text-gray-300">
          <h4 className="font-semibold text-gray-100 mb-2">📞 Alert System</h4>
          <ul className="text-sm space-y-1">
            <li>• <strong>Phone Calls:</strong> Configured in .env with Twilio credentials</li>
            <li>• <strong>Push Notifications:</strong> Configured with Firebase tokens</li>
            <li>• <strong>Escalation:</strong> Alerts start with Priority 1, escalate every 30 seconds</li>
            <li>• <strong>Active Only:</strong> Only contacts marked as "Active" receive notifications</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default ContactsManager;
