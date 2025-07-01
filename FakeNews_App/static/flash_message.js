
window.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.message_flash');

    flashMessages.forEach((msg) => {
        setTimeout(() => {
            msg.classList.add('fade-out');

            // Ensuite on le retire complètement du DOM après l'animation
            setTimeout(() => {
                msg.remove();
            }, 1000); // temps de la transition CSS (1s)
        }, 5000); // 5 secondes avant de disparaître
    });
});

