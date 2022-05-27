// const rootCas =  require('ssl-root-cas').create();
// rootCas.addFile(__dirname + '/cert/intermediate.pem');
// require('https').globalAgent.options.ca = rootCas;

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
        // Write img to disk
        const fileName = 'data.jpg';
        fs.writeFileSync(fileName, Buffer.from(data.toString().split(",")[1], 'base64'));

            // Send filename to python script
            pyshell.send(`${fileName}\n`);
    });

    pyshell.on('message', function (fileName) {
        try{
            // read binary data
            const bitmap = fs.readFileSync(fileName);
            // convert binary data to base64 encoded string
            const data = Buffer.from(bitmap).toString('base64');
            
            ws.send(data);
        } catch(e){
            console.log('Got error from pythong', fileName);
        }
    });

    // // end the input stream and allow the process to exit
    // pyshell.end(function (err) {
    //     if (err){
    //         console.log(err);
    //     };

    //     console.log('finished');
    // });
});

server.listen(10151);

console.log('Server running');