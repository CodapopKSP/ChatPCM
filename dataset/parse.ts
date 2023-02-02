//Read two JSON files containing arrays of comments and parse their contents into a .txt file
//Run with Deno
import emojiStrip from "npm:emoji-strip"
import he from "npm:he"

interface Comment {
    comment_author: string,
    comment: string,
    reply_author: string,
    reply: string,
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
async function writeFile(filePath: string, commentSequence: string) {
    try {
        await Deno.writeTextFile(filePath, commentSequence, {
            append: true,
        });
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
function stringifyComments(comment: Comment) {
    let out: string;

    try {
        if (isNull(comment.comment)) { //Only save the reply
            out = `///////////////\n${purge(comment.reply)}\n`;

        } else if (isNull(comment.reply)) {//Only save the parent
            out = `///////////////\n${purge(comment.comment)}\n`;

        } else { //Save both the parent and the reply
            out = `///////////////\n${purge(comment.comment)}\n===============\n${purge(comment.reply)}\n`;


        }

        return out;
    } catch (e) {
        console.log(e.message)
        return "";
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
    // deno-lint-ignore no-invalid-regexp
    const emojiRE = /\p{EPres}|\p{ExtPict}/gu;
    const brailleRE = /\p{Script=Braille}/ug;

    str = he.decode(str);   //Remove HTML artifacts
    str = str.replace(emojiRE, ''); //Remove emojis (first pass, toughest)
    str = str.replace(brailleRE, '•'); //Remove braille dots
    str = str.replace(/\n\n/gm, '\n').trim();  //Remove new lines
    return emojiStrip(str);//Remove emojis (second pass)
}

//Write a unique filename
function DESTINATION(fileNum: number) {
    return `./output/dataset${fileNum}.txt`;
}



//Read, stringify and write a JSON file containing an array of Comments
async function parse(sourcePath: string, fileNum: number) {
    console.log('Opening file\n');
    const commentsArr: Comment[] = await readFile(sourcePath);

    console.log('Iterating file\n');
    let i = 0;
    const total = commentsArr.length;

    for (const comment of commentsArr) {
        try {
            if (i % TOKEN === 0) {
                fileNum++;  //Create a new file every TOKEN processed comment pairs
                console.log('\nGenerating new file:', fileNum, '\n');
            }

            await writeFile(DESTINATION(fileNum), stringifyComments(comment));
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
