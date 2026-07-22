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
    if (e.target.matches('[data-formset="images"] input[name$="-is_primary"]') && e.target.checked) {
      document.querySelectorAll('[data-formset="images"] input[name$="-is_primary"]').forEach((checkbox) => {
        if (checkbox !== e.target) checkbox.checked = false;
      });
    }
  });

  function addFormsetRow(prefix) {
    const template = document.getElementById(`${prefix}-empty-form`);
    const container = document.querySelector(`[data-formset="${prefix}"]`);
    const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    if (!template || !container || !totalForms) return null;

    const index = parseInt(totalForms.value, 10);
    const html = template.innerHTML.replace(/__prefix__/g, index);
    const wrapper = document.createElement('div');
    wrapper.innerHTML = html.trim();
    const row = wrapper.firstElementChild;
    container.appendChild(row);
    totalForms.value = index + 1;
    return row;
  }

  document.addEventListener('click', (e) => {
    const addBtn = e.target.closest('[data-add-row]');
    if (addBtn) {
      addFormsetRow(addBtn.dataset.addRow);
      return;
    }

    const removeBtn = e.target.closest('[data-remove-row]');
    if (removeBtn) {
      const row = removeBtn.closest('[data-formset-row]');
      if (row) row.remove();
    }
  });

  /* --------------------------------------------------------------------
     Multi-file image upload: drop/select several photos at once and
     have each one fill its own formset row automatically.
     -------------------------------------------------------------------- */

  function findEmptyImageRow() {
    const rows = document.querySelectorAll('[data-formset="images"] [data-formset-row]');
    for (const row of rows) {
      const dropzone = row.querySelector('.image-dropzone');
      const input = row.querySelector('.image-dropzone input[type="file"]');
      if (dropzone && input && !input.files.length && !dropzone.classList.contains('has-image')) {
        return row;
      }
    }
    return null;
  }

  function assignFileToRow(row, file) {
    const dropzone = row.querySelector('.image-dropzone');
    const input = dropzone ? dropzone.querySelector('input[type="file"]') : null;
    if (!dropzone || !input) return;

    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;
    previewFile(dropzone, file);
  }

  function handleMultipleImageFiles(fileList) {
    Array.from(fileList)
      .filter((file) => file.type.startsWith('image/'))
      .forEach((file) => {
        const row = findEmptyImageRow() || addFormsetRow('images');
        if (row) assignFileToRow(row, file);
      });
  }

  const multiDropzone = document.getElementById('images-multi-dropzone');
  const multiInput = document.getElementById('images-multi-input');

  if (multiDropzone && multiInput) {
    multiInput.addEventListener('change', () => {
      handleMultipleImageFiles(multiInput.files);
      multiInput.value = '';
    });

    multiDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      multiDropzone.classList.add('is-dragover');
    });

    multiDropzone.addEventListener('dragleave', () => {
      multiDropzone.classList.remove('is-dragover');
    });

    multiDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      multiDropzone.classList.remove('is-dragover');
      if (e.dataTransfer.files && e.dataTransfer.files.length) {
        handleMultipleImageFiles(e.dataTransfer.files);
      }
    });
  }

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
