import React from 'react';
import { formatPrice } from '../../utils/formatPrice';
import './RetailerComparison.css';

const RetailerComparison = ({ competitors }) => {
  if (!competitors || competitors.length === 0) return null;

  // Find lowest price
  const lowestPrice = Math.min(...competitors.map(c => c.price));

  return (
    <div className="retailer-comparison">
      <h3 className="retailer-comparison-title">Compare stores</h3>
      <div className="retailer-table-container">
        <table className="retailer-table">
          <thead>
            <tr>
              <th>Store</th>
              <th>Price</th>
              <th>Seller & Reliability</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {competitors.map((comp, idx) => (
              <tr key={idx} className={comp.price === lowestPrice ? 'best-price-row' : ''}>
                <td>
                  <div className="retailer-name-cell">
                    <span className="retailer-dot"></span>
                    {comp.retailer}
                  </div>
                </td>
                <td className="price-cell">
                  {formatPrice(comp.price)}
                </td>
                <td>
                  <div className="seller-cell">
                    <span className="seller-name">{comp.seller?.name || comp.seller}</span>
                    <span className={`reliability-badge ${comp.seller?.reliability === 'RELIABLE' ? 'rel-good' : 'rel-warn'}`}>
                      {comp.seller?.reliability === 'RELIABLE' ? 'Looks reliable' : 'Check seller'}
                    </span>
                  </div>
                </td>
                <td className="action-cell">
                  <a href={comp.url} target="_blank" rel="noopener noreferrer" className="view-link">
                    View →
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RetailerComparison;
