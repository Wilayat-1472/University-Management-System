import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Users, BookOpen, Clock, Calendar } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Dashboard</h1>
        <p style={{ color: 'var(--text-muted)' }}>Welcome back, {user?.username} ({user?.role?.name})</p>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '24px' }}>
        {/* Quick Stats Cards based on Role */}
        {user?.role?.name === 'Admin' && (
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ background: 'rgba(88, 101, 242, 0.2)', padding: '16px', borderRadius: '50%', color: 'var(--primary)' }}>
              <Users size={28} />
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Total Users</p>
              <h2 style={{ fontSize: '1.8rem', marginTop: '4px' }}>Manage</h2>
            </div>
          </div>
        )}
        
        {(user?.role?.name === 'Student' || user?.role?.name === 'Faculty') && (
          <>
            <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ background: 'rgba(162, 85, 226, 0.2)', padding: '16px', borderRadius: '50%', color: 'var(--secondary)' }}>
                <BookOpen size={28} />
              </div>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>My Courses</p>
                <h2 style={{ fontSize: '1.8rem', marginTop: '4px' }}>View</h2>
              </div>
            </div>
            
            <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ background: 'rgba(18, 184, 134, 0.2)', padding: '16px', borderRadius: '50%', color: 'var(--accent)' }}>
                <Clock size={28} />
              </div>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Attendance</p>
                <h2 style={{ fontSize: '1.8rem', marginTop: '4px' }}>Verify</h2>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
