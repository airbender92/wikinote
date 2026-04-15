// 当前目录下执行命令: node copyFileSync.cjs

const fs = require('fs');
const path = require('path');

const sourceFile = path.join(__dirname, '../../assets/source.txt');
const targetFile = path.join(__dirname, '../../dist/target.txt');

try{
    if(!fs.existsSync(sourceFile)){
        fs.writeFileSync(sourceFile, '这是一个测试文件, 用于测试fs.copyFileSync方法', 'utf8');
        console.log('✓ 创建测试文件成功: source.txt',);
    }
}catch(err){
    console.error('复制文件失败:', err);
}

try{
    fs.copyFileSync(sourceFile, targetFile);
    console.log('✓ 复制文件成功');
    console.log(`从 ${sourceFile} 复制到 ${targetFile}`);

    const targetContent = fs.readFileSync(targetFile, 'utf8');
    console.log('\n 目标文件内容：');
    console.log(targetContent);
}catch(err){
    console.error('复制文件失败:', err);
}
    
