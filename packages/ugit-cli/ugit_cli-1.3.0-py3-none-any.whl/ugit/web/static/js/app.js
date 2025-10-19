let currentPath = '';
let currentFiles = [];
let allFiles = [];
let navigationHistory = [];
let latestCommitInfo = null;
let currentFilter = 'all';
let searchQuery = '';

// File type icons mapping for better visual representation
const fileIconMap = {
    // Programming languages
    'js': 'fa-brands fa-js',
    'ts': 'fa-brands fa-js',
    'jsx': 'fa-brands fa-react',
    'tsx': 'fa-brands fa-react',
    'py': 'fa-brands fa-python',
    'java': 'fa-brands fa-java',
    'php': 'fa-brands fa-php',
    'rb': 'fa-solid fa-gem',
    'go': 'fa-brands fa-golang',
    'rs': 'fa-solid fa-gear',
    'c': 'fa-solid fa-c',
    'cpp': 'fa-solid fa-code',
    'cs': 'fa-solid fa-code',
    'swift': 'fa-brands fa-swift',
    
    // Web
    'html': 'fa-brands fa-html5',
    'css': 'fa-brands fa-css3-alt',
    'scss': 'fa-brands fa-sass',
    'sass': 'fa-brands fa-sass',
    'less': 'fa-brands fa-less',
    'vue': 'fa-brands fa-vuejs',
    
    // Data/Config
    'json': 'fa-solid fa-brackets-curly',
    'xml': 'fa-solid fa-code',
    'yaml': 'fa-solid fa-file-code',
    'yml': 'fa-solid fa-file-code',
    'toml': 'fa-solid fa-file-code',
    'ini': 'fa-solid fa-file-code',
    'conf': 'fa-solid fa-gear',
    'env': 'fa-solid fa-lock',
    
    // Documents
    'md': 'fa-brands fa-markdown',
    'txt': 'fa-solid fa-file-lines',
    'pdf': 'fa-solid fa-file-pdf',
    'doc': 'fa-solid fa-file-word',
    'docx': 'fa-solid fa-file-word',
    
    // Images
    'png': 'fa-solid fa-file-image',
    'jpg': 'fa-solid fa-file-image',
    'jpeg': 'fa-solid fa-file-image',
    'gif': 'fa-solid fa-file-image',
    'svg': 'fa-solid fa-file-image',
    'webp': 'fa-solid fa-file-image',
    'ico': 'fa-solid fa-file-image',
    
    // Archives
    'zip': 'fa-solid fa-file-zipper',
    'tar': 'fa-solid fa-file-zipper',
    'gz': 'fa-solid fa-file-zipper',
    'rar': 'fa-solid fa-file-zipper',
    '7z': 'fa-solid fa-file-zipper',
    
    // Others
    'sql': 'fa-solid fa-database',
    'db': 'fa-solid fa-database',
    'lock': 'fa-solid fa-lock',
    'log': 'fa-solid fa-file-lines',
    'sh': 'fa-solid fa-terminal',
    'bash': 'fa-solid fa-terminal',
    'gitignore': 'fa-brands fa-git-alt',
    'dockerfile': 'fa-brands fa-docker',
};

document.addEventListener('DOMContentLoaded', function() {
    loadLatestCommit();
    loadFiles('');
    
    document.getElementById('back-button').addEventListener('click', goBack);
    document.getElementById('back-to-files').addEventListener('click', showFileList);
    
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    const refreshBtn = document.getElementById('refresh-commits');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadCommits);
    }
    
    // Search functionality
    const searchInput = document.getElementById('file-search');
    const clearSearch = document.getElementById('clear-search');
    
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase();
            filterAndDisplayFiles();
            clearSearch.style.display = searchQuery ? 'block' : 'none';
        });
        
        clearSearch.addEventListener('click', () => {
            searchInput.value = '';
            searchQuery = '';
            filterAndDisplayFiles();
            clearSearch.style.display = 'none';
        });
    }
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            filterAndDisplayFiles();
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            if (e.key === 'Escape') {
                e.target.blur();
                searchInput.value = '';
                searchQuery = '';
                filterAndDisplayFiles();
                clearSearch.style.display = 'none';
            }
            return;
        }
        
        switch(e.key) {
            case '/':
                e.preventDefault();
                searchInput.focus();
                break;
            case '?':
                e.preventDefault();
                toggleShortcuts();
                break;
            case 'Escape':
                if (document.getElementById('file-viewer').style.display === 'block') {
                    showFileList();
                } else if (navigationHistory.length > 0) {
                    goBack();
                }
                break;
            case 'r':
                e.preventDefault();
                if (document.querySelector('[data-tab="files"]').classList.contains('active')) {
                    loadFiles(currentPath);
                } else {
                    loadCommits();
                }
                break;
            case 'h':
                e.preventDefault();
                loadFiles('');
                navigationHistory = [];
                document.getElementById('back-button').style.display = 'none';
                break;
        }
    });
});

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = 'notification show ' + type;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function showLoading(show = true) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'flex' : 'none';
}

