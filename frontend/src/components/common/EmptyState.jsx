import React from 'react';

const EmptyState = ({ emoji, title, description, actionLabel, onAction }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '64px 20px',
      textAlign: 'center'
    }} className="fade-in">
      <div style={{ fontSize: '48px', marginBottom: '24px' }}>{emoji || '🤔'}</div>
      <h2 style={{ fontSize: '20px', margin: '0 0 12px 0', color: 'var(--text)' }}>{title}</h2>
      <p style={{ fontSize: '15px', color: 'var(--text-secondary)', margin: '0 0 24px 0', maxWidth: '400px' }}>
        {description}
      </p>
      {actionLabel && onAction && (
        <button 
          onClick={onAction}
          style={{
            padding: '12px 24px',
            backgroundColor: 'transparent',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            color: 'var(--text)',
            cursor: 'pointer',
            fontSize: '15px',
            fontWeight: '500'
          }}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
