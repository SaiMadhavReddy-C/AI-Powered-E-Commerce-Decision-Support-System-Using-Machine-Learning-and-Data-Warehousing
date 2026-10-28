import React from 'react';

const PageContainer = ({ children }) => {
  return (
    <div className="page-wrapper fade-in">
      <div className="container page-container-main">
        {children}
      </div>
    </div>
  );
};

export default PageContainer;
