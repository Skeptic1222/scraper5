/**
 * File Upload Handler Module
 * Handles file uploads with drag-and-drop support
 */

class UploadHandler {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.uploadForm = document.getElementById('upload-form');
        this.progressDiv = document.getElementById('upload-progress');
        this.progressBar = this.progressDiv?.querySelector('.progress-bar');
        this.uploadStatus = document.getElementById('upload-status');
        this.resultsDiv = document.getElementById('upload-results');
        this.errorsDiv = document.getElementById('upload-errors');
        this.uploadMessage = document.getElementById('upload-message');
        this.errorMessage = document.getElementById('upload-error-message');

        this.init();
    }

    init() {
        if (!this.uploadArea || !this.fileInput) {
            console.log('Upload elements not found on this page');
            return;
        }

        // File input change handler
        this.fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            if (files.length > 0) {
                this.handleFiles(files);
            }
        });

        // Drag and drop handlers
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.add('drag-over');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.remove('drag-over');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFiles(files);
            }
        });

        // Load uploaded files list
        this.loadUploadsList();
    }

    handleFiles(files) {
        // Process each file
        for (let file of files) {
            this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        // Validate file
        const allowedExtensions = ['png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'avi', 'mov', 'pdf', 'doc', 'docx', 'txt', 'zip'];
        const fileExtension = file.name.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
            this.showError(`File type .${fileExtension} is not allowed`);
            return;
        }

        // Check file size (16MB max)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            this.showError(`File ${file.name} is too large. Maximum size is 16MB`);
            return;
        }

        // Show progress
        this.showProgress();

        // Create FormData
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Upload file
            const xhr = new XMLHttpRequest();

            // Track upload progress
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    this.updateProgress(percentComplete);
                }
            });

            // Handle completion
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            this.showSuccess(response.message || 'File uploaded successfully');
                            this.loadUploadsList(); // Refresh the list
                            // Clear file input
                            this.fileInput.value = '';
                        } else {
                            this.showError(response.error || 'Upload failed');
                        }
                    } catch (e) {
                        this.showError('Invalid server response');
                    }
                } else {
                    this.showError(`Upload failed with status ${xhr.status}`);
                }
                this.hideProgress();
            });

            // Handle errors
            xhr.addEventListener('error', () => {
                this.showError('Network error during upload');
                this.hideProgress();
            });

            // Send request
            xhr.open('POST', window.APP_BASE + '/api/upload');
            xhr.send(formData);

        } catch (error) {
            console.error('Upload error:', error);
            this.showError(error.message || 'Upload failed');
            this.hideProgress();
        }
    }

    showProgress() {
        if (this.progressDiv) {
            this.progressDiv.style.display = 'block';
            this.resultsDiv.style.display = 'none';
            this.errorsDiv.style.display = 'none';
        }
    }

    hideProgress() {
        if (this.progressDiv) {
            setTimeout(() => {
                this.progressDiv.style.display = 'none';
            }, 500);
        }
    }

    updateProgress(percent) {
        if (this.progressBar) {
            this.progressBar.style.width = percent + '%';
            this.progressBar.setAttribute('aria-valuenow', percent);
        }
        if (this.uploadStatus) {
            this.uploadStatus.textContent = `Uploading... ${Math.round(percent)}%`;
        }
    }

    showSuccess(message) {
        if (this.resultsDiv && this.uploadMessage) {
            this.uploadMessage.textContent = message;
            this.resultsDiv.style.display = 'block';
            this.errorsDiv.style.display = 'none';

            // Hide after 5 seconds
            setTimeout(() => {
                this.resultsDiv.style.display = 'none';
            }, 5000);
        }
    }

    showError(message) {
        if (this.errorsDiv && this.errorMessage) {
            this.errorMessage.textContent = message;
            this.errorsDiv.style.display = 'block';
            this.resultsDiv.style.display = 'none';

            // Hide after 5 seconds
            setTimeout(() => {
                this.errorsDiv.style.display = 'none';
            }, 5000);
        }
    }

    async loadUploadsList() {
        const uploadsList = document.getElementById('uploads-list');
        if (!uploadsList) return;

        try {
            const response = await fetch(window.APP_BASE + '/api/uploads');
            const data = await response.json();

            if (data.success && data.uploads) {
                if (data.uploads.length === 0) {
                    uploadsList.innerHTML = `
                        <div class="text-center text-muted">
                            <i class="fas fa-inbox fa-3x mb-3"></i>
                            <p>No files uploaded yet</p>
                        </div>
                    `;
                } else {
                    uploadsList.innerHTML = this.renderUploadsList(data.uploads);
                }
            } else {
                uploadsList.innerHTML = '<div class="alert alert-warning">Failed to load uploads</div>';
            }
        } catch (error) {
            console.error('Error loading uploads:', error);
            uploadsList.innerHTML = '<div class="alert alert-danger">Error loading uploads</div>';
        }
    }

    renderUploadsList(uploads) {
        return `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Size</th>
                            <th>Type</th>
                            <th>Uploaded</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${uploads.map(upload => `
                            <tr>
                                <td>
                                    <i class="fas ${this.getFileIcon(upload.file_type)}"></i>
                                    ${upload.original_filename || upload.filename}
                                </td>
                                <td>${this.formatFileSize(upload.file_size)}</td>
                                <td>${upload.file_type || 'Unknown'}</td>
                                <td>${this.formatDate(upload.upload_time)}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="window.open('${upload.url}', '_blank')">
                                        <i class="fas fa-eye"></i> View
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="uploadHandler.deleteUpload(${upload.id})">
                                        <i class="fas fa-trash"></i> Delete
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    getFileIcon(fileType) {
        if (!fileType) return 'fa-file';

        if (fileType.startsWith('image/')) return 'fa-image';
        if (fileType.startsWith('video/')) return 'fa-video';
        if (fileType.startsWith('audio/')) return 'fa-music';
        if (fileType.includes('pdf')) return 'fa-file-pdf';
        if (fileType.includes('word') || fileType.includes('doc')) return 'fa-file-word';
        if (fileType.includes('zip') || fileType.includes('archive')) return 'fa-file-archive';
        if (fileType.includes('text')) return 'fa-file-alt';

        return 'fa-file';
    }

    formatFileSize(bytes) {
        if (!bytes) return '0 B';

        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';

        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    async deleteUpload(uploadId) {
        if (!confirm('Are you sure you want to delete this file?')) {
            return;
        }

        try {
            const response = await fetch(window.APP_BASE + '/api/uploads/' + uploadId, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('File deleted successfully');
                this.loadUploadsList(); // Refresh the list
            } else {
                this.showError(data.error || 'Failed to delete file');
            }
        } catch (error) {
            console.error('Error deleting upload:', error);
            this.showError('Error deleting file');
        }
    }
}

// Initialize on page load
let uploadHandler;
document.addEventListener('DOMContentLoaded', () => {
    uploadHandler = new UploadHandler();
});

// Function for refresh button
function refreshUploadsList() {
    if (uploadHandler) {
        uploadHandler.loadUploadsList();
    }
}