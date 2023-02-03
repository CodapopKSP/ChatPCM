//Read two JSON files containing arrays of comments and parse their contents into a .txt file
//Run with Deno
// import emojiStrip from "npm:emoji-strip"
import he from "npm:he"

interface Comment {
    comment_author: string,
    comment: string,
    reply_author: string,
    reply: string,
}

class CommentOut {
    comment: string;
    reply: string;
    constructor(comment: string, reply: string) {
        this.comment = comment;
        this.reply = reply;
    }
}

const PARENTS = './datasets/parents.json';
const CHILDREN = './datasets/children.json';
const TOKEN = 30000;    //Number of comment pairs per file

//Reads a JSON file containing an array of Comments
async function readFile(filePath: string) {
    try {
        return JSON.parse(await Deno.readTextFile(filePath));
    } catch (e) {
        console.log(filePath + ': ' + e.message);
    }
}

//Appends a string to a file
async function writeFile(filePath: string, commentSequence: CommentOut[]) {
    const map = commentSequence.map(obj => {
        return { [obj.comment as string]: obj.reply }
    });
    const stringified = JSON.stringify(map);

    try {
        await Deno.writeTextFile(filePath, stringified);
    } catch (e) {
        console.log(e.message);
    }
}

/*Represents a comment as a string in the format: 
    Author:
    Body
    Reply_author:
    Reply_body
*/
function cleanComments(comment: Comment) {
    let out;

    try {
        if (isNull(comment.comment)) { //Only save the reply
            out = new CommentOut('', purge(comment.reply));

        } else if (isNull(comment.reply)) {//Only save the parent
            out = new CommentOut(purge(comment.comment), '');

        } else { //Save both the parent and the reply
            out = new CommentOut(purge(comment.comment), purge(comment.reply));

        }
        return out;
    } catch (e) {
        console.log(e.message)
        return new CommentOut('', '');
    }
}

//Returns true if the string is null, undefined, removed by reddit or deleted by the user
function isNull(str: string) {
    if (str === undefined) return true;
    if (str === null) return true;
    if (str === '') return true;
    if (str === '[deleted]') return true;
    if (str === '[removed]') return true;
    return false;
}

//Remove all line breaks from a string (they break our format), unescape escape sequences
function purge(str: string) {
    const whitelistRE = /[A-Za-z0-9À-ÿ!@#$%^&*()_+-={}[\]:";'<>,.?\/\\ (\r\n|\r|\n)]+/g;

    str = he.decode(str);   //Remove HTML artifacts
    const res = (str.match(whitelistRE) || []).join('');
    return res;
}

//Write a unique filename
function DESTINATION(fileNum: number) {
    return `./output/dataset${fileNum}.json`;
}



//Read, stringify and write a JSON file containing an array of Comments
async function parse(sourcePath: string, fileNum: number) {
    console.log('Opening file\n');
    const commentsArr: Comment[] = await readFile(sourcePath);

    console.log('Iterating file\n');
    let i = 0;
    const total = commentsArr.length;
    let arr: CommentOut[] = [];

    for (const comment of commentsArr) {
        try {
            if (i % TOKEN === 0 && i != 0) {//Create a new file every TOKEN processed comment pairs
                fileNum++;
                await writeFile(DESTINATION(fileNum), arr);
                arr = [];
                console.log('\nGenerating new file:', fileNum, '\n');
            }
            arr.push(cleanComments(comment));
            i++;
            console.log(`Comment inserted - ${(i / total * 100).toFixed(2)}%`);
        } catch (e) {
            console.log(e.message);
        }
    }
    console.log('\nFinished iterating file\n');
    return fileNum;
}


console.time()
console.log('Parents file\n');
let n = await parse(PARENTS, -1);
console.timeLog()
console.log('Children file\n');
n = await parse(CHILDREN, n);
console.timeEnd()
console.log('Done. Created', n + 1, 'files');


Deno.exit(0)
