document.querySelectorAll('.nav-center li.dropdown').forEach(dropdown => {
  const btn = dropdown.querySelector('.dropbtn');
  const content = dropdown.querySelector('.dropdown-content');

  
  btn.addEventListener('click', e => {
    e.preventDefault();
    const isExpanded = btn.getAttribute('aria-expanded') === 'true';
  
    document.querySelectorAll('.nav-center li.dropdown').forEach(d => {
      const button = d.querySelector('.dropbtn');
      const cont = d.querySelector('.dropdown-content');
      if (d !== dropdown) {
        button.setAttribute('aria-expanded', 'false');
        d.classList.remove('show');
        cont.style.display = 'none';
      }
    });

    if (isExpanded) {
      btn.setAttribute('aria-expanded', 'false');
      dropdown.classList.remove('show');
      content.style.display = 'none';
    } else {
      btn.setAttribute('aria-expanded', 'true');
      dropdown.classList.add('show');
      content.style.display = 'flex';
    }
  });

  
  dropdown.addEventListener('mouseenter', () => {
    btn.setAttribute('aria-expanded', 'true');
    dropdown.classList.add('show');
    content.style.display = 'flex';
  });

  let timeoutClose;
  dropdown.addEventListener('mouseleave', () => {
    timeoutClose = setTimeout(() => {
      btn.setAttribute('aria-expanded', 'false');
      dropdown.classList.remove('show');
      content.style.display = 'none';
    }, 200); 
  });

  
  dropdown.addEventListener('mouseenter', () => {
    clearTimeout(timeoutClose);
  });
});


document.addEventListener('click', e => {
  document.querySelectorAll('.nav-center li.dropdown').forEach(dropdown => {
    const btn = dropdown.querySelector('.dropbtn');
    const content = dropdown.querySelector('.dropdown-content');
    if (!dropdown.contains(e.target)) {
      btn.setAttribute('aria-expanded', 'false');
      dropdown.classList.remove('show');
      content.style.display = 'none';
    }
  });
});

let lastScrollTop = 0;
const navbar = document.querySelector('.navbar');
let ticking = false;

window.addEventListener('scroll', function() {
  if (!ticking) {
    window.requestAnimationFrame(function() {
      let currentScroll = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
      if (currentScroll <= 0) {
        navbar.classList.remove('hidden', 'scrolled');
        navbar.classList.add('visible');
      } else if (currentScroll > lastScrollTop) {
        
        navbar.classList.add('hidden');
        navbar.classList.remove('visible', 'scrolled');
      } else if (currentScroll < lastScrollTop) {
       
        navbar.classList.remove('hidden');
        navbar.classList.add('visible', 'scrolled');
      }
      lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
      ticking = false;
    });
    ticking = true;
  }
});


























function showSuggestions() {
    document.getElementById('suggestionsDropdown').classList.add('active');
}

function selectAddress(address) {
    document.getElementById('addressInput').value = address;
    document.getElementById('suggestionsDropdown').classList.remove('active');
}

function filterSuggestions(value) {
    const dropdown = document.getElementById('suggestionsDropdown');
    const items = dropdown.querySelectorAll('.suggestion-item');
    
    if (!value) {
        items.forEach(item => item.style.display = 'block');
        return;
    }
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(value.toLowerCase())) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function toggleFilters() {
    document.getElementById('filtersDropdown').classList.toggle('active');
}

function goToMap() {
    window.location.href = 'map.html';
}


document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-input-wrapper')) {
        document.getElementById('suggestionsDropdown').classList.remove('active');
    }
    if (!e.target.closest('.filters-wrapper')) {
        document.getElementById('filtersDropdown').classList.remove('active');
    }
});













  document.querySelectorAll('.btn-fav').forEach(button => {
    button.addEventListener('click', () => {
      const isActive = button.classList.toggle('fav-active');
      button.setAttribute('aria-pressed', isActive);
    });
  });

  
  function setupCarrousel(container) {
    const carrousel = container.querySelector('.carrousel');
    const btnLeft = container.querySelector('.arrow-left');
    const btnRight = container.querySelector('.arrow-right');

    btnLeft.addEventListener('click', () => {
      carrousel.scrollBy({ left: -carrousel.clientWidth * 0.7, behavior: 'smooth' });
    });
    btnRight.addEventListener('click', () => {
      carrousel.scrollBy({ left: carrousel.clientWidth * 0.7, behavior: 'smooth' });
    });
  }

  
  document.querySelectorAll('.carrousel-container').forEach(setupCarrousel);









 document.addEventListener('DOMContentLoaded', () => {
    const rows = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if(entry.isIntersecting) {
          entry.target.classList.add('visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });

    rows.forEach(row => observer.observe(row));
  });









const accordion = document.getElementsByClassName('container');

for (i=0; i<accordion.length; i++) {
  accordion[i].addEventListener('click', function () {
    this.classList.toggle('active')
  })
}























