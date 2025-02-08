// 创建仓库相关的功能
let createRepoModal = null;

// 删除仓库相关
let deleteRepoModal = null;

// 编辑仓库相关
let editRepoModal = null;

// 克隆仓库相关
let cloneRepoModal = null;

// 文件浏览相关
let fileExplorerModal = null;
let currentRepo = null;
let currentPath = '';

// 仓库名称验证规则
const repoNamePattern = /^[a-zA-Z0-9.][a-zA-Z0-9._-]{1,190}$/;

// 删除文件相关
let deleteFileModal = null;

// 上传文件相关
let uploadFileModal = null;

document.addEventListener('DOMContentLoaded', function() {
    createRepoModal = new bootstrap.Modal(document.getElementById('createRepoModal'));
    deleteRepoModal = new bootstrap.Modal(document.getElementById('deleteRepoModal'));
    editRepoModal = new bootstrap.Modal(document.getElementById('editRepoModal'));
    cloneRepoModal = new bootstrap.Modal(document.getElementById('cloneRepoModal'));
    fileExplorerModal = new bootstrap.Modal(document.getElementById('fileExplorerModal'));
    deleteFileModal = new bootstrap.Modal(document.getElementById('deleteFileModal'));
    uploadFileModal = new bootstrap.Modal(document.getElementById('uploadFileModal'));
});

function showCreateRepoModal(platform) {
    document.getElementById('platformType').value = platform;
    // 清空表单
    document.getElementById('repoName').value = '';
    document.getElementById('repoDesc').value = '';
    document.getElementById('repoPrivate').checked = false;
    document.getElementById('initReadme').checked = false;
    document.getElementById('syncCreate').checked = false;
    createRepoModal.show();
}

// 验证仓库名称
function validateRepoName(name) {
    if (!repoNamePattern.test(name)) {
        return {
            valid: false,
            message: '仓库名称必须：\n' +
                    '1. 以字母、数字或点(.)开头\n' +
                    '2. 只能包含字母、数字、下划线(_)、中划线(-)、英文句号(.)\n' +
                    '3. 长度为2~191个字符'
        };
    }
    return { valid: true };
}

async function createRepository() {
    const platform = document.getElementById('platformType').value;
    const name = document.getElementById('repoName').value;
    
    // 验证仓库名称
    const validation = validateRepoName(name);
    if (!validation.valid) {
        alert(validation.message);
        return;
    }

    const description = document.getElementById('repoDesc').value;
    const isPrivate = document.getElementById('repoPrivate').checked;
    const initReadme = document.getElementById('initReadme').checked;
    const syncCreate = document.getElementById('syncCreate').checked;

    try {
        const response = await fetch('/api/repos/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                platform,
                name,
                description,
                private: isPrivate,
                init_readme: initReadme,
                sync_create: syncCreate
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('仓库创建成功！\n' + result.message);
            createRepoModal.hide();
            // 刷新仓库列表
            refreshGithubRepos();
            refreshGiteeRepos();
        } else {
            alert('创建失败: ' + result.message);
        }
    } catch (error) {
        alert('创建仓库时出错: ' + error);
    }
}

function showDeleteRepoModal(platform, repoId, repoName) {
    document.getElementById('deletePlatform').value = platform;
    document.getElementById('deleteRepoId').value = repoId;
    document.getElementById('deleteRepoName').value = repoName;
    document.getElementById('confirmRepoName').textContent = repoName;
    document.getElementById('syncDelete').checked = false;
    deleteRepoModal.show();
}

async function deleteRepository() {
    const platform = document.getElementById('deletePlatform').value;
    const repoId = document.getElementById('deleteRepoId').value;
    const repoName = document.getElementById('deleteRepoName').value;
    const syncDelete = document.getElementById('syncDelete').checked;

    // 添加二次确认
    const confirmMessage = `确定要删除仓库 "${repoName}" 吗？\n` + 
        (syncDelete ? '同时会删除另一个平台的同名仓库（如果存在）。' : '');
    if (!confirm(confirmMessage)) {
        return;
    }

    try {
        const response = await fetch('/api/repos/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                platform,
                repo_id: repoId,
                repo_name: repoName,
                sync_delete: syncDelete
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('仓库删除成功！\n' + result.message);
            deleteRepoModal.hide();
            // 刷新仓库列表
            refreshGithubRepos();
            refreshGiteeRepos();
        } else {
            alert('删除失败: ' + result.message);
        }
    } catch (error) {
        alert('删除仓库时出错: ' + error);
    }
}

function showEditRepoModal(platform, repoId, repoName, description, isPrivate, hasIssues, hasWiki, hasProjects) {
    document.getElementById('editPlatform').value = platform;
    document.getElementById('editRepoId').value = repoId;
    document.getElementById('editOldRepoName').value = repoName;
    document.getElementById('editRepoName').value = repoName;
    document.getElementById('editRepoDesc').value = description;
    document.getElementById('editRepoPrivate').checked = isPrivate;
    document.getElementById('editHasIssues').checked = hasIssues;
    document.getElementById('editHasWiki').checked = hasWiki;
    document.getElementById('editHasProjects').checked = hasProjects;
    document.getElementById('syncEdit').checked = false;
    editRepoModal.show();
}

