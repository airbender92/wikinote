var findAnagrams = function(s, p){
    const res = [];
    const count = new Array(26).fill(0);
    const aCode = 'a'.charCodeAt(0);
    const pLen = p.length;
    let diff = 0;
    for(const c  of p){
        count[c.charCodeAt(0)-aCode]--;
    }
    for(let num of count){
        if(num !== 0) diff++;
    }
    if(diff === 0) res.push(0);

    for(let i = pLen; i < s.length; i++){
        const inIdx = s.charCodeAt(i)-aCode;
        if(count[inIdx] === 0) diff++;
        count[inIdx]--;
        if(count[inIdx] === 0) diff--;

        const outIdx =
    }
}