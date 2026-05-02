import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Save } from 'lucide-react';

const Profile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    address: '',
    student_id: '',
    department: ''
  });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/profile/me');
        if (response.data) {
          setProfile({
            first_name: response.data.first_name || '',
            last_name: response.data.last_name || '',
            phone: response.data.phone || '',
            address: response.data.address || '',
            student_id: response.data.student_id || '',
            department: response.data.department || ''
          });
        }
      } catch (error) {
        console.error('Error fetching profile', error);
      }
    };
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage('');
    
    try {
      await api.put('/profile/me', profile);
      setMessage('Profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error updating profile');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '800px' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>My Profile</h1>
        <p style={{ color: 'var(--text-muted)' }}>Manage your personal information</p>
      </div>

      <div className="glass-panel" style={{ padding: '32px' }}>
        {message && (
          <div style={{ 
            padding: '12px', 
            borderRadius: 'var(--radius-sm)', 
            marginBottom: '24px',
            background: message.includes('Error') ? 'rgba(220, 53, 69, 0.1)' : 'rgba(18, 184, 134, 0.1)',
            color: message.includes('Error') ? 'var(--danger)' : 'var(--success)'
          }}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="input-group">
              <label>First Name</label>
              <input type="text" name="first_name" value={profile.first_name} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>Last Name</label>
              <input type="text" name="last_name" value={profile.last_name} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>Phone Number</label>
              <input type="text" name="phone" value={profile.phone} onChange={handleChange} />
            </div>
            
            {user?.role?.name === 'Student' && (
              <div className="input-group">
                <label>Student ID</label>
                <input type="text" name="student_id" value={profile.student_id} onChange={handleChange} />
              </div>
            )}
            
            <div className="input-group" style={{ gridColumn: '1 / -1' }}>
              <label>Department</label>
              <input type="text" name="department" value={profile.department} onChange={handleChange} />
            </div>
            
            <div className="input-group" style={{ gridColumn: '1 / -1' }}>
              <label>Address</label>
              <input type="text" name="address" value={profile.address} onChange={handleChange} />
            </div>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <button type="submit" className="btn btn-primary" disabled={isSaving}>
              <Save size={18} /> {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Profile;
