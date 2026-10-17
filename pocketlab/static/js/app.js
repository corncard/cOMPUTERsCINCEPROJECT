document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('expense-form');
  const tableBody = document.getElementById('expense-table-body');

  if (!form || !tableBody) {
    return;
  }

  const formatCurrency = (value) => `$${Number(value).toFixed(2)}`;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const payload = {
      date: formData.get('date'),
      category: formData.get('category'),
      amount: formData.get('amount'),
      description: formData.get('description') || '',
    };

    try {
      const response = await fetch('/api/expenses', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unable to save expense.' }));
        throw new Error(errorData.error || 'Unable to save expense.');
      }

      const item = await response.json();
      const row = document.createElement('tr');
      row.dataset.id = item.id;
      row.innerHTML = `
        <td>${item.date}</td>
        <td>${item.category}</td>
        <td>${formatCurrency(item.amount)}</td>
        <td>${item.description || ''}</td>
      `;
      tableBody.prepend(row);
      form.reset();
      form.querySelector('input[name="date"]').focus();
    } catch (error) {
      window.alert(error.message);
    }
  });
});
