(function () {
  /* --------------------------------------------------------------------
     Product image dropzone + dynamic formset rows (product add/edit page)
     -------------------------------------------------------------------- */

  function previewFile(dropzone, file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      dropzone.style.backgroundImage = `url(${e.target.result})`;
      dropzone.classList.add('has-image');
    };
    reader.readAsDataURL(file);

    const row = dropzone.closest('[data-formset-row]');
    const filenameEl = row ? row.querySelector('.image-dropzone__filename') : null;
    if (filenameEl) filenameEl.textContent = file.name;
  }

  document.addEventListener('change', (e) => {
    if (e.target.matches('.image-dropzone input[type="file"]')) {
      previewFile(e.target.closest('.image-dropzone'), e.target.files[0]);
    }
  });

  document.addEventListener('dragover', (e) => {
    const dropzone = e.target.closest('.image-dropzone');
    if (dropzone) {
      e.preventDefault();
      dropzone.classList.add('is-dragover');
    }
  });

  document.addEventListener('dragleave', (e) => {
    const dropzone = e.target.closest('.image-dropzone');
    if (dropzone) dropzone.classList.remove('is-dragover');
  });

  document.addEventListener('drop', (e) => {
    const dropzone = e.target.closest('.image-dropzone');
    if (!dropzone) return;
    e.preventDefault();
    dropzone.classList.remove('is-dragover');

    const input = dropzone.querySelector('input[type="file"]');
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (input && file) {
      input.files = e.dataTransfer.files;
      previewFile(dropzone, file);
    }
  });

  document.addEventListener('click', (e) => {
    const addBtn = e.target.closest('[data-add-row]');
    if (addBtn) {
      const prefix = addBtn.dataset.addRow;
      const template = document.getElementById(`${prefix}-empty-form`);
      const container = document.querySelector(`[data-formset="${prefix}"]`);
      const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
      if (!template || !container || !totalForms) return;

      const index = parseInt(totalForms.value, 10);
      const html = template.innerHTML.replace(/__prefix__/g, index);
      const wrapper = document.createElement('div');
      wrapper.innerHTML = html.trim();
      container.appendChild(wrapper.firstElementChild);
      totalForms.value = index + 1;
      return;
    }

    const removeBtn = e.target.closest('[data-remove-row]');
    if (removeBtn) {
      const row = removeBtn.closest('[data-formset-row]');
      if (row) row.remove();
    }
  });

  /* --------------------------------------------------------------------
     Mobile sidebar drawer
     -------------------------------------------------------------------- */

  const hamburger = document.getElementById('dash-hamburger');
  const sidebar = document.getElementById('dash-sidebar');
  const sidebarBackdrop = document.getElementById('sidebar-backdrop');

  function openSidebar() {
    sidebar.classList.add('is-open');
    sidebarBackdrop.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('is-open');
    sidebarBackdrop.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  if (hamburger && sidebar && sidebarBackdrop) {
    hamburger.addEventListener('click', openSidebar);
    sidebarBackdrop.addEventListener('click', closeSidebar);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeSidebar();
    });
  }

  /* --------------------------------------------------------------------
     Modal system: AJAX-loaded forms, AJAX-submitted forms, confirm dialogs
     -------------------------------------------------------------------- */

  const overlay = document.getElementById('modal-overlay');
  const modalBody = document.getElementById('modal-body');
  const modalTitle = document.getElementById('modal-title');
  if (!overlay) return;

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
  }

  function openModal(title) {
    modalTitle.textContent = title || '';
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    overlay.classList.remove('is-open');
    modalBody.innerHTML = '';
    document.body.style.overflow = '';
  }

  async function loadModalForm(url, title) {
    openModal(title);
    modalBody.innerHTML = '<p class="modal-loading">Loading…</p>';
    try {
      const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      modalBody.innerHTML = await res.text();
    } catch (err) {
      modalBody.innerHTML = '<p class="form-errors">Could not load this form. Please try again.</p>';
    }
  }

  function openConfirmModal(title, message, actionUrl, confirmLabel) {
    openModal(title);
    modalBody.innerHTML = `
      <p>${message}</p>
      <form data-modal-ajax-form action="${actionUrl}" method="post">
        <div class="form-actions">
          <button type="submit" class="btn btn-danger">${confirmLabel || 'Yes, continue'}</button>
          <button type="button" class="btn btn-outline" data-modal-close>Cancel</button>
        </div>
      </form>`;
  }

  async function submitModalForm(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    try {
      const res = await fetch(form.action || window.location.href, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: new FormData(form),
      });

      const contentType = res.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const data = await res.json();
        if (data.success) {
          window.location.reload();
        } else {
          modalBody.innerHTML = `<p class="form-errors">${data.error || 'Something went wrong.'}</p>
            <div class="form-actions"><button type="button" class="btn btn-outline" data-modal-close>Close</button></div>`;
        }
      } else {
        // Form re-rendered with validation errors
        modalBody.innerHTML = await res.text();
      }
    } catch (err) {
      modalBody.innerHTML = '<p class="form-errors">Something went wrong. Please try again.</p>';
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  }

  document.addEventListener('click', (e) => {
    if (e.target === overlay || e.target.closest('[data-modal-close]')) {
      closeModal();
      return;
    }

    const opener = e.target.closest('[data-modal-url]');
    if (opener && !opener.hasAttribute('data-modal-confirm')) {
      e.preventDefault();
      loadModalForm(opener.dataset.modalUrl, opener.dataset.modalTitle || '');
      return;
    }

    const confirmer = e.target.closest('[data-modal-confirm]');
    if (confirmer) {
      e.preventDefault();
      openConfirmModal(
        confirmer.dataset.modalTitle || 'Are you sure?',
        confirmer.dataset.modalMessage || 'This action cannot be undone.',
        confirmer.dataset.modalUrl,
        confirmer.dataset.modalConfirmLabel,
      );
    }
  });

  document.addEventListener('submit', (e) => {
    if (e.target.closest('#modal-body')) {
      e.preventDefault();
      submitModalForm(e.target);
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) closeModal();
  });
})();
