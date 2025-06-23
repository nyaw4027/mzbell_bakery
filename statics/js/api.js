document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('product-list');
  const searchInput = document.getElementById('search-input');
  const filterSelect = document.getElementById('filter-select');

  function fetchProducts(query = '') {
    let url = '/api/products/';
    if (query) {
      url += `?search=${encodeURIComponent(query)}`;
    }

    fetch(url, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then(products => {
        if (!container) return;

        container.innerHTML = '';

        const filtered = filterSelect.value === 'on_sale'
          ? products.filter(p => p.is_on_sale)
          : products;

        if (filtered.length === 0) {
          container.innerHTML = '<p>No products found.</p>';
          return;
        }

        filtered.forEach(product => {
          const card = document.createElement('div');
          card.className = 'product-card';
          card.style.border = '1px solid #ddd';
          card.style.padding = '10px';
          card.style.marginBottom = '10px';
          card.style.borderRadius = '8px';

          card.innerHTML = `
            <h3>${product.name}</h3>
            <p><strong>Price:</strong> ₵${product.price}</p>
            <p>${product.description}</p>
            <p><strong>Stock:</strong> ${product.stock > 0 ? product.stock : 'Out of stock'}</p>
            ${product.image_url ? `<img src="${product.image_url}" alt="${product.name}" style="max-width:150px;" />` : '<p><em>No image available</em></p>'}
            <button class="add-to-cart-btn" data-product-id="${product.id}">Add to Cart</button>
          `;

          container.appendChild(card);
        });

        attachAddToCartListeners();
      })
      .catch(error => {
        console.error('Fetch error:', error);
      });
  }

  function attachAddToCartListeners() {
    const buttons = document.querySelectorAll('.add-to-cart-btn');
    buttons.forEach(button => {
      button.addEventListener('click', () => {
        const productId = button.dataset.productId;
        fetch(`/cart/add/${productId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ quantity: 1 })
        })
          .then(response => response.json())
          .then(data => {
            alert(`${data.name} added to cart!`);
          })
          .catch(err => {
            alert('Failed to add to cart');
            console.error(err);
          });
      });
    });
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Search & Filter Events
  searchInput?.addEventListener('input', () => fetchProducts(searchInput.value));
  filterSelect?.addEventListener('change', () => fetchProducts(searchInput.value));

  fetchProducts(); // Initial load
});
