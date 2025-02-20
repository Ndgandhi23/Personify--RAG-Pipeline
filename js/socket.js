const socket = new WebSocket('ws://127.0.0.1:8081');

socket.onopen = function(event) {
    console.log('Connected to the WebSocket server.');
};

socket.onmessage = function(event) {
    console.log('Data received from server:', event.data);
    refreshApplicationGrid(event.data)
};
