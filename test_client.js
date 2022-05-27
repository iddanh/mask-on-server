const { WebSocket } = require('ws');

const ws = new WebSocket('wss://maskon.cs.colman.ac.il:10151/', { rejectUnauthorized: false });

ws.on('open', function open() {
    console.log("Connection with server established");
    ws.send('test message');
});

ws.on('message', function message(data) {
    console.log('received: %s', data);
});