async function updateRepository() {
    const platform = document.getElementById('editPlatform').value;
    const repoId = document.getElementById('editRepoId').value;
    const oldRepoName = document.getElementById('editOldRepoName').value;
    const repoName = document.getElementById('editRepoName').value;
    
    // 如果仓库名称有改动，进行验证
    if (repoName !== oldRepoName) {
        const validation = validateRepoName(repoName);
        if (!validation.valid) {
            alert(validation.message);
            return;
        }
        
        // 添加 Gitee 特殊提示
        if (platform === 'gitee') {
            if (!confirm(`确定要将仓库名称从 "${oldRepoName}" 改为 "${repoName}" 吗？\n注意：这将同时修改仓库的访问路径。`)) {
                return;
            }
        } else {
            if (!confirm(`确定要将仓库名称从 "${oldRepoName}" 改为 "${repoName}" 吗？\n这可能会影响到现有的克隆URL。`)) {
                return;
            }
        }
    }

    const description = document.getElementById('editRepoDesc').value;
    const isPrivate = document.getElementById('editRepoPrivate').checked;
    const hasIssues = document.getElementById('editHasIssues').checked;
    const hasWiki = document.getElementById('editHasWiki').checked;
    const hasProjects = document.getElementById('editHasProjects').checked;
    const syncEdit = document.getElementById('syncEdit').checked;

    try {
        const response = await fetch('/api/repos/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                platform,
                repo_id: repoId,
                old_repo_name: oldRepoName,
                repo_name: repoName,
                description,
                private: isPrivate,
                has_issues: hasIssues,
                has_wiki: hasWiki,
                has_projects: hasProjects,
                sync_edit: syncEdit
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('仓库设置更新成功！\n' + result.message);
            editRepoModal.hide();
            // 刷新仓库列表
            refreshGithubRepos();
            refreshGiteeRepos();
        } else {
            alert('更新失败: ' + result.message);
        }
    } catch (error) {
        alert('更新仓库设置时出错: ' + error);
    }
}

function showCloneRepoModal(platform, repoName, httpsUrl, sshUrl, zipUrl) {
    document.getElementById('httpsCloneUrl').value = httpsUrl;
    document.getElementById('sshCloneUrl').value = sshUrl;
    document.getElementById('downloadZipUrl').href = zipUrl;
    cloneRepoModal.show();
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    document.execCommand('copy');
    
    // 显示复制成功提示
    const button = element.nextElementSibling;
    const originalHtml = button.innerHTML;
    button.innerHTML = '<i class="bi bi-check"></i>';
    setTimeout(() => {
        button.innerHTML = originalHtml;
    }, 2000);
}

function showFileExplorer(platform, repoName) {
    currentRepo = { platform, name: repoName };
    currentPath = '';
    document.getElementById('repoNameTitle').textContent = repoName;
    loadFiles(platform, repoName, '');
    fileExplorerModal.show();
}

