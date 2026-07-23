(function () {
  function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => toast.classList.remove('is-visible'), 2500);
  }

  function request(url, body) {
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.CSRF_TOKEN,
      },
      body: JSON.stringify(body),
    }).then(async (res) => {
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Something went wrong.');
      }
      return data;
    });
  }

  function addItem(variantId, quantity) {
    if (!variantId) {
      showToast('Please choose an option first.');
      return Promise.reject(new Error('No variant selected'));
    }
    return request('/api/cart/add/', { variant_id: variantId, quantity: quantity })
      .then((data) => {
        const counter = document.getElementById('cart-count');
        if (counter) counter.textContent = data.total_items;
        showToast('Added to cart.');
        return data;
      })
      .catch((err) => {
        showToast(err.message);
        throw err;
      });
  }

  function updateItem(itemId, quantity) {
    return request(`/api/cart/items/${itemId}/update/`, { quantity: quantity })
      .catch((err) => {
        showToast(err.message);
        throw err;
      });
  }

  function removeItem(itemId) {
    return request(`/api/cart/items/${itemId}/remove/`, {})
      .then((data) => {
        showToast('Item removed.');
        return data;
      });
  }

  function formatPrice(value) {
    const amount = Math.round(parseFloat(value));
    return Number.isFinite(amount) ? amount.toLocaleString('en-US') : value;
  }

  window.CSRF_TOKEN = window.CSRF_TOKEN || (typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : '');

  window.ELinkCart = { addItem, updateItem, removeItem, showToast, formatPrice };

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-quick-add]');
    if (!btn || btn.disabled) return;
    e.preventDefault();

    const variantId = btn.dataset.variantId;
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.textContent = 'Adding…';

    addItem(variantId, 1)
      .catch(() => {})
      .finally(() => {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
      });
  });
})();
