const { WebSocketServer } = require('ws');
const https = require('https');
const fs = require("fs");
const { PythonShell } = require('python-shell');

server = https.createServer({
    pfx: fs.readFileSync('./cert/CSSTUD.pfx'),
    passphrase: 'Bamba@CS22'
})

const wss = new WebSocketServer({ server: server });

wss.on('connection', function connection(ws) {
    console.log('Connection established!')

    // Start python instance for each connection
    const pyshell = new PythonShell('VideoTransformer.py');

    ws.on('message', function message(data) {
        // Convert to string
        const stringData = data.toString().split(",")[1];

        // Send filename to python script
        pyshell.send(`${stringData}\n`);
    });

    pyshell.on('message', function (data) {
        try {
            
            // Skip errors
            if (data === '<class \'cv2.error\'>') {
                return;
            }

            // Remove unneeded chars and send to client
            ws.send(data.substring(2, data.length - 1));
        } catch(e) {
            console.log('Got error from python', fileName);
        }
    });
});

server.listen(10151);

console.log('Server running');