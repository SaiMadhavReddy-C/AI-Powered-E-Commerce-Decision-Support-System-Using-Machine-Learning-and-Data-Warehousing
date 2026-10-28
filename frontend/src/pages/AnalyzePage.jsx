import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchProduct } from '../services/api';
import PageContainer from '../components/Layout/PageContainer';
import ThinkingScreen from '../components/Thinking/ThinkingScreen';
import ProductHeader from '../components/Product/ProductHeader';
import RecommendationCard from '../components/Recommendation/RecommendationCard';
import WhyPanel from '../components/Recommendation/WhyPanel';
import BestOption from '../components/Recommendation/BestOption';
import WatchButton from '../components/Watchlist/WatchButton';
import EmptyState from '../components/common/EmptyState';
import { RECOMMENDATION_TYPES } from '../utils/constants';
import './AnalyzePage.css';

const THINKING_STEPS = [
  'Product found',
  'Offers checked',
  'Recent prices checked',
  'Putting it together...'
];

export default function AnalyzePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [product, setProduct] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [thinkingComplete, setThinkingComplete] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      try {
        setLoading(true);
        setThinkingComplete(false);
        
        // Very fast processing (50ms per step) for instant UI feel
        for (let i = 0; i < THINKING_STEPS.length; i++) {
          if (!isMounted) return;
          setCurrentStep(i);
          await new Promise(r => setTimeout(r, 50));
        }

        if (!isMounted) return;
        setThinkingComplete(true);
        const data = await fetchProduct(id);
        setProduct(data);
      } catch (err) {
        console.error('Failed to load product', err);
        setProduct(null);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, [id]);

  if (loading) {
    return (
      <PageContainer>
        <div className="analyze-page-container">
          <ThinkingScreen 
            productName={product?.name || 'the product'} 
            steps={THINKING_STEPS} 
            currentStep={currentStep} 
            complete={thinkingComplete} 
          />
        </div>
      </PageContainer>
    );
  }

  if (!product) {
    return (
      <PageContainer>
        <div className="analyze-page-container">
          <EmptyState 
            emoji="🔍"
            title="Product not found" 
            description="We couldn't find the product you're looking for. Please try another search."
          />
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="analyze-page-container fade-in-up">
        <ProductHeader product={product} />
        
        <div className="analyze-section">
          <RecommendationCard product={product} />
        </div>

        <div className="analyze-section">
          <WhyPanel 
            reasons={product.reasons} 
            recommendationLabel={RECOMMENDATION_TYPES[product.recommendation]?.label || 'Recommendation'} 
          />
        </div>

        {product.bestOffer && (
          <div className="analyze-section">
            <BestOption 
              bestOffer={product.bestOffer} 
              currentPrice={product.currentPrice} 
              onCompareClick={() => navigate(`/analyze/${id}/details`)} 
            />
          </div>
        )}

        <div className="analyze-section analyze-action-section">
          <WatchButton productId={product.id} targetPrice={product.buyPoint} productName={product.name} />
        </div>

        <hr className="divider" />

        <div className="see-how-decided-wrapper">
          <Link to={`/analyze/${id}/details`} className="btn-secondary see-how-decided-btn">
            See how I decided &rarr;
          </Link>
        </div>
      </div>
    </PageContainer>
  );
}
