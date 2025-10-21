/**
 * Bengal SSG Default Theme
 * Image Lightbox
 *
 * Click to enlarge images in a beautiful lightbox overlay.
 * No dependencies, vanilla JavaScript.
 */

(function() {
  'use strict';

  let lightbox = null;
  let currentImage = null;

  /**
   * Create lightbox element
   */
  function createLightbox() {
    lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.setAttribute('role', 'dialog');
    lightbox.setAttribute('aria-label', 'Image lightbox');
    lightbox.setAttribute('aria-hidden', 'true');

    // Create image element
    const img = document.createElement('img');
    img.className = 'lightbox__image';
    img.alt = '';

    // Create close button
    const closeButton = document.createElement('button');
    closeButton.className = 'lightbox__close';
    closeButton.setAttribute('aria-label', 'Close lightbox');
    closeButton.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    `;

    // Create caption (optional)
    const caption = document.createElement('div');
    caption.className = 'lightbox__caption';

    // Assemble lightbox
    lightbox.appendChild(img);
    lightbox.appendChild(closeButton);
    lightbox.appendChild(caption);

    // Add to document
    document.body.appendChild(lightbox);

    // Event listeners
    closeButton.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', function(e) {
      // Close when clicking backdrop (not the image)
      if (e.target === lightbox) {
        closeLightbox();
      }
    });

    // Keyboard controls
    document.addEventListener('keydown', handleKeyboard);

    return lightbox;
  }

  /**
   * Open lightbox with an image
   *
   * @param {HTMLImageElement} imgElement - Image element to display
   */
  function openLightbox(imgElement) {
    if (!lightbox) {
      lightbox = createLightbox();
    }

    currentImage = imgElement;
    const img = lightbox.querySelector('.lightbox__image');
    const caption = lightbox.querySelector('.lightbox__caption');

    // Set image source (use high-res version if available)
    const highResSrc = imgElement.getAttribute('data-lightbox-src') || imgElement.src;
    img.src = highResSrc;
    img.alt = imgElement.alt;

    // Set caption if available
    const captionText = imgElement.alt || imgElement.getAttribute('data-caption');
    if (captionText) {
      caption.textContent = captionText;
      caption.style.display = 'block';
    } else {
      caption.style.display = 'none';
    }

    // Show lightbox
    lightbox.classList.add('active');
    lightbox.setAttribute('aria-hidden', 'false');

    // Prevent body scroll
    document.body.style.overflow = 'hidden';

    // Focus the lightbox for keyboard controls
    lightbox.focus();
  }

  /**
   * Close lightbox
   */
  function closeLightbox() {
    if (!lightbox) return;

    lightbox.classList.remove('active');
    lightbox.setAttribute('aria-hidden', 'true');

    // Restore body scroll
    document.body.style.overflow = '';

    // Return focus to the original image
    if (currentImage) {
      currentImage.focus();
    }

    currentImage = null;
  }

  /**
   * Handle keyboard controls
   *
   * @param {KeyboardEvent} e - Keyboard event
   */
  function handleKeyboard(e) {
    if (!lightbox || !lightbox.classList.contains('active')) return;

    switch (e.key) {
      case 'Escape':
        closeLightbox();
        break;

      case 'ArrowLeft':
        // Navigate to previous image (if multiple)
        navigateImages(-1);
        break;

      case 'ArrowRight':
        // Navigate to next image (if multiple)
        navigateImages(1);
        break;
    }
  }

  /**
   * Navigate between images (if multiple in a gallery)
   *
   * @param {number} direction - Direction to navigate (-1 or 1)
   */
  function navigateImages(direction) {
    if (!currentImage) return;

    // Find all lightbox-enabled images
    const images = Array.from(document.querySelectorAll('[data-lightbox]'));
    const currentIndex = images.indexOf(currentImage);

    if (currentIndex === -1 || images.length <= 1) return;

    // Calculate new index (with wrapping)
    let newIndex = currentIndex + direction;
    if (newIndex < 0) newIndex = images.length - 1;
    if (newIndex >= images.length) newIndex = 0;

    // Open new image
    openLightbox(images[newIndex]);
  }

  /**
   * Setup lightbox for images
   * Automatically adds lightbox to all content images
   */
  function setupImageLightbox() {
    // Find all images in content areas
    const selectors = [
      '.prose img',
      '.docs-content img',
      'article img',
      'main img'
    ];

    const images = document.querySelectorAll(selectors.join(', '));

    images.forEach(img => {
      // Skip if already has lightbox or explicitly disabled
      if (img.hasAttribute('data-lightbox') || img.hasAttribute('data-no-lightbox')) {
        return;
      }

      // Skip small images (icons, avatars)
      if (img.width < 400 && img.height < 400) {
        return;
      }

      // Skip images inside links (they already have a destination)
      if (img.closest('a')) {
        return;
      }

      // Enable lightbox
      img.setAttribute('data-lightbox', '');
      img.setAttribute('tabindex', '0');
      img.setAttribute('role', 'button');
      img.setAttribute('aria-label', `View larger version of: ${img.alt || 'image'}`);

      // Add click handler
      img.addEventListener('click', function() {
        openLightbox(this);
      });

      // Add keyboard handler for accessibility
      img.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openLightbox(this);
        }
      });
    });
  }

  /**
   * Initialize
   */
  function init() {
    setupImageLightbox();
    console.log('Image lightbox initialized');
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Re-run setup if images are dynamically added
  // (e.g., via AJAX or lazy loading)
  if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
      let shouldUpdate = false;
      mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length > 0) {
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeName === 'IMG' || (node.querySelector && node.querySelector('img'))) {
              shouldUpdate = true;
            }
          });
        }
      });

      if (shouldUpdate) {
        setupImageLightbox();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

})();
