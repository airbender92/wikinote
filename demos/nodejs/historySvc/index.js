import { createServer } from 'http'
import { Level } from 'level'
import timestamp from 'monotonic-timestamp'
import JSONStream from 'JSONStream'
import amqp from 'amqplib'
import { Readable } from 'node:stream'

async function main(){
    const db = new Level('./msgHistory')
    const connection = await amqp.connect('amqp://127.0.0.1')
    const channel = await connection.createChannel();
    await channel.assertExchange('chat', 'fanout')

    const { queue } = await channel.assertQueue('chat_history')

    await channel.bindQueue(queue, 'chat')
    channel.consume(queue, async msg => {
        const content = msg.content.toString();
        console.log(`Saving message: ${content}`)
        await db.put(timestamp(), content)
        channel.ack(msg)
    })

    createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' })
  const iter = db.values()
  const readable = Readable.from(iter, { objectMode: true })
  readable
    .pipe(JSONStream.stringify())
    .pipe(res)
}).listen(8090)
}

main().catch(err => console.error(err))