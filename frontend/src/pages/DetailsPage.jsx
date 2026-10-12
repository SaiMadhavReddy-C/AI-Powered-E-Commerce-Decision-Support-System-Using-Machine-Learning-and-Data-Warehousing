import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchProduct } from '../services/api';
import PageContainer from '../components/Layout/PageContainer';
import ProductHeader from '../components/Product/ProductHeader';
import PriceChart from '../components/Price/PriceChart';
import RetailerComparison from '../components/Price/RetailerComparison';
import SellerInfo from '../components/Recommendation/SellerInfo';
import EmptyState from '../components/common/EmptyState';
import './DetailsPage.css';

export default function DetailsPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [techDetailsOpen, setTechDetailsOpen] = useState(false);

  useEffect(() => {
    fetchProduct(id).then(data => {
      setProduct(data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setProduct(null);
      setLoading(false);
    });
  }, [id]);

  if (loading) {
    return <PageContainer><div className="details-page-container"><p>Loading details...</p></div></PageContainer>;
  }

  if (!product) {
    return (
      <PageContainer>
        <div className="details-page-container">
          <EmptyState emoji="🔍" title="Product not found" description="Could not load details." />
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="details-page-container fade-in">
        <Link to={`/analyze/${id}`} className="back-link">
          &larr; Back to recommendation
        </Link>
        
        <div className="details-header-wrapper">
          <ProductHeader product={product} />
        </div>

        <div className="details-level-section">
          <h2 className="level-heading">Level 1: Consumer Details</h2>
          
          <section className="details-section">
            <h3>Compare stores</h3>
            <RetailerComparison competitors={product.competitors} />
          </section>

          <hr className="divider-light" />

          <section className="details-section">
            <h3>Price history</h3>
            <PriceChart 
              priceHistory={product.priceHistory} 
              buyPoint={product.buyPoint} 
              currentPrice={product.currentPrice} 
            />
          </section>

          <hr className="divider-light" />

          <section className="details-section">
            <h3>Seller information</h3>
            <SellerInfo seller={product.seller} />
          </section>
        </div>

        <hr className="divider" />

        <div className="details-level-section">
          <h2 className="level-heading">Level 2: ShopQ Reasoning</h2>
          <section className="details-section">
            <div className="decision-logic-text">
              <p><strong>Logic:</strong> {product.explanation || "Price looks stable compared to the 90-day average."}</p>
              <p><strong>Trend:</strong> {product.trend === 'FALLING' ? 'Falling' : product.trend === 'RISING' ? 'Rising' : 'Stable'}</p>
              <p><strong>Confidence:</strong> {product.confidence || "High"}</p>
            </div>
          </section>
        </div>

        <hr className="divider" />

        <div className="details-level-section">
          <section className="details-section">
            <button 
              id="tech-details-trigger"
              className="collapsible-trigger"
              onClick={() => setTechDetailsOpen(!techDetailsOpen)}
              aria-expanded={techDetailsOpen}
              aria-controls="tech-details-content"
              aria-label={techDetailsOpen ? "Collapse technical details" : "Expand technical details"}
            >
              <h2 className="level-heading" style={{ margin: 0 }}>Level 3: Technical Details</h2>
              <span className="chevron" aria-hidden="true">{techDetailsOpen ? '▲' : '▼'}</span>
            </button>
            
            {techDetailsOpen && (
              <div 
                id="tech-details-content" 
                className="tech-details-content"
                role="region"
                aria-labelledby="tech-details-trigger"
              >
                <ul>
                  <li><strong>Match confidence:</strong> 98%</li>
                  <li><strong>Data sources:</strong> Amazon API, PriceGrabber</li>
                  <li><strong>Model:</strong> PriceTrend-v2</li>
                  <li><strong>Schema:</strong> product_core_v1</li>
                  <li><strong>Last refresh:</strong> {product.lastChecked || 'Recently'}</li>
                </ul>
              </div>
            )}
          </section>
        </div>
      </div>
    </PageContainer>
  );
}
