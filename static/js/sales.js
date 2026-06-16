// Update cart count
function updateCartCount() {
    const cartCount = localStorage.getItem('cartCount') || '0';
    document.querySelector('.cart-count').textContent = cartCount;
}

// Add to cart
function addToCart(productId) {
    const cartCount = parseInt(localStorage.getItem('cartCount') || '0');
    localStorage.setItem('cartCount', cartCount + 1);
    updateCartCount();

    // Show notification
    showNotification('เพิ่มสินค้าลงตะกร้าแล้ว!', 'success');
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#27ae60' : '#3498db'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize cart count on page load
document.addEventListener('DOMContentLoaded', updateCartCount);

// Add to cart button listeners
document.addEventListener('click', function(e) {
    if (e.target.closest('.btn-add-cart')) {
        const btn = e.target.closest('.btn-add-cart');
        const productId = btn.dataset.productId;
        addToCart(productId);
    }
});
