import React from 'react';
import './ThinkingScreen.css';

const ThinkingScreen = ({ productName, steps, currentStep, complete }) => {
  return (
    <div className="thinking-screen fade-in">
      <h2 className="thinking-title">
        {complete ? "I've got it." : `Checking ${productName}...`}
      </h2>
      
      <div className="thinking-steps">
        {steps.map((step, idx) => {
          const isComplete = complete || idx < currentStep;
          const isActive = !complete && idx === currentStep;
          const isPending = !complete && idx > currentStep;
          
          return (
            <div key={idx} className={`thinking-step ${isComplete ? 'step-complete' : ''} ${isActive ? 'step-active' : ''} ${isPending ? 'step-pending' : ''}`}>
              <div className="step-icon">
                {isComplete && <span className="icon-check">✓</span>}
                {isActive && <span className="icon-pulse"></span>}
              </div>
              <span className="step-text">{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ThinkingScreen;
