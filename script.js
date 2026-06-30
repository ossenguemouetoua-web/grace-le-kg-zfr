document.addEventListener('click', function(e) {
    const b = document.createElement('div');
    b.classList.add('bulle-eau');
    b.style.left = e.clientX + window.scrollX + 'px';
    b.style.top = e.clientY + window.scrollY + 'px';
    document.body.appendChild(b);
    setTimeout(() => { b.remove(); }, 600);
});
