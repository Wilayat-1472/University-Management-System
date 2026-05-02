import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Users, UserCircle, LogOut } from 'lucide-react';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside style={{
      width: '260px',
      height: '100vh',
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--glass-border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0'
    }}>
      <div style={{ padding: '0 24px', marginBottom: '40px' }}>
        <h2 style={{ 
          background: 'linear-gradient(to right, var(--primary), var(--accent))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontSize: '1.5rem',
          fontWeight: '700'
        }}>UMS Portal</h2>
      </div>

      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px', padding: '0 16px' }}>
        <NavLink 
          to="/" 
          style={({ isActive }) => ({
            display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
            background: isActive ? 'var(--glass-bg)' : 'transparent',
            textDecoration: 'none',
            fontWeight: isActive ? '600' : '500',
            borderLeft: isActive ? '3px solid var(--primary)' : '3px solid transparent'
          })}
        >
          <LayoutDashboard size={20} /> Dashboard
        </NavLink>

        {user?.role?.name === 'Admin' && (
          <NavLink 
            to="/users" 
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
              background: isActive ? 'var(--glass-bg)' : 'transparent',
              textDecoration: 'none',
              fontWeight: isActive ? '600' : '500',
              borderLeft: isActive ? '3px solid var(--primary)' : '3px solid transparent'
            })}
          >
            <Users size={20} /> Manage Users
          </NavLink>
        )}

        <NavLink 
          to="/profile" 
          style={({ isActive }) => ({
            display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
            background: isActive ? 'var(--glass-bg)' : 'transparent',
            textDecoration: 'none',
            fontWeight: isActive ? '600' : '500',
            borderLeft: isActive ? '3px solid var(--primary)' : '3px solid transparent'
          })}
        >
          <UserCircle size={20} /> My Profile
        </NavLink>
      </nav>

      <div style={{ padding: '0 16px', marginTop: 'auto' }}>
        <button 
          onClick={handleLogout}
          className="btn btn-outline"
          style={{ width: '100%', color: 'var(--danger)', borderColor: 'rgba(220, 53, 69, 0.3)' }}
        >
          <LogOut size={18} /> Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
