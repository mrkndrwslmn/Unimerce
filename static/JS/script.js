document.querySelectorAll('.accordion-menu').forEach(button => {
    button.addEventListener('click', () => {
        const submenu = button.nextElementSibling; // Select the submenu directly following the button

        submenu.classList.toggle('active'); // Toggle the active class
        const icon = button.querySelector('.caret-back');
        icon.classList.toggle('rotate'); // Optional: to rotate the caret icon if needed
    });
});

const scrollLeftButton = document.getElementById('scroll-left');
const scrollRightButton = document.getElementById('scroll-right');
const container = document.getElementById('collections-container');

// Function to check if the container is scrollable
function checkScrollable() {
    const isScrollable = container.scrollWidth > container.clientWidth;
    scrollLeftButton.style.display = isScrollable ? 'block' : 'none';
    scrollRightButton.style.display = isScrollable ? 'block' : 'none';

    // Enable or disable buttons based on scroll position
    scrollLeftButton.disabled = container.scrollLeft === 0; // Disable left button if at the start
    scrollRightButton.disabled = container.scrollLeft + container.clientWidth >= container.scrollWidth; // Disable right button if at the end
    updateButtonStyles(); // Update button styles based on their state
}

// Function to update button styles based on disabled state
function updateButtonStyles() {
    if (scrollLeftButton.disabled) {
        scrollLeftButton.classList.add('disabled');
    } else {
        scrollLeftButton.classList.remove('disabled');
    }

    if (scrollRightButton.disabled) {
        scrollRightButton.classList.add('disabled');
    } else {
        scrollRightButton.classList.remove('disabled');
    }
}

// Initial check for scrollable content
checkScrollable();

// Add scroll event listener to check if the content is scrollable after content is loaded
window.addEventListener('load', checkScrollable);

// Scroll right button functionality
scrollRightButton.addEventListener('click', function() {
    container.scrollBy({
        left: 330,
        behavior: 'smooth'
    });
    checkScrollable(); // Check scrollable state after scrolling
});

// Scroll left button functionality
scrollLeftButton.addEventListener('click', function() {
    container.scrollBy({
        left: -330,
        behavior: 'smooth'
    });
    checkScrollable(); // Check scrollable state after scrolling
});

// Existing color change functionality
const colors = document.querySelectorAll('.colors i');
const productImage = document.querySelector('.image-container img');

colors.forEach(color => {
    color.addEventListener('click', function() {
        // Update the product image based on the selected color (if you have different images for each color)
        const selectedColor = this.classList[2]; // Get the color class (e.g., 'red')
        productImage.src = `url_to_image_${selectedColor}.png`; // Update the image source based on the selected color
    });
});

let slideIndex = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
let autoSlideInterval;

// Show the current slide and hide the rest
function showSlides(index) {
  slides.forEach((slide, idx) => {
    if (idx === index) {
      slide.style.visibility = "visible"; // Show the current slide
      slide.style.opacity = "1"; // Fade in
      slide.classList.add('active');
    } else {
      slide.style.visibility = "hidden"; // Keep space but hide
      slide.style.opacity = "0"; // Fade out
      slide.classList.remove('active');
    }
  });

  dots.forEach((dot) => {
    dot.classList.remove('active'); // Remove active class from all dots
  });
  dots[index].classList.add('active'); // Set the current dot as active
}

// Start the automatic slideshow
function startAutoSlide() {
  autoSlideInterval = setInterval(() => {
    slideIndex++;
    if (slideIndex >= slides.length) slideIndex = 0; // Loop back to the first slide
    showSlides(slideIndex);
  }, 5000); // Change slide every 5 seconds for smoother transitions
}

// Manual navigation (previous/next)
function plusSlides(n) {
  clearInterval(autoSlideInterval); // Stop auto slideshow when manually navigating
  slideIndex += n;
  if (slideIndex < 0) slideIndex = slides.length - 1; // Loop to the last slide
  if (slideIndex >= slides.length) slideIndex = 0; // Loop back to the first slide
  showSlides(slideIndex);
  startAutoSlide(); // Restart auto slideshow
}

// Dot navigation
dots.forEach((dot, idx) => {
  dot.addEventListener('click', () => {
    clearInterval(autoSlideInterval); // Stop auto slideshow when dot is clicked
    slideIndex = idx;
    showSlides(slideIndex);
    startAutoSlide(); // Restart auto slideshow
  });
});

