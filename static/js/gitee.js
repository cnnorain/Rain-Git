// Gitee仓库列表处理
socket.on('gitee_repos', (data) => {
    console.log('收到Gitee仓库数据:', data);
    const giteeReposDiv = document.getElementById('gitee-repos');
    const repos = data.repos;
    
    if (!repos || repos.length === 0) {
        console.log('没有Gitee仓库数据');
        giteeReposDiv.innerHTML = '<div class="alert alert-info">没有找到Gitee仓库</div>';
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
                        <button class="btn btn-sm btn-outline-secondary" onclick="showFileExplorer('gitee', '${repo.name}')">
                            <i class="bi bi-folder"></i> 文件
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" 
                                onclick="showCloneRepoModal('gitee', 
                                    '${repo.name}',
                                    '${repo.clone_url}',
                                    '${repo.ssh_url}',
                                    '${repo.html_url}/repository/archive/${repo.default_branch}.zip')">
                            克隆
                        </button>
                        <button class="btn btn-sm btn-outline-info" 
                                onclick="showEditRepoModal('gitee', ${repo.id}, '${repo.name}', '${repo.description || ''}', ${repo.private})">
                            编辑
                        </button>
                        <button class="btn btn-sm btn-outline-success" 
                                onclick="refreshRepo('gitee', ${repo.id})">
                            刷新
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="showDeleteRepoModal('gitee', ${repo.id}, '${repo.name}')">
                            删除
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    console.log('生成的HTML:', reposHtml);
    giteeReposDiv.innerHTML = reposHtml;
});

// 刷新仓库列表
function refreshGiteeRepos() {
    console.log('请求刷新Gitee仓库列表');
    socket.emit('refresh_repos');
}

// 其他Gitee相关的前端功能将在这里实现 