import React, { useState, useRef } from 'react';
import { formatPriceK, formatPrice } from '../../utils/formatPrice';
import './PriceChart.css';

const PriceChart = ({ priceHistory, buyPoint, currentPrice: _currentPrice }) => {
  const [tooltip, setTooltip] = useState(null);
  const svgRef = useRef(null);

  if (!priceHistory || priceHistory.length < 2) return null;

  const width = 600;
  const height = 240;
  const padding = { top: 20, right: 20, bottom: 30, left: 50 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const prices = priceHistory.map(d => d.price);
  if (buyPoint) prices.push(buyPoint);
  const minPrice = Math.min(...prices) * 0.95;
  const maxPrice = Math.max(...prices) * 1.05;
  
  const minDate = new Date(priceHistory[0].date).getTime();
  const maxDate = new Date(priceHistory[priceHistory.length - 1].date).getTime();

  const getX = (dateStr) => {
    const time = new Date(dateStr).getTime();
    return padding.left + ((time - minDate) / (maxDate - minDate)) * innerWidth;
  };

  const getY = (price) => {
    return padding.top + innerHeight - ((price - minPrice) / (maxPrice - minPrice)) * innerHeight;
  };

  // Path generation
  const d = priceHistory.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${getX(pt.date)} ${getY(pt.price)}`).join(' ');
  const areaD = `${d} L ${getX(priceHistory[priceHistory.length-1].date)} ${height - padding.bottom} L ${padding.left} ${height - padding.bottom} Z`;

  const updateTooltipFromClientX = (clientX) => {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    if (!rect.width) return;

    // Scale from rendered client pixels to SVG viewBox width (600)
    const scaleX = width / rect.width;
    const x = (clientX - rect.left) * scaleX;
    
    if (x < padding.left || x > width - padding.right) {
      setTooltip(null);
      return;
    }
    
    const ratio = Math.max(0, Math.min(1, (x - padding.left) / innerWidth));
    const time = minDate + ratio * (maxDate - minDate);
    
    // Find closest point
    let closest = priceHistory[0];
    let minDist = Math.abs(new Date(closest.date).getTime() - time);
    
    for (const pt of priceHistory) {
      const dist = Math.abs(new Date(pt.date).getTime() - time);
      if (dist < minDist) {
        minDist = dist;
        closest = pt;
      }
    }
    
    setTooltip({
      x: getX(closest.date),
      y: getY(closest.price),
      date: new Date(closest.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
      price: closest.price,
      rawDate: closest.date
    });
  };

  const handleMouseMove = (e) => {
    updateTooltipFromClientX(e.clientX);
  };

  const handleTouch = (e) => {
    if (e.touches && e.touches.length > 0) {
      updateTooltipFromClientX(e.touches[0].clientX);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      e.preventDefault();
      const currentIndex = tooltip
        ? priceHistory.findIndex(p => p.date === tooltip.rawDate)
        : -1;
      let nextIndex = 0;
      if (currentIndex !== -1) {
        if (e.key === 'ArrowRight') {
          nextIndex = currentIndex < priceHistory.length - 1 ? currentIndex + 1 : currentIndex;
        } else {
          nextIndex = currentIndex > 0 ? currentIndex - 1 : 0;
        }
      } else {
        nextIndex = e.key === 'ArrowRight' ? 0 : priceHistory.length - 1;
      }
      const pt = priceHistory[nextIndex];
      setTooltip({
        x: getX(pt.date),
        y: getY(pt.price),
        date: new Date(pt.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
        price: pt.price,
        rawDate: pt.date
      });
    } else if (e.key === 'Escape') {
      setTooltip(null);
    }
  };

  const startDateLabel = new Date(priceHistory[0].date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  const endDateLabel = new Date(priceHistory[priceHistory.length - 1].date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });

  return (
    <div className="price-chart-container">
      <svg 
        ref={svgRef}
        viewBox={`0 0 ${width} ${height}`} 
        className="price-chart-svg"
        tabIndex="0"
        role="region"
        aria-label={`Interactive price history chart from ${startDateLabel} to ${endDateLabel}. Drag across or use left and right arrow keys to view price tooltips.`}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setTooltip(null)}
        onTouchStart={handleTouch}
        onTouchMove={handleTouch}
        onKeyDown={handleKeyDown}
      >
        {/* Y Axis Grid & Labels */}
        {[0, 0.5, 1].map(tick => {
          const p = minPrice + (maxPrice - minPrice) * tick;
          const y = getY(p);
          return (
            <g key={tick}>
              <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} stroke="var(--border)" opacity="0.3" />
              <text x={padding.left - 10} y={y + 4} textAnchor="end" fontSize="11" fill="var(--text-secondary)">
                {formatPriceK(p)}
              </text>
            </g>
          );
        })}

        {/* X Axis Line */}
        <line x1={padding.left} y1={height - padding.bottom} x2={width - padding.right} y2={height - padding.bottom} stroke="var(--border)" />
        
        {/* X Axis Labels (every 15 days roughly) */}
        {priceHistory.filter((_, i) => i % Math.ceil(priceHistory.length / 5) === 0).map((pt, i) => (
          <text key={i} x={getX(pt.date)} y={height - padding.bottom + 15} textAnchor="middle" fontSize="11" fill="var(--text-secondary)">
             {new Date(pt.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
          </text>
        ))}

        {/* Area */}
        <path d={areaD} fill="var(--accent-light)" opacity="0.4" />
        
        {/* Line */}
        <path d={d} fill="none" stroke="var(--text)" strokeWidth="2" />

        {/* Buy Point Line */}
        {buyPoint && (
          <line 
            x1={padding.left} y1={getY(buyPoint)} 
            x2={width - padding.right} y2={getY(buyPoint)} 
            stroke="var(--positive)" strokeWidth="1" strokeDasharray="4 4" 
          />
        )}

        {/* Last Point */}
        <circle cx={getX(priceHistory[priceHistory.length-1].date)} cy={getY(priceHistory[priceHistory.length-1].price)} r="4" fill="var(--accent)" />

        {/* Tooltip */}
        {tooltip && (
          <g>
            <line x1={tooltip.x} y1={padding.top} x2={tooltip.x} y2={height - padding.bottom} stroke="var(--accent)" strokeDasharray="2 2" opacity="0.5" />
            <circle cx={tooltip.x} cy={tooltip.y} r="5" fill="white" stroke="var(--accent)" strokeWidth="2" />
            <rect x={tooltip.x > width/2 ? tooltip.x - 100 : tooltip.x + 10} y={tooltip.y - 40} width="90" height="40" rx="4" fill="white" stroke="var(--border)" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.1))" />
            <text x={tooltip.x > width/2 ? tooltip.x - 55 : tooltip.x + 55} y={tooltip.y - 24} textAnchor="middle" fontSize="12" fontWeight="600" fill="var(--text)">
              {formatPrice(tooltip.price)}
            </text>
            <text x={tooltip.x > width/2 ? tooltip.x - 55 : tooltip.x + 55} y={tooltip.y - 10} textAnchor="middle" fontSize="10" fill="var(--text-secondary)">
              {tooltip.date}
            </text>
          </g>
        )}
      </svg>
    </div>
  );
};

export default PriceChart;
