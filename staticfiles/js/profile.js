function initProfile() {
  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(btn.dataset.tab).classList.add('active');
    });
  });

  // Modal
  const modal = document.getElementById("editModal");
  const openBtn = document.getElementById("editBtn");
  const closeBtn = document.getElementById("closeModal");
  openBtn && openBtn.addEventListener("click", () => modal.style.display = "block");
  closeBtn && closeBtn.addEventListener("click", () => modal.style.display = "none");
  window.addEventListener("click", e => {
    if (e.target == modal) modal.style.display = "none";
  });

  // Delete confirmation
  const delBtn = document.getElementById("deleteAccountBtn");
  const cancelDel = document.getElementById("cancelDeleteBtn");
  const confirmBox = document.getElementById("confirmationDialog");
  delBtn && delBtn.addEventListener("click", () => confirmBox.style.display = "block");
  cancelDel && cancelDel.addEventListener("click", () => confirmBox.style.display = "none");

  // Init save buttons
  if (typeof initSaveButtons === 'function') {
    initSaveButtons();
  }

  // Init like buttons (optional)
  if (typeof initLikeButtons === 'function') {
    initLikeButtons();
  }
}

// При першому завантаженні
document.addEventListener('DOMContentLoaded', initProfile);

// При кожному поверненні через HTMX
document.body.addEventListener('htmx:afterSwap', (e) => {
  if (e.target && (e.target.id === "profile-content" || e.target.closest('#profile-content'))) {
    initProfile();
  }
});
