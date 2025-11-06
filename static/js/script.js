document.querySelectorAll('.dropdown').forEach(drop => {
    drop.addEventListener('mouseover', () => {
        drop.querySelector('.dropdown-menu').style.display = 'block';
    });
    drop.addEventListener('mouseout', () => {
        drop.querySelector('.dropdown-menu').style.display = 'none';
    });
});

function toggleMenu() {
  const nav = document.getElementById("myTopnav");
  nav.classList.toggle("responsive");
}
