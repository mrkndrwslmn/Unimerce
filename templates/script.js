document.getElementById('scroll-right').addEventListener('click', function() {
    const container = document.getElementById('collections-container');
    container.scrollBy({
        left: 330,
        behavior: 'smooth'
    });
});