async function loadFiles(platform, repoName, path) {
    // 显示加载状态
    document.getElementById('fileList').innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
        </div>
    `;

    try {
        const response = await fetch(`/api/repos/files?platform=${platform}&repo=${repoName}&path=${path}`);
        const result = await response.json();
        
        if (result.success) {
            updateFileBreadcrumb(path);
            updateFileList(result.files);
            hideFileContent();
        } else {
            alert('加载文件列表失败: ' + result.message);
        }
    } catch (error) {
        alert('加载文件列表时出错: ' + error);
    }
}

function updateFileBreadcrumb(path) {
    const parts = path ? path.split('/') : [];
    let html = '<li class="breadcrumb-item"><a href="#" onclick="navigateToPath(\'\')">根目录</a></li>';
    
    let currentPath = '';
    parts.forEach((part, index) => {
        currentPath += (index === 0 ? '' : '/') + part;
        if (index === parts.length - 1) {
            html += `<li class="breadcrumb-item active">${part}</li>`;
        } else {
            html += `<li class="breadcrumb-item"><a href="#" onclick="navigateToPath('${currentPath}')">${part}</a></li>`;
        }
    });
    
    document.getElementById('fileBreadcrumb').innerHTML = html;
}

function updateFileList(files) {
    // 按类型和名称排序：文件夹在前，同类型按名称排序
    files.sort((a, b) => {
        if (a.type === b.type) {
            return a.name.localeCompare(b.name);
        }
        return a.type === 'dir' ? -1 : 1;
    });

    const listHtml = files.map(file => `
        <a href="#" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" 
            onclick="${file.type === 'dir' ? 
                     `navigateToPath('${currentPath}/${file.name}')` : 
                     `viewFile('${file.name}', '${file.path}')`}">
            <div>
                <i class="bi ${getFileIcon(file.name, file.type)} me-2"></i>
                ${file.name}
            </div>
            <div class="d-flex align-items-center">
                <span class="text-muted small me-3">
                    ${file.type === 'dir' ? 
                      '<i class="bi bi-folder"></i> 目录' : 
                      formatFileSize(file.size)}
                </span>
                <button class="btn btn-sm btn-outline-danger" 
                        onclick="event.stopPropagation(); showDeleteFileModal('${file.path}', '${file.name}', '${file.type}')"
                        title="删除${file.type === 'dir' ? '目录' : '文件'}">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </a>
    `).join('');
    
    document.getElementById('fileList').innerHTML = `<div class="list-group list-group-flush">${listHtml}</div>`;
}

// 根据文件扩展名返回对应的图标
function getFileIcon(filename, type) {
    if (type === 'dir') return 'bi-folder-fill text-warning';
    
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'js': 'bi-filetype-js text-warning',
        'py': 'bi-filetype-py text-primary',
        'html': 'bi-filetype-html text-danger',
        'css': 'bi-filetype-css text-info',
        'md': 'bi-markdown text-success',
        'json': 'bi-filetype-json text-success',
        'jpg': 'bi-file-image text-primary',
        'png': 'bi-file-image text-primary',
        'gif': 'bi-file-image text-primary'
    };
    
    return iconMap[ext] || 'bi-file-text';
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    // 小于1KB显示字节数，否则保留一位小数
    const size = bytes / Math.pow(k, i);
    return i === 0 ? 
        `${bytes} ${sizes[i]}` : 
        `${size.toFixed(1)} ${sizes[i]}`;
}

// 文件搜索功能
function filterFiles() {
    const searchText = document.getElementById('fileSearch').value.toLowerCase();
    const items = document.querySelectorAll('#fileList .list-group-item');
    
    items.forEach(item => {
        const fileName = item.querySelector('div').textContent.trim().toLowerCase();
        item.style.display = fileName.includes(searchText) ? '' : 'none';
    });
}

// 刷新当前目录
function refreshCurrentPath() {
    loadFiles(currentRepo.platform, currentRepo.name, currentPath);
}

function navigateToPath(path) {
    currentPath = path;
    loadFiles(currentRepo.platform, currentRepo.name, path);
}

async function viewFile(fileName, filePath) {
    try {
        const response = await fetch(`/api/repos/file-content?platform=${currentRepo.platform}&repo=${currentRepo.name}&path=${filePath}`);
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('fileContentTitle').textContent = fileName;
            const codeElement = document.getElementById('fileContentCode');
            codeElement.textContent = result.content;
            // 根据文件扩展名设置语言
            const ext = fileName.split('.').pop().toLowerCase();
            if (ext) {
                codeElement.className = `language-${ext}`;
            }
            // 应用语法高亮
            hljs.highlightElement(codeElement);
            document.getElementById('fileList').style.display = 'none';
            document.getElementById('fileContent').style.display = 'block';
        } else {
            alert('加载文件内容失败: ' + result.message);
        }
    } catch (error) {
        alert('加载文件内容时出错: ' + error);
    }
}

function hideFileContent() {
    document.getElementById('fileList').style.display = 'block';
    document.getElementById('fileContent').style.display = 'none';
}

function showDeleteFileModal(path, name, type) {
    document.getElementById('deleteFilePath').value = path;
    document.getElementById('deleteFileName').textContent = name;
    document.getElementById('deleteFileType').textContent = type === 'dir' ? '目录' : '文件';
    deleteFileModal.show();
}

async function deleteFile() {
    const path = document.getElementById('deleteFilePath').value;
    
    try {
        const response = await fetch('/api/repos/delete-file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                platform: currentRepo.platform,
                repo: currentRepo.name,
                path: path
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('删除成功！');
            deleteFileModal.hide();
            // 刷新当前目录
            loadFiles(currentRepo.platform, currentRepo.name, currentPath);
        } else {
            alert('删除失败: ' + result.message);
        }
    } catch (error) {
        alert('删除文件时出错: ' + error);
    }
}

function showUploadFileModal() {
    document.getElementById('fileInput').value = '';
    document.getElementById('commitMessage').value = '';
    document.getElementById('syncUpload').checked = false;
    uploadFileModal.show();
}

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert('请选择要上传的文件');
        return;
    }

    const commitMessage = document.getElementById('commitMessage').value;
    const syncUpload = document.getElementById('syncUpload').checked;

    // 读取文件内容
    const reader = new FileReader();
    reader.onload = async function(e) {
        const content = e.target.result.split(',')[1]; // 获取base64编码的内容
        const uploadPath = currentPath ? `${currentPath}/${file.name}` : file.name;

        try {
            const response = await fetch('/api/repos/upload-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    platform: currentRepo.platform,
                    repo: currentRepo.name,
                    path: uploadPath,
                    content: content,
                    message: commitMessage,
                    sync_upload: syncUpload
                })
            });

            const result = await response.json();
            if (result.success) {
                alert('文件上传成功！\n' + result.message);
                uploadFileModal.hide();
                // 刷新当前目录
                loadFiles(currentRepo.platform, currentRepo.name, currentPath);
            } else {
                alert('上传失败: ' + result.message);
            }
        } catch (error) {
            alert('上传文件时出错: ' + error);
        }
    };

    reader.readAsDataURL(file);
} 