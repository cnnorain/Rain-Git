// GitHub仓库列表处理
socket.on('github_repos', (data) => {
    const githubReposDiv = document.getElementById('github-repos');
    const repos = data.repos;
    
    if (!repos || repos.length === 0) {
        githubReposDiv.innerHTML = '<div class="alert alert-info">没有找到GitHub仓库</div>';
        return;
    }
    
    const reposHtml = repos.map(repo => `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">
                    ${repo.name}
                    <small class="text-muted">
                        <i class="bi ${repo.private ? 'bi-eye-slash-fill text-danger' : 'bi-eye-fill text-success'}" 
                           title="${repo.private ? '私有仓库' : '公开仓库'}"></i>
                    </small>
                </h5>
                <p class="card-text">${repo.description || '暂无描述'}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-primary me-2">⭐ ${repo.stars}</span>
                        <span class="badge bg-secondary">🔄 ${repo.forks}</span>
                    </div>
                    <div>
                        <a href="${repo.html_url}" target="_blank" class="btn btn-sm btn-outline-primary">查看</a>
                        <button class="btn btn-sm btn-outline-secondary" onclick="showFileExplorer('github', '${repo.name}')">
                            <i class="bi bi-folder"></i> 文件
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" 
                                onclick="showCloneRepoModal('github', 
                                    '${repo.name}',
                                    '${repo.clone_url}',
                                    '${repo.ssh_url}',
                                    '${repo.html_url}/archive/refs/heads/${repo.default_branch}.zip')">
                            克隆
                        </button>
                        <button class="btn btn-sm btn-outline-info" 
                                onclick="showEditRepoModal('github', ${repo.id}, '${repo.name}', '${repo.description || ''}', ${repo.private})">
                            编辑
                        </button>
                        <button class="btn btn-sm btn-outline-success" 
                                onclick="refreshRepo('github', ${repo.id})">
                            刷新
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="showDeleteRepoModal('github', ${repo.id}, '${repo.name}')">
                            删除
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    githubReposDiv.innerHTML = reposHtml;
});

// 刷新仓库列表
function refreshGithubRepos() {
    socket.emit('refresh_repos');
}

// 其他GitHub相关的前端功能将在这里实现 