import { createServer } from 'http'
import Consul from 'consul'
import portfinder from 'portfinder'
import { nanoid } from 'nanoid'

const serviceType = process.argv[2];
const { pid } = process;

async function main() {
  const consul = new Consul({
    host: '127.0.0.1',
    port: 8500
  });

  const port = await portfinder.getPortPromise();
  const address = '127.0.0.1';
  const serviceId = nanoid();

  const server = createServer((req, res) => {
    let i = 1e7; while (i > 0) i--;
    res.end(`${serviceType} response from pid: ${pid}\n`);
  });

  server.listen(port, address, () => {
    console.log(`Started ${serviceType} on ${address}:${port}, pid: ${pid}`);

    consul.agent.service.register({
      id: serviceId,
      name: serviceType,
      address,
      port,
      check: {
        http: `http://${address}:${port}`,
        interval: '5s'
      }
    }, (err) => {
      if (err) console.error('注册失败', err);
      else console.log('✅ 已注册到 Consul');
    });
  });

  process.on('SIGINT', () => {
    consul.agent.service.deregister(serviceId, () => {
      console.log('\n🛑 已注销服务');
      process.exit(0);
    });
  });
}

main().catch(console.error);