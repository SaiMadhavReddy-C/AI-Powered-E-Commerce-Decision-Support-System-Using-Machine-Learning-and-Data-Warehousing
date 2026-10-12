import React from 'react';

const PageContainer = ({ children }) => {
  return (
    <div className="page-wrapper fade-in">
      <main className="container page-container-main">
        {children}
      </main>
    </div>
  );
};

export default PageContainer;
