import React, { useState } from 'react';
import { getAlerts } from '../services/mockData';
import PageContainer from '../components/Layout/PageContainer';
import EmptyState from '../components/common/EmptyState';
import './AlertsPage.css';

export default function AlertsPage() {
  const [alerts] = useState(() => getAlerts());

  return (
    <PageContainer>
      <div className="alerts-page-container fade-in">
        <div className="alerts-header">
          <h1>Alerts</h1>
          <p className="subtitle">Important updates about your watched products.</p>
        </div>

        {alerts.length > 0 ? (
          <div className="alerts-list">
            {alerts.map(alert => (
              <div key={alert.id} className={`alert-card ${alert.read ? 'read' : 'unread'}`}>
                <div className="alert-card-header">
                  <h3 className="alert-title">{alert.title}</h3>
                  <span className="alert-time">
                    {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="alert-message">{alert.message}</p>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState 
            emoji="🔕"
            title="No alerts yet" 
            description="When prices drop or sellers change, you'll see it here." 
          />
        )}
      </div>
    </PageContainer>
  );
}
