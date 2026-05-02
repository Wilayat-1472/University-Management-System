import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { UserPlus, Trash2, Edit } from 'lucide-react';

const UserManagement = () => {
  const [users, setUsers] = array([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>User Management</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage system access and roles</p>
        </div>
        <button className="btn btn-primary">
          <UserPlus size={18} /> Add User
        </button>
      </div>

      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: 'rgba(255, 255, 255, 0.05)', borderBottom: '1px solid var(--glass-border)' }}>
              <th style={{ padding: '16px 24px', fontWeight: '500', color: 'var(--text-muted)' }}>User</th>
              <th style={{ padding: '16px 24px', fontWeight: '500', color: 'var(--text-muted)' }}>Role</th>
              <th style={{ padding: '16px 24px', fontWeight: '500', color: 'var(--text-muted)' }}>Status</th>
              <th style={{ padding: '16px 24px', fontWeight: '500', color: 'var(--text-muted)', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="4" style={{ padding: '24px', textAlign: 'center' }}>Loading...</td>
              </tr>
            ) : (
              users.map(user => (
                <tr key={user.id} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                  <td style={{ padding: '16px 24px' }}>
                    <div style={{ fontWeight: '500' }}>{user.username}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{user.email}</div>
                  </td>
                  <td style={{ padding: '16px 24px' }}>
                    <span style={{ 
                      padding: '4px 12px', 
                      borderRadius: '24px', 
                      fontSize: '0.85rem',
                      background: user.role.name === 'Admin' ? 'rgba(88, 101, 242, 0.15)' : 'rgba(255,255,255,0.1)',
                      color: user.role.name === 'Admin' ? 'var(--primary)' : 'var(--text-primary)'
                    }}>
                      {user.role.name}
                    </span>
                  </td>
                  <td style={{ padding: '16px 24px' }}>
                    <span style={{ 
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      color: user.is_active ? 'var(--success)' : 'var(--danger)',
                      fontSize: '0.9rem'
                    }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'currentColor' }}></span>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                    <button className="btn btn-outline" style={{ padding: '6px', marginRight: '8px', border: 'none' }}>
                      <Edit size={16} />
                    </button>
                    <button className="btn btn-outline" style={{ padding: '6px', border: 'none', color: 'var(--danger)' }}>
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserManagement;
