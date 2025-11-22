function toggleMenu() {
  const nav = document.getElementById("myTopnav");
  const dropdowns = nav.querySelectorAll('.dropdown .dropdown-content');

  if (nav.className === "topnav") {
    nav.className += " responsive";
  } else {
    nav.className = "topnav";
  }

  // Ukryj wszystkie submenu przy każdym toggle hamburgera
  dropdowns.forEach(dd => {
    dd.style.display = "none";
  });
}

// Funkcja dla mobilnego rozwijania submenu
function toggleDropdown(event) {
  if (window.innerWidth <= 600) {
    event.preventDefault();
    const dropdownContent = event.currentTarget.nextElementSibling;

    // Toggle tylko tego dropdownu
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
    } else {
      dropdownContent.style.display = "block";
    }
  }
}

function addIngredient() {
  const container = document.getElementById('ingredients-container');
  const newItem = document.createElement('div');
  newItem.className = 'field-item';
  newItem.innerHTML = `
    <input type="text" name="ingredients" placeholder="np. 200 g mąki">
    <button type="button" class="btn-delete" onclick="removeField(this)">
      <i class="fa fa-trash"></i>
    </button>
  `;
  container.appendChild(newItem);
}

function addStep() {
  const container = document.getElementById('steps-container');
  const newItem = document.createElement('div');
  newItem.className = 'field-item';
  newItem.innerHTML = `
    <input type="text" name="steps" placeholder="np. Wymieszaj składniki">
    <button type="button" class="btn-delete" onclick="removeField(this)">
      <i class="fa fa-trash"></i>
    </button>
  `;
  container.appendChild(newItem);
}

function removeField(element) {
  element.closest('.field-item').remove();
}

//logowanie i rejestracja
function openModal(id) {
  document.getElementById(id).style.display = "block";
}
function closeModal(id) {
  document.getElementById(id).style.display = "none";
}
window.onclick = function(event) {
  const modals = document.getElementsByClassName('modal');
  for (let m of modals) {
    if (event.target == m) m.style.display = "none";
  }
}

function initStarRating(containerSelector, inputSelector) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  const stars = container.querySelectorAll('.fa-star');
  const input = document.querySelector(inputSelector);

  stars.forEach(star => {
    star.addEventListener('click', () => {
      const value = star.getAttribute('data-value');
      input.value = value;

      stars.forEach(s => {
        s.classList.toggle('star-checked', s.getAttribute('data-value') <= value);
      });
    });

    star.addEventListener('mouseover', () => {
      const value = star.getAttribute('data-value');
      stars.forEach(s => {
        s.classList.toggle('star-checked', s.getAttribute('data-value') <= value);
      });
    });

    star.addEventListener('mouseout', () => {
      const selected = input.value;
      stars.forEach(s => {
        s.classList.toggle('star-checked', s.getAttribute('data-value') <= selected);
      });
    });
  });
}

window.addEventListener('resize', () => {
  const nav = document.getElementById("myTopnav");
  const dropdowns = nav.querySelectorAll('.dropdown .dropdown-content');

  if (window.innerWidth > 600) {
    dropdowns.forEach(dd => {
      dd.style.display = ''; // usuwa inline display, pozwala CSS zrobić swoje
    });

    // usuń klasę responsive jeśli była
    if (nav.classList.contains('responsive')) {
      nav.classList.remove('responsive');
    }
  }
});