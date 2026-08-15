import { createServer } from 'http'
import staticHandler from 'serve-handler'
import { WebSocketServer, WebSocket  } from 'ws';
import yargs from 'yargs';
import zmq from 'zeromq'
import { hideBin } from 'yargs/helpers'

const server = createServer((req, res) => {
    return staticHandler(req, res, {public: 'www'})
})

let pubSocket

const argv = yargs(hideBin(process.argv)).parse()



async function initializeSockets () {
    pubSocket = new zmq.Publisher();
    await pubSocket.bind(`tcp://127.0.0.1:${argv.pub}`)

    const subSocket = new zmq.Subscriber();
    const subPorts = [].concat(argv.sub)
    for(const port of subPorts){
        console.log(`Subscribing to ${port}`)
        subSocket.connect(`tcp://127.0.0.1:${port}`)
    }
    subSocket.subscribe('chat')

    for await (const [msg] of subSocket){
        console.log(`Message from another server: ${msg}`)
        broadcast(msg.toString().split(' ')[1])
    }
}

initializeSockets()

const wss = new WebSocketServer({server});
wss.on('connection', client => {
    console.log('Client connected')
    client.on('message', msg => {
        console.log(`Message: ${msg}`)
        broadcast(msg)
        pubSocket.send(`chat ${msg}`)
    })
})

function broadcast(msg){
    for(const client of wss.clients){
       if(client.readyState === WebSocket.OPEN){
            client.send(msg);
        }
    }
}

// 之后使用 argv.http
server.listen(argv.http || 8080)