function loadLatestCommit() {
    fetch('/api/latest-commit')
        .then(response => response.json())
        .then(data => {
            if (data.commit) {
                latestCommitInfo = data.commit;
                document.getElementById('latest-commit-message').textContent = data.commit.message || 'No commit message';
                document.getElementById('latest-commit-hash').textContent = data.commit.sha ? data.commit.sha.substring(0, 7) : 'N/A';
                document.getElementById('latest-commit-date').textContent = data.commit.timestamp ? formatCommitDate(data.commit.timestamp) : 'N/A';
            } else {
                document.getElementById('latest-commit-message').textContent = 'No commits yet';
                document.getElementById('latest-commit-hash').textContent = 'N/A';
                document.getElementById('latest-commit-date').textContent = 'N/A';
            }
        })
        .catch(error => {
            console.error('Error loading latest commit:', error);
            document.getElementById('latest-commit-message').textContent = 'Error loading commit';
            document.getElementById('latest-commit-hash').textContent = 'N/A';
            document.getElementById('latest-commit-date').textContent = 'N/A';
        });
}

function loadFiles(path) {
    showLoading(true);
    
    const url = path ? `/api/files?path=${encodeURIComponent(path)}` : '/api/files';
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            currentPath = path;
            currentFiles = data.files || [];
            allFiles = [...currentFiles];
            
            if (data.commit) {
                latestCommitInfo = data.commit;
            }
            
            filterAndDisplayFiles();
            updateBreadcrumb(path);
            showFileList();
            showLoading(false);
        })
        .catch(error => {
            console.error('Error loading files:', error);
            showNotification('Error loading files', 'error');
            showLoading(false);
        });
}

function filterAndDisplayFiles() {
    let filtered = [...allFiles];
    
    if (searchQuery) {
        filtered = filtered.filter(file => 
            file.name.toLowerCase().includes(searchQuery)
        );
    }
    
    if (currentFilter !== 'all') {
        filtered = filtered.filter(file => {
            if (file.type === 'tree') return true;
            const fileType = getFileType(file.name);
            return fileType === currentFilter;
        });
    }
    
    displayFiles(filtered);
    updateFileCount(filtered.length);
}

function getFileIcon(fileName, isDirectory) {
    if (isDirectory) {
        return '<i class="fa-solid fa-folder"></i>';
    }
    
    const ext = fileName.toLowerCase().split('.').pop();
    const iconClass = fileIconMap[ext] || fileIconMap[fileName.toLowerCase()] || 'fa-solid fa-file';
    return `<i class="${iconClass}"></i>`;
}

function displayFiles(files) {
    const tableBody = document.getElementById('file-table-body');
    tableBody.innerHTML = '';

    // Sort: directories first, then files alphabetically
    const sortedFiles = [...files].sort((a, b) => {
        if (a.type === 'tree' && b.type !== 'tree') return -1;
        if (a.type !== 'tree' && b.type === 'tree') return 1;
        return a.name.localeCompare(b.name);
    });

    sortedFiles.forEach((file, index) => {
        const row = document.createElement('tr');
        const isDirectory = file.type === 'tree';
        
        let commitMessage, commitDate;
        
        if (file.commit_message) {
            commitMessage = file.commit_message;
            commitDate = formatCommitDate(file.commit_date);
        } else {
            commitMessage = 'Loading...';
            commitDate = 'Loading...';
        }
        
        row.innerHTML = `
            <td>
                <div class="file-row-name" onclick="handleFileClick('${escapeHtml(file.name)}', ${isDirectory})">
                    <div class="file-row-icon ${isDirectory ? 'folder' : 'file'}">
                        ${getFileIcon(file.name, isDirectory)}
                    </div>
                    <span class="file-row-text">${escapeHtml(file.name)}</span>
                </div>
            </td>
            <td>
                <div class="file-commit-message">
                    ${escapeHtml(commitMessage)}
                </div>
            </td>
            <td>
                <div class="file-commit-date">
                    ${commitDate}
                </div>
            </td>
        `;
        
        // Stagger animation
        row.style.animation = `fadeInRow 0.3s ease ${index * 0.02}s both`;
        tableBody.appendChild(row);
    });
}

