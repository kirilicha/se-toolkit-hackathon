const form = document.getElementById('item-form');
const itemsContainer = document.getElementById('items');
const statsContainer = document.getElementById('stats');
const emptyState = document.getElementById('empty-state');
const refreshBtn = document.getElementById('refresh-btn');
const cancelBtn = document.getElementById('cancel-btn');
const formTitle = document.getElementById('form-title');
const submitBtn = document.getElementById('submit-btn');

const filters = {
  search: document.getElementById('search'),
  itemType: document.getElementById('filter-type'),
  sortBy: document.getElementById('sort-by'),
  order: document.getElementById('order'),
  favoriteOnly: document.getElementById('favorite-only'),
};

function getFormData() {
  return {
    item_type: document.getElementById('item-type').value,
    title: document.getElementById('title').value.trim(),
    rating: Number(document.getElementById('rating').value),
    entry_date: document.getElementById('entry-date').value || null,
    comment: document.getElementById('comment').value.trim(),
    is_favorite: document.getElementById('is-favorite').checked,
  };
}

function resetForm() {
  form.reset();
  document.getElementById('item-id').value = '';
  formTitle.textContent = 'Add item';
  submitBtn.textContent = 'Save item';
  cancelBtn.classList.add('hidden');
}

function fillForm(item) {
  document.getElementById('item-id').value = item.id;
  document.getElementById('item-type').value = item.item_type;
  document.getElementById('title').value = item.title;
  document.getElementById('rating').value = item.rating;
  document.getElementById('entry-date').value = item.entry_date || '';
  document.getElementById('comment').value = item.comment || '';
  document.getElementById('is-favorite').checked = item.is_favorite;
  formTitle.textContent = `Edit item #${item.id}`;
  submitBtn.textContent = 'Update item';
  cancelBtn.classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function fetchStats() {
  const response = await fetch('/api/stats');
  const stats = await response.json();
  statsContainer.innerHTML = `
    <div class="stat-card"><span>Total</span><strong>${stats.total_items}</strong></div>
    <div class="stat-card"><span>Books</span><strong>${stats.books_count}</strong></div>
    <div class="stat-card"><span>Movies</span><strong>${stats.movies_count}</strong></div>
    <div class="stat-card"><span>Favorites</span><strong>${stats.favorites_count}</strong></div>
    <div class="stat-card"><span>Avg rating</span><strong>${stats.average_rating}</strong></div>
  `;
}

function buildQuery() {
  const params = new URLSearchParams({
    sort_by: filters.sortBy.value,
    order: filters.order.value,
    item_type: filters.itemType.value,
    favorite_only: String(filters.favoriteOnly.checked),
  });
  if (filters.search.value.trim()) {
    params.set('search', filters.search.value.trim());
  }
  return params.toString();
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderItems(items) {
  itemsContainer.innerHTML = '';
  emptyState.classList.toggle('hidden', items.length !== 0);

  for (const item of items) {
    const card = document.createElement('article');
    card.className = 'item-card';
    card.innerHTML = `
      <div class="item-header">
        <div>
          <div class="pill-row">
            <span class="pill">${escapeHtml(item.item_type)}</span>
            ${item.is_favorite ? '<span class="pill favorite">favorite</span>' : ''}
          </div>
          <h3>${escapeHtml(item.title)}</h3>
        </div>
        <div class="rating">${item.rating}/10</div>
      </div>
      <p class="meta">Read / watched: ${item.entry_date || '—'} · Added: ${new Date(item.created_at).toLocaleString()}</p>
      <p class="comment">${item.comment ? escapeHtml(item.comment) : 'No comment yet.'}</p>
      <div class="card-actions">
        <button data-action="edit" data-id="${item.id}">Edit</button>
        <button data-action="delete" data-id="${item.id}" class="danger">Delete</button>
      </div>
    `;
    itemsContainer.appendChild(card);
  }
}

async function fetchItems() {
  const response = await fetch(`/api/items?${buildQuery()}`);
  const items = await response.json();
  renderItems(items);
}

async function reloadData() {
  await Promise.all([fetchStats(), fetchItems()]);
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const itemId = document.getElementById('item-id').value;
  const method = itemId ? 'PUT' : 'POST';
  const url = itemId ? `/api/items/${itemId}` : '/api/items';

  const response = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(getFormData()),
  });

  if (!response.ok) {
    const error = await response.json();
    alert(error.detail || 'Request failed');
    return;
  }

  resetForm();
  await reloadData();
});

itemsContainer.addEventListener('click', async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;

  const action = target.dataset.action;
  const itemId = target.dataset.id;
  if (!itemId) return;

  if (action === 'edit') {
    const response = await fetch(`/api/items/${itemId}`);
    const item = await response.json();
    fillForm(item);
  }

  if (action === 'delete') {
    const confirmed = confirm('Delete this item?');
    if (!confirmed) return;

    const response = await fetch(`/api/items/${itemId}`, { method: 'DELETE' });
    if (!response.ok) {
      alert('Delete failed');
      return;
    }
    await reloadData();
  }
});

for (const input of Object.values(filters)) {
  input.addEventListener('input', reloadData);
  input.addEventListener('change', reloadData);
}

refreshBtn.addEventListener('click', reloadData);
cancelBtn.addEventListener('click', resetForm);

resetForm();
reloadData();
