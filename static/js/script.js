function toggleMenu() {
  const nav = document.getElementById("myTopnav");
  const dropdowns = nav.querySelectorAll('.dropdown .dropdown-content');

  nav.classList.toggle("responsive");

  dropdowns.forEach(dd => dd.style.display = "none");
};

function toggleDropdown(event) {
  if (window.innerWidth <= 600) {
    event.preventDefault();
    const dropdownContent = event.currentTarget.nextElementSibling;
    dropdownContent.style.display =
      dropdownContent.style.display === "block" ? "none" : "block";
  }
};

function addIngredient() {
  const container = document.getElementById('ingredients-container');
  const newItem = document.createElement('div');
  newItem.className = 'field-item';
  newItem.innerHTML = `
    <input type="text" name="ingredients" placeholder="np. 200 g mąki">
    <button type="button" class="btn btn-danger" onclick="removeField(this)">
      <i class="fa fa-trash"></i>
    </button>`;
  container.appendChild(newItem);
};

function initStarRating(containerSelector, inputSelector) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  const stars = container.querySelectorAll('.fa-star');
  const input = document.querySelector(inputSelector);

  stars.forEach(star => {
    star.addEventListener('click', () => {
      const value = star.dataset.value;
      input.value = value;
      stars.forEach(s => s.classList.toggle('star-checked', s.dataset.value <= value));
    });

    star.addEventListener('mouseover', () => {
      const value = star.dataset.value;
      stars.forEach(s => s.classList.toggle('star-checked', s.dataset.value <= value));
    });

    star.addEventListener('mouseout', () => {
      const selected = input.value;
      stars.forEach(s => s.classList.toggle('star-checked', s.dataset.value <= selected));
    });
  });
}

function addStep() {
  const container = document.getElementById('steps-container');
  const newItem = document.createElement('div');
  newItem.className = 'field-item';
  newItem.innerHTML = `
    <input type="text" name="steps" placeholder="np. Wymieszaj składniki">
    <button type="button" class="btn btn-danger" onclick="removeField(this)">
      <i class="fa fa-trash"></i>
    </button>`;
  container.appendChild(newItem);
}

function removeField(element) {
  element.closest('.field-item').remove();
}

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
};



document.addEventListener('DOMContentLoaded', function() {
  initStarRating('#commentModal .comment-form .star-rating', '#rating-new'); 
  initStarRating('#commentModal .comment-form .star-rating', '#rating-edit'); 
});

document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
  if (flashMessages.length > 0) {
    setTimeout(function() {
      flashMessages.forEach(function(message) {
        message.style.transition = "opacity 0.5s ease, margin-top 0.5s ease";
        message.style.opacity = "0";
        message.style.marginTop = "-" + message.offsetHeight + "px";
        setTimeout(() => message.remove(), 500);
      });
    }, 5000);
  }
})

window.addEventListener('resize', () => {
  const nav = document.getElementById("myTopnav");
  const dropdowns = nav.querySelectorAll('.dropdown .dropdown-content');

  if (window.innerWidth > 600) {
    dropdowns.forEach(dd => dd.style.display = '');
    nav.classList.remove('responsive');
  }
});