function updateFileCount(count) {
    document.getElementById('file-count').textContent = `${count} ${count === 1 ? 'item' : 'items'}`;
}

function handleFileClick(fileName, isDirectory) {
    if (isDirectory) {
        navigationHistory.push(currentPath);
        const newPath = currentPath ? `${currentPath}/${fileName}` : fileName;
        loadFiles(newPath);
        
        const backButton = document.getElementById('back-button');
        if (backButton) {
            backButton.style.display = 'flex';
        }
    } else {
        viewFile(fileName);
    }
}

function viewFile(fileName) {
    const fullPath = currentPath ? `${currentPath}/${fileName}` : fileName;
    
    showLoading(true);
    
    fetch(`/api/file?path=${encodeURIComponent(fullPath)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            showFileViewer(fileName, data.content, data.size, data.type);
            showLoading(false);
        })
        .catch(error => {
            console.error('Error loading file:', error);
            showNotification('Error loading file', 'error');
            showLoading(false);
        });
}

function showFileViewer(fileName, content, size, fileType) {
    document.querySelector('.file-browser').style.display = 'none';
    const fileViewer = document.getElementById('file-viewer');
    fileViewer.style.display = 'block';
    
    document.getElementById('file-path').textContent = fileName;
    
    const sizeKB = (size / 1024).toFixed(1);
    const lines = content ? content.split('\n').length : 0;
    document.getElementById('file-stats').innerHTML = `
        <span class="stat-badge"><i class="fa-solid fa-weight-hanging"></i> ${sizeKB} KB</span>
        <span class="stat-separator">•</span>
        <span class="stat-badge"><i class="fa-solid fa-list-ol"></i> ${lines} lines</span>
    `;
    
    const contentDiv = document.getElementById('file-content');
    
    if (fileType === 'binary' || isBinaryFile(fileName)) {
        contentDiv.innerHTML = `
            <div class="binary-file-display">
                <div class="binary-icon">
                    <i class="fa-solid fa-file-circle-question"></i>
                </div>
                <div class="binary-info">
                    <h3>Binary File</h3>
                    <p>${escapeHtml(fileName)}</p>
                    <p class="file-size">${(size / 1024).toFixed(1)} KB</p>
                    <p class="binary-note">This file cannot be displayed in the browser</p>
                </div>
            </div>
        `;
    } else if (isImageFile(fileName)) {
        contentDiv.innerHTML = `
            <div class="image-preview">
                <img src="data:image/${getImageType(fileName)};base64,${btoa(content)}" alt="${escapeHtml(fileName)}">
            </div>
        `;
    } else if (content) {
        const lines = content.split('\n');
        const lineNumbers = lines.map((_, index) => `<div class="line-number">${index + 1}</div>`).join('');
        
        const language = getLanguageFromFileName(fileName);
        let highlightedCode = escapeHtml(content);
        
        if (window.Prism && language && Prism.languages[language]) {
            highlightedCode = Prism.highlight(content, Prism.languages[language], language);
        }
        
        contentDiv.innerHTML = `
            <div class="code-viewer-wrapper">
                <div class="code-actions">
                    <button onclick="copyCodeToClipboard()" class="copy-code-btn" title="Copy to clipboard">
                        <i class="fa-solid fa-copy"></i>
                        <span>Copy</span>
                    </button>
                </div>
                <div class="line-numbers-wrapper">
                    <div class="line-numbers">${lineNumbers}</div>
                    <pre class="code-content language-${language}"><code>${highlightedCode}</code></pre>
                </div>
            </div>
        `;
        
        // Store content for copy function
        window.currentFileContent = content;
    } else {
        contentDiv.innerHTML = `
            <div class="empty-file-display">
                <i class="fa-solid fa-file-slash"></i>
                <p>Empty file</p>
            </div>
        `;
    }
}

function copyCodeToClipboard() {
    if (window.currentFileContent) {
        navigator.clipboard.writeText(window.currentFileContent).then(() => {
            const btn = document.querySelector('.copy-code-btn');
            const originalContent = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-check"></i><span>Copied!</span>';
            btn.classList.add('copied');
            
            setTimeout(() => {
                btn.innerHTML = originalContent;
                btn.classList.remove('copied');
            }, 2000);
            
            showNotification('Code copied to clipboard!', 'success');
        }).catch(err => {
            showNotification('Failed to copy code', 'error');
        });
    }
}

function showFileList() {
    document.querySelector('.file-browser').style.display = 'block';
    document.getElementById('file-viewer').style.display = 'none';
}

function goBack() {
    if (navigationHistory.length > 0) {
        const previousPath = navigationHistory.pop();
        searchQuery = '';
        document.getElementById('file-search').value = '';
        document.getElementById('clear-search').style.display = 'none';
        loadFiles(previousPath);
        
        if (navigationHistory.length === 0) {
            const backButton = document.getElementById('back-button');
            if (backButton) {
                backButton.style.display = 'none';
            }
        }
    }
}

function getFileType(fileName) {
    const ext = fileName.toLowerCase().split('.').pop();
    
    const codeExts = ['js', 'ts', 'jsx', 'tsx', 'py', 'java', 'cpp', 'c', 'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt'];
    const docExts = ['md', 'txt', 'pdf', 'doc', 'docx', 'json', 'yaml', 'yml', 'xml', 'csv'];
    const mediaExts = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'mp4', 'mp3', 'wav', 'avi'];
    
    if (codeExts.includes(ext)) return 'code';
    if (docExts.includes(ext)) return 'docs';
    if (mediaExts.includes(ext)) return 'media';
    
    return 'all';
}

function toggleShortcuts() {
    const overlay = document.getElementById('shortcuts-overlay');
    overlay.classList.toggle('show');
}

function updateBreadcrumb(path) {
    const breadcrumb = document.getElementById('breadcrumb');
    const pathParts = path ? path.split('/') : [];
    
    let breadcrumbHTML = `
        <span class="breadcrumb-item root">
            <i class="fa-solid fa-house"></i>
            <span class="breadcrumb-text" onclick="loadFiles('')">Repository</span>
        </span>
    `;
    
    let currentPath = '';
    pathParts.forEach((part, index) => {
        currentPath += (currentPath ? '/' : '') + part;
        const isLast = index === pathParts.length - 1;
        const escapedPath = currentPath.replace(/'/g, '\\\'');
        
        breadcrumbHTML += `
            <span class="breadcrumb-item ${isLast ? 'active' : ''}">
                <span class="breadcrumb-text" onclick="loadFiles('${escapedPath}')">${escapeHtml(part)}</span>
            </span>
        `;
    });
    
    breadcrumb.innerHTML = breadcrumbHTML;
}

function isImageFile(fileName) {
    const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'];
    return imageExtensions.some(ext => fileName.toLowerCase().endsWith(ext));
}

function getImageType(fileName) {
    const ext = fileName.toLowerCase().split('.').pop();
    return ext === 'jpg' ? 'jpeg' : ext;
}

function isBinaryFile(fileName) {
    const binaryExtensions = ['.exe', '.bin', '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z', '.deb', '.rpm'];
    return binaryExtensions.some(ext => fileName.toLowerCase().endsWith(ext));
}

function getLanguageFromFileName(fileName) {
    const ext = fileName.toLowerCase().split('.').pop();
    const languageMap = {
        'js': 'javascript',
        'ts': 'typescript',
        'jsx': 'javascript',
        'tsx': 'typescript',
        'py': 'python',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'sh': 'bash',
        'bash': 'bash',
        'zsh': 'bash',
        'fish': 'bash',
        'ps1': 'powershell',
        'html': 'markup',
        'xml': 'markup',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'less': 'less',
        'json': 'json',
        'yaml': 'yaml',
        'yml': 'yaml',
        'toml': 'toml',
        'ini': 'ini',
        'cfg': 'ini',
        'conf': 'nginx',
        'sql': 'sql',
        'md': 'markdown',
        'tex': 'latex',
        'r': 'r',
        'matlab': 'matlab',
        'm': 'matlab'
    };
    return languageMap[ext] || 'text';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function switchTab(tabName) {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const tabContent = document.getElementById(`${tabName}-tab`);
    tabContent.classList.add('active');
    
    if (tabName === 'commits') {
        loadCommits();
    }
}

function loadCommits() {
    showLoading(true);
    
    fetch('/api/commits')
        .then(response => response.json())
        .then(data => {
            displayCommits(data.commits || []);
            showLoading(false);
        })
        .catch(error => {
            console.error('Error loading commits:', error);
            displayCommitsError('Failed to load commits. Please try again.');
            showLoading(false);
        });
}

function displayCommits(commits) {
    const commitsList = document.getElementById('commits-list');
    commitsList.innerHTML = '';
    
    if (!commits || commits.length === 0) {
        commitsList.innerHTML = `
            <div class="empty-commits">
                <i class="fa-solid fa-code-commit"></i>
                <p>No commits found in this repository</p>
            </div>
        `;
        return;
    }
    
    commits.forEach((commit, index) => {
        const commitItem = document.createElement('div');
        commitItem.className = 'commit-item';
        commitItem.style.animation = `fadeInRow 0.3s ease ${index * 0.05}s both`;
        
        const shortSha = commit.sha ? commit.sha.substring(0, 7) : 'N/A';
        const message = commit.message || 'No commit message';
        const author = commit.author || 'Unknown';
        const date = commit.timestamp ? formatDate(commit.timestamp) : 'Unknown date';
        const initials = getInitials(author);
        
        commitItem.innerHTML = `
            <div class="commit-avatar" title="${escapeHtml(author)}">
                ${initials}
            </div>
            <div class="commit-info">
                <div class="commit-title">${escapeHtml(message)}</div>
                <div class="commit-meta">
                    <span class="commit-author">
                        <i class="fa-solid fa-user"></i>
                        ${escapeHtml(author)}
                    </span>
                    <span class="commit-separator">•</span>
                    <span class="commit-sha" title="${commit.sha || 'N/A'}">${shortSha}</span>
                    <span class="commit-separator">•</span>
                    <span class="commit-date">
                        <i class="fa-solid fa-clock"></i>
                        ${date}
                    </span>
                </div>
            </div>
        `;
        
        commitsList.appendChild(commitItem);
    });
}

function getInitials(name) {
    if (!name) return 'U';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
}

function displayCommitsError(message) {
    const commitsList = document.getElementById('commits-list');
    commitsList.innerHTML = `
        <div class="commits-error">
            <i class="fa-solid fa-exclamation-triangle"></i>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

function formatDate(timestamp) {
    try {
        let date;
        if (typeof timestamp === 'string') {
            date = new Date(timestamp);
        } else if (typeof timestamp === 'number') {
            date = new Date(timestamp * 1000);
        } else {
            return 'Invalid date';
        }
        
        if (isNaN(date.getTime())) {
            return 'Invalid date';
        }
        
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Invalid date';
    }
}

function formatCommitDate(timestamp) {
    try {
        if (!timestamp) return 'unknown';
        
        let date;
        if (typeof timestamp === 'string') {
            date = new Date(timestamp);
        } else if (typeof timestamp === 'number') {
            date = new Date(timestamp * 1000);
        } else {
            return 'unknown';
        }
        
        if (isNaN(date.getTime())) {
            return 'unknown';
        }
        
        const now = new Date();
        const diffMs = now - date;
        const diffSeconds = Math.floor(diffMs / 1000);
        const diffMinutes = Math.floor(diffSeconds / 60);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffDays === 0) {
            if (diffMinutes < 1) return 'now';
            if (diffMinutes < 60) return diffMinutes === 1 ? '1 minute ago' : `${diffMinutes} minutes ago`;
            return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
        } else if (diffDays === 1) {
            return 'yesterday';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            return weeks === 1 ? '1 week ago' : `${weeks} weeks ago`;
        } else if (diffDays < 365) {
            const months = Math.floor(diffDays / 30);
            return months === 1 ? '1 month ago' : `${months} months ago`;
        } else {
            const years = Math.floor(diffDays / 365);
            return years === 1 ? '1 year ago' : `${years} years ago`;
        }
    } catch (error) {
        return 'unknown';
    }
}
