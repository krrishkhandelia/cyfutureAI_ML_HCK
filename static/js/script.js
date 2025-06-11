document.addEventListener('DOMContentLoaded', function () {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-button');
    const imagePreview = document.getElementById('image-preview');
    const filePreview = document.querySelector('.file-preview');
    const removePreview = document.getElementById('remove-preview');
    const filenameDisplay = document.querySelector('.filename-display');
    const scanTypeInputs = document.querySelectorAll('input[name="scan_type"]');

    if (!uploadArea || !fileInput) return;

    let fileSelected = false;
    let scanTypeSelected = false;

    // Handle drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.classList.add('dragover');
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleFileSelection(files);
    }

    uploadArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFileSelection(fileInput.files);
        }
    });

    function handleFileSelection(files) {
        const file = files[0];

        if (!file.type.match('image.*')) {
            showError('Please select an image file (JPEG, PNG)');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showError('File is too large. Maximum file size is 10MB');
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
            uploadArea.querySelector('.upload-content').classList.add('d-none');
            filePreview.classList.remove('d-none');
            filenameDisplay.textContent = file.name;

            fileSelected = true;
            checkFormValidity();
        };
        reader.readAsDataURL(file);
    }

    function clearFileInput() {
        fileInput.value = '';
        imagePreview.src = '';
        filePreview.classList.add('d-none');
        uploadArea.querySelector('.upload-content').classList.remove('d-none');
        filenameDisplay.textContent = '';

        fileSelected = false;
        checkFormValidity();
    }

    if (removePreview) {
        removePreview.addEventListener('click', function (e) {
            e.stopPropagation();
            clearFileInput();
        });
    }

    scanTypeInputs.forEach(input => {
        input.addEventListener('change', () => {
            scanTypeSelected = true;
            checkFormValidity();
        });
    });

    function checkFormValidity() {
        uploadButton.disabled = !(fileSelected && scanTypeSelected);
    }

    function showError(message) {
        const existing = document.querySelector('.alert-danger');
        if (existing) existing.remove();

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        const formContainer = uploadArea.closest('.card-body') || document.body;
        formContainer.insertBefore(alertDiv, formContainer.firstChild);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Result Page: Zoom functionality
    const scanImage = document.querySelector('.scan-image');

    if (scanImage) {
        let scale = 1;
        let panning = false;
        let pointX = 0;
        let pointY = 0;

        function setTransform() {
            scanImage.style.transform = `translate(${pointX}px, ${pointY}px) scale(${scale})`;
        }

        const zoomIn = document.getElementById('zoom-in');
        const zoomOut = document.getElementById('zoom-out');
        const zoomReset = document.getElementById('zoom-reset');

        if (zoomIn) {
            zoomIn.addEventListener('click', () => {
                scale = Math.min(5, scale + 0.1);
                setTransform();
            });
        }

        if (zoomOut) {
            zoomOut.addEventListener('click', () => {
                scale = Math.max(0.5, scale - 0.1);
                setTransform();
            });
        }

        if (zoomReset) {
            zoomReset.addEventListener('click', () => {
                scale = 1;
                pointX = 0;
                pointY = 0;
                setTransform();
            });
        }
    }
});