// Initialize the slideshow
showSlides(slideIndex); // Show the first slide
startAutoSlide(); // Start the automatic slideshow

document.addEventListener('DOMContentLoaded', function () {
  // Select all promotion items
  const promotions = document.querySelectorAll('.promotion-item');

  promotions.forEach(promotion => {
      // Get the end date from the data attribute
      const endDateString = promotion.dataset.endDate.trim();

      const [year, month, day] = endDateString.split('-').map(num => parseInt(num, 10));
      const endDate = new Date(year, month - 1, day, 23, 59, 59); // Month is 0-indexed

      // Start the countdown
      const timer = promotion.querySelector('.timer');
      const daysElem = promotion.querySelector('.days');
      const hoursElem = promotion.querySelector('.hours');
      const minutesElem = promotion.querySelector('.minutes');
      const secondsElem = promotion.querySelector('.seconds');

      const countdown = setInterval(() => {
          const now = new Date();
          const distance = endDate - now;
          
          if (distance < 0) {
            clearInterval(countdown);
            timer.innerHTML = "Promotion Ended"; // End message
            return;
        }

        // Calculate time components
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Display results
        daysElem.textContent = days < 10 ? '0' + days : days;
        hoursElem.textContent = hours < 10 ? '0' + hours : hours;
        minutesElem.textContent = minutes < 10 ? '0' + minutes : minutes;
        secondsElem.textContent = seconds < 10 ? '0' + seconds : seconds;
    }, 1000); // Update every second
});
});

// Wait for the DOM to fully load
document.addEventListener('DOMContentLoaded', function() {
  // Select the flash messages container
  var flashMessages = document.getElementById('flash-messages');
  
  // If it exists, show it and set a timeout to fade it out
  if (flashMessages) {
      flashMessages.style.display = 'block'; // Show the flash messages
      
      setTimeout(function() {
          flashMessages.classList.remove('show'); // Remove the 'show' class to fade it out
          flashMessages.classList.add('fade'); // Add the 'fade' class for Bootstrap animation

          // Optionally, remove the element from the DOM after the fade transition
          setTimeout(function() {
              flashMessages.remove();
          }, 150); // Adjust time to match CSS transition duration (300ms for Bootstrap)
      }, 3000); // Adjust time for how long the message should display (3000ms = 3 seconds)
  }
});

// JavaScript to toggle the image input container
document.getElementById('edit-button').onclick = function() {
  var inputContainer = document.getElementById('image-input-container');
  if (inputContainer.style.display === 'none') {
      inputContainer.style.display = 'block'; // Show input
  } else {
      inputContainer.style.display = 'none'; // Hide input
  }
};


document.addEventListener("DOMContentLoaded", function() {
  const flashMessage = document.querySelector('.flash-message');
  if (flashMessage) {
    // Set timeout to hide the message after 25 seconds
    setTimeout(function() {
      flashMessage.style.opacity = '0'; // Start fade-out
      setTimeout(function() {
        flashMessage.remove(); // Remove the element from the DOM
      }, 500); // Match this time with the CSS transition duration
    }, 25000); // 25 seconds
  }
});

/* SELLER APPLICATION */
let currentStep = 0; // Current step index
const steps = document.querySelectorAll('.form-step'); // Get all form steps

function showStep(step) {
    // Hide all steps
    steps.forEach((el, index) => {
        el.style.display = index === step ? 'block' : 'none';
    });

    // Update progress circles
    const circles = document.querySelectorAll('.circle');
    circles.forEach((circle, index) => {
        if (index < step) {
            circle.classList.add('done');
        } else if (index === step) {
            circle.classList.add('active');
        } else {
            circle.classList.remove('done', 'active');
        }
    });

    // Enable/disable previous button
    document.getElementById('prevBtn').disabled = step === 0;
    // Show/hide submit step button
    document.getElementById('nextBtn').style.display = step === steps.length - 1 ? 'none' : 'inline-block';
}

// Handle next and previous button clicks
function nextPrev(n) {
    // Hide current step
    steps[currentStep].style.display = 'none';
    // Move to the next step
    currentStep += n;
    // If you have reached the last step, do not go further
    if (currentStep >= steps.length) {
        currentStep = steps.length - 1;
    }
    // If you have reached the first step, do not go back
    if (currentStep < 0) {
        currentStep = 0;
    }
    // Show the current step
    showStep(currentStep);
}

// Show the first step initially
showStep(currentStep);
