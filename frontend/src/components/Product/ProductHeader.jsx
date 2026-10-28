import React from 'react';
import { formatPrice, formatTimeAgo } from '../../utils/formatPrice';
import './ProductHeader.css';

const ProductHeader = ({ product }) => {
  if (!product) return null;

  return (
    <div className="product-header">
      <img src={product.image || 'https://via.placeholder.com/120'} alt={product.name} className="product-image" />
      <div className="product-header-details">
        <h1 className="product-name">{product.name}</h1>
        <div className="product-meta">
          {product.brand && <span>{product.brand}</span>}
          {product.brand && product.category && <span> · </span>}
          {product.category && <span>{product.category}</span>}
          {product.category && product.variant && <span> · </span>}
          {product.variant && <span>{product.variant}</span>}
        </div>
        <div className="product-price-row">
          <span className="product-price">{formatPrice(product.currentPrice)}</span>
          <span className="product-timestamp">{formatTimeAgo(product.lastChecked)}</span>
          {product.dataStatus === 'STALE' && <span className="product-timestamp">Last verified price</span>}
          {product.dataStatus === 'CACHED' && <span className="product-timestamp">Verified cache</span>}
          {product.dataStatus === 'SAMPLE' && <span className="product-timestamp">Sample data</span>}
        </div>
      </div>
    </div>
  );
};

export default ProductHeader;
