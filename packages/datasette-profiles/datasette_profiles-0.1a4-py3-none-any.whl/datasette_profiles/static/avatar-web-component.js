class AvatarEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Initial setup
    this.state = 'select'; // 'select' or 'crop'
    this.image = null;
    this.cropX = 0;
    this.cropY = 0;
    this.cropWidth = 0;
    this.cropHeight = 0;
    this.dragStartX = 0;
    this.dragStartY = 0;
    this.dragStartCropX = 0;
    this.dragStartCropY = 0;
    this.activeHandle = null;
    this.isDragging = false;
    
    // Bound methods for event listeners (to properly remove them later)
    this.onDragMove = this.onDragMove.bind(this);
    this.stopDrag = this.stopDrag.bind(this);
    this.onPaste = this.onPaste.bind(this);
    
    // Handle attribute values
    this.avatarWidth = parseInt(this.getAttribute('avatar-width') || '200', 10);
    this.avatarHeight = parseInt(this.getAttribute('avatar-height') || '200', 10);
    this.quality = parseFloat(this.getAttribute('quality') || '0.7');
    this.targetInput = this.getAttribute('target-form-input') || null;
    
    // Render initial UI
    this.render();
    this.setupEventListeners();
  }
  
  render() {
    const aspectRatio = this.avatarWidth / this.avatarHeight;
    
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          width: 100%;
          max-width: 500px;
          margin: 0 auto;
        }
        
        .container {
          border: 2px dashed #ccc;
          border-radius: 8px;
          padding: 20px;
          text-align: center;
          background-color: #f9f9f9;
          transition: all 0.3s;
        }
        
        .container:hover, .container.dragover {
          border-color: #007bff;
          background-color: #f0f8ff;
        }
        
        .select-prompt {
          display: ${this.state === 'select' ? 'block' : 'none'};
        }
        
        #drop-area {
          cursor: ${this.state === 'select' ? 'pointer' : 'default'};
        }
        
        .crop-container {
          display: ${this.state === 'crop' ? 'block' : 'none'};
          position: relative;
          overflow: hidden;
          margin-bottom: 20px;
          touch-action: none;
        }
        
        .crop-image {
          display: block;
          max-width: 100%;
          margin: 0 auto;
        }
        
        .crop-box {
          position: absolute;
          border: 2px solid white;
          box-shadow: 0 0 0 1000px rgba(0, 0, 0, 0.5);
          box-sizing: border-box;
          cursor: move;
        }
        
        .resize-handle {
          position: absolute;
          width: 30px;
          height: 30px;
          background-color: white;
          border-radius: 50%;
          border: 2px solid #007bff;
          transform: translate(-50%, -50%);
          z-index: 10;
          touch-action: none;
        }
        
        .handle-nw { left: 0; top: 0; cursor: nw-resize; }
        .handle-ne { right: 0; top: 0; transform: translate(50%, -50%); cursor: ne-resize; }
        .handle-sw { left: 0; bottom: 0; transform: translate(-50%, 50%); cursor: sw-resize; }
        .handle-se { right: 0; bottom: 0; transform: translate(50%, 50%); cursor: se-resize; }
        
        .preview-container {
          display: ${this.state === 'crop' ? 'block' : 'none'};
          margin-top: 20px;
        }
        
        .preview-title {
          font-weight: bold;
          margin-bottom: 10px;
        }
        
        .preview-image {
          width: ${this.avatarWidth}px;
          height: ${this.avatarHeight}px;
          object-fit: cover;
          border-radius: 4px;
          border: 1px solid #ddd;
        }
        
        button {
          background-color: #007bff;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 10px;
          font-size: 14px;
        }
        
        button:hover {
          background-color: #0069d9;
        }
        
        .file-input {
          display: none;
        }
        
        p {
          margin: 10px 0;
          color: #555;
        }
        
        .instructions {
          font-size: 14px;
          color: #777;
          margin-top: 10px;
        }
      </style>
      
      <div class="container" id="drop-area">
        <div class="select-prompt">
          <p>Click to select an image, drag & drop,<br>or paste from clipboard</p>
          <p class="instructions">Supported formats: JPEG, PNG, GIF, WebP</p>
          <input type="file" class="file-input" accept="image/*">
        </div>
        
        <div class="crop-container">
          <img class="crop-image" draggable="false">
          <div class="crop-box">
            <div class="resize-handle handle-nw" data-handle="nw"></div>
            <div class="resize-handle handle-ne" data-handle="ne"></div>
            <div class="resize-handle handle-sw" data-handle="sw"></div>
            <div class="resize-handle handle-se" data-handle="se"></div>
          </div>
        </div>
        
        <div class="preview-container">
          <div class="preview-title">Preview (${this.avatarWidth}×${this.avatarHeight}px)</div>
          <img class="preview-image">
          <div>
            <button class="reset-button">Select another image</button>
          </div>
        </div>
      </div>
    `;
  }
  
  setupEventListeners() {
    const container = this.shadowRoot.querySelector('#drop-area');
    const fileInput = this.shadowRoot.querySelector('.file-input');
    
    // Make the entire container clickable when in select state
    container.addEventListener('click', () => {
      if (this.state === 'select') {
        fileInput.click();
      }
    });
    
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        this.handleFile(e.target.files[0]);
      }
    });
    
    // Attach reset button listener if in crop state
    if (this.state === 'crop') {
      this.setupResetButton();
    }
    
    // Drag and drop
    container.addEventListener('dragover', (e) => {
      e.preventDefault();
      if (this.state === 'select') {
        container.classList.add('dragover');
      }
    });
    
    container.addEventListener('dragleave', () => {
      container.classList.remove('dragover');
    });
    
    container.addEventListener('drop', (e) => {
      e.preventDefault();
      container.classList.remove('dragover');
      
      if (this.state === 'select' && e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.handleFile(e.dataTransfer.files[0]);
      }
    });
    
    // Paste from clipboard (add global listener)
    document.addEventListener('paste', this.onPaste);
    
    // Handle crop box interaction
    if (this.state === 'crop') {
      this.setupCropInteraction();
    }
  }
  
  setupResetButton() {
    const resetButton = this.shadowRoot.querySelector('.reset-button');
    if (resetButton) {
      resetButton.addEventListener('click', () => {
        this.resetEditor();
      });
    }
  }
  
  onPaste(e) {
    if (this.state === 'select' && e.clipboardData && e.clipboardData.items) {
      for (const item of e.clipboardData.items) {
        if (item.type.indexOf('image') !== -1) {
          const file = item.getAsFile();
          this.handleFile(file);
          break;
        }
      }
    }
  }
  
  setupCropInteraction() {
    const cropBox = this.shadowRoot.querySelector('.crop-box');
    const handles = this.shadowRoot.querySelectorAll('.resize-handle');
    
    if (!cropBox) return;
    
    // Move crop box
    cropBox.addEventListener('mousedown', this.startDragCropBox.bind(this));
    cropBox.addEventListener('touchstart', this.startDragCropBox.bind(this), { passive: false });
    
    // Resize with handles
    handles.forEach(handle => {
      handle.addEventListener('mousedown', (e) => this.startResizeCropBox(e, handle.dataset.handle));
      handle.addEventListener('touchstart', (e) => this.startResizeCropBox(e, handle.dataset.handle), { passive: false });
    });
    
    // Global mouse/touch events for dragging
    window.addEventListener('mousemove', this.onDragMove);
    window.addEventListener('touchmove', this.onDragMove, { passive: false });
    window.addEventListener('mouseup', this.stopDrag);
    window.addEventListener('touchend', this.stopDrag);
  }
  
  disconnectedCallback() {
    // Clean up event listeners
    window.removeEventListener('mousemove', this.onDragMove);
    window.removeEventListener('touchmove', this.onDragMove);
    window.removeEventListener('mouseup', this.stopDrag);
    window.removeEventListener('touchend', this.stopDrag);
    document.removeEventListener('paste', this.onPaste);
  }
  
  startDragCropBox(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const pointer = e.touches ? e.touches[0] : e;
    this.isDragging = true;
    this.dragStartX = pointer.clientX;
    this.dragStartY = pointer.clientY;
    this.dragStartCropX = this.cropX;
    this.dragStartCropY = this.cropY;
  }
  
  startResizeCropBox(e, handle) {
    e.preventDefault();
    e.stopPropagation();
    
    const pointer = e.touches ? e.touches[0] : e;
    this.isDragging = true;
    this.activeHandle = handle;
    this.dragStartX = pointer.clientX;
    this.dragStartY = pointer.clientY;
    this.dragStartCropX = this.cropX;
    this.dragStartCropY = this.cropY;
    this.dragStartCropWidth = this.cropWidth;
    this.dragStartCropHeight = this.cropHeight;
  }
  
  onDragMove(e) {
    if (!this.isDragging) return;
    e.preventDefault();
    
    const pointer = e.touches ? e.touches[0] : e;
    const deltaX = pointer.clientX - this.dragStartX;
    const deltaY = pointer.clientY - this.dragStartY;
    
    const cropImage = this.shadowRoot.querySelector('.crop-image');
    if (!cropImage || !cropImage.complete) return;
    
    const aspectRatio = this.avatarWidth / this.avatarHeight;
    
    if (this.activeHandle) {
      // Resizing
      let newWidth = this.dragStartCropWidth;
      let newHeight = this.dragStartCropHeight;
      let newX = this.dragStartCropX;
      let newY = this.dragStartCropY;
      
      // Calculate new dimensions based on active handle and maintain aspect ratio
      switch (this.activeHandle) {
        case 'nw':
          newWidth = Math.max(50, this.dragStartCropWidth - deltaX);
          newHeight = newWidth / aspectRatio;
          newX = this.dragStartCropX + (this.dragStartCropWidth - newWidth);
          newY = this.dragStartCropY + (this.dragStartCropHeight - newHeight);
          break;
        case 'ne':
          newWidth = Math.max(50, this.dragStartCropWidth + deltaX);
          newHeight = newWidth / aspectRatio;
          newY = this.dragStartCropY + (this.dragStartCropHeight - newHeight);
          break;
        case 'sw':
          newWidth = Math.max(50, this.dragStartCropWidth - deltaX);
          newHeight = newWidth / aspectRatio;
          newX = this.dragStartCropX + (this.dragStartCropWidth - newWidth);
          break;
        case 'se':
          newWidth = Math.max(50, this.dragStartCropWidth + deltaX);
          newHeight = newWidth / aspectRatio;
          break;
      }
      
      // Keep within image bounds
      if (newX < 0) {
        newWidth += newX;
        newHeight = newWidth / aspectRatio;
        newX = 0;
      }
      
      if (newY < 0) {
        newHeight += newY;
        newWidth = newHeight * aspectRatio;
        newY = 0;
      }
      
      if (newX + newWidth > cropImage.width) {
        newWidth = cropImage.width - newX;
        newHeight = newWidth / aspectRatio;
      }
      
      if (newY + newHeight > cropImage.height) {
        newHeight = cropImage.height - newY;
        newWidth = newHeight * aspectRatio;
      }
      
      // Ensure minimum size
      if (newWidth >= 50 && newHeight >= 50) {
        this.cropWidth = newWidth;
        this.cropHeight = newHeight;
        this.cropX = newX;
        this.cropY = newY;
      }
    } else {
      // Moving
      const maxX = cropImage.width - this.cropWidth;
      const maxY = cropImage.height - this.cropHeight;
      
      this.cropX = Math.max(0, Math.min(this.dragStartCropX + deltaX, maxX));
      this.cropY = Math.max(0, Math.min(this.dragStartCropY + deltaY, maxY));
    }
    
    this.updateCropBox();
    this.updatePreview();
  }
  
  stopDrag() {
    this.isDragging = false;
    this.activeHandle = null;
  }
  
  handleFile(file) {
    if (!file || !file.type.match(/^image\//)) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        this.image = img;
        this.initCropping();
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
  
  initCropping() {
    this.state = 'crop';
    this.render();
    
    const cropImage = this.shadowRoot.querySelector('.crop-image');
    if (!cropImage) return;
    
    cropImage.src = this.image.src;
    
    // Set up reset button event listener
    this.setupResetButton();
    
    // Wait for image to load in the DOM
    cropImage.onload = () => {
      const aspectRatio = this.avatarWidth / this.avatarHeight;
      
      // Calculate initial crop position
      if (cropImage.width / cropImage.height > aspectRatio) {
        // Image is wider than our aspect ratio
        this.cropHeight = cropImage.height;
        this.cropWidth = this.cropHeight * aspectRatio;
        this.cropX = (cropImage.width - this.cropWidth) / 2;
        this.cropY = 0;
      } else {
        // Image is taller than our aspect ratio
        this.cropWidth = cropImage.width;
        this.cropHeight = this.cropWidth / aspectRatio;
        this.cropX = 0;
        this.cropY = (cropImage.height - this.cropHeight) / 2;
      }
      
      this.updateCropBox();
      this.setupCropInteraction();
      this.updatePreview();
    };
  }
  
  updateCropBox() {
    const cropBox = this.shadowRoot.querySelector('.crop-box');
    if (!cropBox) return;
    
    // Position and size the crop box
    cropBox.style.left = `${this.cropX}px`;
    cropBox.style.top = `${this.cropY}px`;
    cropBox.style.width = `${this.cropWidth}px`;
    cropBox.style.height = `${this.cropHeight}px`;
  }
  
  updatePreview() {
    if (!this.image) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = this.avatarWidth;
    canvas.height = this.avatarHeight;
    const ctx = canvas.getContext('2d');
    
    // Get the displayed image dimensions
    const cropImage = this.shadowRoot.querySelector('.crop-image');
    if (!cropImage || !cropImage.complete) return;
    
    // Calculate the scale factors between original image and displayed image
    const scaleX = this.image.naturalWidth / cropImage.width;
    const scaleY = this.image.naturalHeight / cropImage.height;
    
    // Adjust crop coordinates to the original image dimensions
    const sourceX = this.cropX * scaleX;
    const sourceY = this.cropY * scaleY;
    const sourceWidth = this.cropWidth * scaleX;
    const sourceHeight = this.cropHeight * scaleY;
    
    // Draw the cropped portion of the image to the canvas
    ctx.drawImage(
      this.image,
      sourceX, sourceY, sourceWidth, sourceHeight,
      0, 0, canvas.width, canvas.height
    );
    
    // Generate JPEG data URL with specified quality
    const dataUrl = canvas.toDataURL('image/jpeg', this.quality);
    
    // Update the preview image
    const previewImage = this.shadowRoot.querySelector('.preview-image');
    if (previewImage) {
      previewImage.src = dataUrl;
    }
    
    // Update the target input field if specified
    if (this.targetInput) {
      const inputElement = document.querySelector(this.targetInput);
      if (inputElement) {
        inputElement.value = dataUrl;
        
        // Dispatch change event
        const event = new Event('change', { bubbles: true });
        inputElement.dispatchEvent(event);
      }
    }
  }
  
  resetEditor() {
    this.state = 'select';
    this.image = null;
    this.render();
    this.setupEventListeners();
    
    // Clear target input if specified
    if (this.targetInput) {
      const inputElement = document.querySelector(this.targetInput);
      if (inputElement) {
        inputElement.value = '';
        
        // Dispatch change event
        const event = new Event('change', { bubbles: true });
        inputElement.dispatchEvent(event);
      }
    }
  }
  
  // Observe attribute changes
  static get observedAttributes() {
    return ['avatar-width', 'avatar-height', 'quality', 'target-form-input'];
  }
  
  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue === newValue) return;
    
    switch (name) {
      case 'avatar-width':
        this.avatarWidth = parseInt(newValue || '200', 10);
        break;
      case 'avatar-height':
        this.avatarHeight = parseInt(newValue || '200', 10);
        break;
      case 'quality':
        this.quality = parseFloat(newValue || '0.7');
        break;
      case 'target-form-input':
        this.targetInput = newValue;
        break;
    }
    
    // Re-render if necessary
    if (this.state === 'crop' && this.image) {
      this.render();
      this.setupCropInteraction();
      this.updateCropBox();
      this.updatePreview();
    } else {
      this.render();
      this.setupEventListeners();
    }
  }
}

// Define the custom element
customElements.define('avatar-editor', AvatarEditor);
