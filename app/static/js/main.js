document.addEventListener("DOMContentLoaded", function () {
    const yearNodes = document.querySelectorAll('[data-current-year]');
    yearNodes.forEach((node) => node.textContent = new Date().getFullYear());

    const targetInput = document.getElementById('target_url');
    const targetSelect = document.getElementById('demo_target');
    const targetNote = document.getElementById('demoTargetNote');
    const quickCards = document.querySelectorAll('.target-card');

    function updateTarget(url, summary) {
        if (targetInput && url) targetInput.value = url;
        if (targetNote) targetNote.textContent = summary || 'Demo target selected.';
        if (targetSelect && url) {
            const matching = Array.from(targetSelect.options).find(opt => opt.value === url);
            if (matching) targetSelect.value = url;
        }
    }

    if (targetSelect) {
        targetSelect.addEventListener('change', function () {
            const selected = targetSelect.options[targetSelect.selectedIndex];
            if (!selected || !selected.value) return;
            updateTarget(selected.value, selected.dataset.summary + ' Risk profile: ' + selected.dataset.risk + '.');
        });
    }

    quickCards.forEach((card) => {
        card.addEventListener('click', function () {
            updateTarget(card.dataset.targetUrl, card.dataset.targetSummary);
            quickCards.forEach(btn => btn.classList.remove('is-active'));
            card.classList.add('is-active');
        });
    });
});
