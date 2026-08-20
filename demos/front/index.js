const sleep = (ms) => new Promise((resolve) => {
    setTimeout(resolve, ms)
})

async function demo(){
console.time('标记名')
await sleep(4000)
console.timeEnd('标记名')
}




function* sleepGen(ms){
    yield new Promise(resolve => setTimeout(resolve, ms))
}

async function sleep2(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

function sleepSync(ms){
    const end = Date.now() + ms;
    while(Date.now() < end){}
}

function run(){
    demo();
    sleepGen(1000);
    sleep2(1000)
    sleepSync(1000)
}

run();

console.log('endd')