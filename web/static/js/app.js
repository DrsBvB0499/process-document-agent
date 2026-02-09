// Global app functionality

// Modal handling
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('new-project-modal');
    const newProjectBtn = document.getElementById('new-project-btn');
    const closeBtn = modal?.querySelector('.close');
    const form = document.getElementById('new-project-form');

    if (newProjectBtn) {
        newProjectBtn.onclick = function() {
            modal.style.display = 'block';
        }
    }

    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.style.display = 'none';
        }
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const projectName = document.getElementById('project_name').value;
            const description = document.getElementById('description').value;

            try {
                const response = await fetch('/api/projects', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        project_name: projectName,
                        description: description
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Success! Redirect to the new project
                    window.location.href = `/project/${data.project_id}`;
                } else {
                    alert(`Error: ${data.error}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        });
    }
});

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// API helper
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
