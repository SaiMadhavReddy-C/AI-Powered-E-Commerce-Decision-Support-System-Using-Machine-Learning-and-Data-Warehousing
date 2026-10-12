
export const formatPrice = (price) => {
  if (price === undefined || price === null) return '';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(price);
};

export const formatPriceK = (price) => {
    if (price >= 1000) {
        return '₹' + (price / 1000).toFixed(0) + 'K';
    }
    return '₹' + price;
}

export const formatTimeAgo = (timestamp) => {
  if (!timestamp) return '';
  const diff = Date.now() - new Date(timestamp).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Checked just now';
  if (mins < 60) return `Checked ${mins} min ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `Checked ${hours} hr ago`;
  const days = Math.floor(hours / 24);
  return `Checked ${days} days ago`;
};
