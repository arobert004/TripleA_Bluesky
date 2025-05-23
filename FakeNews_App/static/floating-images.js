const fakeNewsQuotes = [
    "La Terre est plate !",
    "Le changement climatique est un canular !",
    "Les vaccins causent l'autisme !",
    "Les Illuminati contrôlent le monde en secret !",
    "L'alunissage de 1969 a été une mise en scène !",
    "YEAH!",
    "Tous les Anthony sont très séduisants",
    "Le monde est controlé par les reptiliens !"
];

const images = [
    '41oZ1lKdB5L._AC_UF894_1000_QL80_-removebg-preview.png',
    'elon-musk-peta-removebg-preview.png',
    'macron-c-darko-vojinovic-ap-sipa-removebg-preview.png',
    'stupidmemeguy.png',
    'stupidguymeme2.png'
];

function createFloatingElement() {
    const container = document.createElement('div');
    container.className = 'floating-container';
    container.style.position = 'fixed';
    container.style.zIndex = '1000';
    
    // Bulle avec texte
    const bubbleContainer = document.createElement('div');
    bubbleContainer.className = 'bubble-container';
    
    const bubbleImg = document.createElement('img');
    bubbleImg.src = '/static/images/Bulle-bd-droite-removebg-preview.png';
    bubbleImg.className = 'bubble-image';
    
    const bubbleText = document.createElement('div');
    bubbleText.className = 'bubble-text';
    bubbleText.textContent = fakeNewsQuotes[Math.floor(Math.random() * fakeNewsQuotes.length)];
    
    bubbleContainer.appendChild(bubbleImg);
    bubbleContainer.appendChild(bubbleText);
    container.appendChild(bubbleContainer);
    
    // Image
    const img = document.createElement('img');
    img.src = `/static/images/${images[Math.floor(Math.random() * images.length)]}`;
    img.className = 'floating-image';
    container.appendChild(img);
    
    // Position aléatoire
    const side = Math.random() < 0.5 ? 'left' : 'right';
    container.style[side] = Math.random() * 20 + 'px';
    
    document.body.appendChild(container);
    
    // Animation de la bulle
    setTimeout(() => {
        bubbleContainer.style.opacity = '1';
        bubbleContainer.style.transform = 'translateY(0)';
    }, 100);
    
    // Disparition
    setTimeout(() => {
        bubbleContainer.style.opacity = '0';
        bubbleContainer.style.transform = 'translateY(20px)';
        setTimeout(() => {
            document.body.removeChild(container);
        }, 500);
    }, 5000);
}

// Création périodique d'éléments flottants
function startFloatingElements() {
    setInterval(() => {
        if (document.querySelectorAll('.floating-container').length < 2) {
            createFloatingElement();
        }
    }, 8000);
    
    // Premier élément
    createFloatingElement();
}

// Démarrer quand le DOM est chargé
document.addEventListener('DOMContentLoaded', startFloatingElements);
