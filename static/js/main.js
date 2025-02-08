// WebSocket连接
const socket = io();

// WebSocket连接成功
socket.on('connect', () => {
    console.log('WebSocket connected');
    // 连接成功后主动请求仓库数据
    socket.emit('refresh_repos');
});

// WebSocket连接错误
socket.on('connect_error', (error) => {
    console.error('WebSocket connection error:', error);
});

// WebSocket断开连接
socket.on('disconnect', () => {
    console.log('WebSocket disconnected');
}); 