export const daysUntilExpiry = (expiryDate) => {
  const now = new Date();
  const expiry = new Date(expiryDate);
  const diff = expiry.getTime() - now.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
};

export const getRiskBadge = (daysLeft) => {
  if (daysLeft <= 3) return "High Risk";
  if (daysLeft <= 7) return "Moderate Risk";
  return "Safe";
};
