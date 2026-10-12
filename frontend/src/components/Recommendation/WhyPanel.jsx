import React, { useState } from 'react';
import './WhyPanel.css';

const WhyPanel = ({ reasons, recommendationLabel }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!reasons || reasons.length === 0) return null;

  return (
    <div className="why-panel">
      <button 
        id="why-panel-toggle"
        className="why-toggle" 
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls="why-panel-content"
        aria-label={isOpen ? `Collapse explanation for ${recommendationLabel || 'recommendation'}` : `Why I said this - expand explanation for ${recommendationLabel || 'recommendation'}`}
      >
        Why I said this <span aria-hidden="true">{isOpen ? '↑' : '↓'}</span>
      </button>
      
      {isOpen && (
        <div 
          id="why-panel-content" 
          className="why-content slide-up"
          role="region"
          aria-labelledby="why-panel-toggle"
        >
          <ul className="why-list">
            {reasons.map((reason, idx) => (
              <li key={idx} className="why-item">
                <span className="why-icon" aria-hidden="true">✓</span>
                <span className="why-text">{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default WhyPanel;
