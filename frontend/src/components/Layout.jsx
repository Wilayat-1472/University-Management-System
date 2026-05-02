import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export const Layout = () => {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <header style={{
          height: '70px',
          borderBottom: '1px solid var(--glass-border)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 32px',
          background: 'var(--glass-bg)',
          backdropFilter: 'blur(10px)'
        }}>
          {/* Header content like search bar or notifications could go here */}
        </header>
        <div className="page-container">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
