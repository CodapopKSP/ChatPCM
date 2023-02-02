//Fetch from Historia the names, children and parents of the most pilled comments. Used to train Deep Based
//Run with Deno
import { MongoClient } from 'npm:mongodb'
// import { MongoClient, ObjectId } from 'npm:mongodb'  //Replace with this if _id is included

interface BasedComment {
    // _id: ObjectId
    body: string
    // created_utc: number
    id: string
    // link_id: string    //This is useless
    parent_id: string   //If it starts with t3_ don't bother checking
    // pills: number  //Sort by this - not required
    // permalink: string   //This is useless
}

interface CompleteBasedComment extends BasedComment {
    author: string
    author_flair_text: string
    parent: FetchedComment | null
    children: FetchedComment[]
}

interface FetchedComment {
    author: string
    author_flair_text: string
    id: string
    body: string
    created_utc: number
}

interface self {
    author: string,
    author_flair_text: string
}

const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri);

await client.connect();
const based = client.db('historia').collection<BasedComment>('based_comments');
const comments = client.db('historia').collection('comments_pushshift');
const destination = client.db('historia').collection('based_comments_complete');


const basedComments = await based.find().toArray();
let i = 0;
const total = 166587;

for (const doc of basedComments) {
    try {
        console.log('Now processing:', doc.id)
        console.log('Fetching name and flair')
        const self = await comments.findOne<self>({ id: doc.id }, { projection: { _id: 0, author: 1, author_flair_text: 1 } });

        console.log('Fetching parent')
        let parent: FetchedComment | null
        if (doc.parent_id.match(new RegExp(/t1_.{7}/))) {
            console.log('\tParent found:', doc.parent_id)
            const parent_id_parsed = doc.parent_id.substring(3)
            parent = await comments.findOne<FetchedComment>({ id: parent_id_parsed }, { projection: { _id: 0, author: 1, author_flair_text: 1, id: 1, body: 1, created_utc: 1 } });
        } else {
            console.log('\tNo parent found')
            parent = null;
        }

        console.log('Fetching children')
        const id_as_parent = 't1_' + doc.id;
        const children = await comments.find<FetchedComment>({ parent_id: id_as_parent }, { projection: { _id: 0, author: 1, author_flair_text: 1, id: 1, body: 1, created_utc: 1 } }).toArray();

        console.log('Finished fetching, assembling')

        const final = {
            // _id: doc._id,
            body: doc.body,
            // created_utc: doc.created_utc,
            id: doc.id,
            // link_id: doc.link_id,
            parent_id: doc.parent_id,
            // pills: doc.pills,
            // permalink: doc.permalink,
            author: self?.author ?? '',
            author_flair_text: self?.author_flair_text ?? '',
            parent: parent,
            children: children
        } satisfies CompleteBasedComment;

        i++;
        console.log(`Pushing to database. ${i}/${total} ${(i / total * 100).toFixed(2)}%`)
        await destination.insertOne(final);

        console.log()
    } catch (error) {
        console.log(error)
    }

}

Deno.exit(0)
