# Building the dataset
## Objective
This collection of scripts aims at creating a dataset of multiple .json files of limited size and standard format
```json
{
    "comment": "string",
    "comment_author": "string",
    "reply": "string",
    "reply_author": "string"
}
```
Users should first select their target comments with some kind of criteria. We used the comments that received the most pills in the DataBased, the databse which powers [basedcount_bot](https://github.com/CodapopKSP/basedcount_bot) but other datasets could work equally fine. These comments will be the most prevalent in the resulting training dataset so pick them with care. This guide won't cover the creation of such a sample. It should look like this:
```json
{
    "body": "string",
    "id": "string",
    "parent_id": "string"
}
```
these are the fundamental fields, without which the script will not work. For richer datasets, users might want to include other fields by removing the commented lines in the "database.ts" script.

The instructions below explain how to build the training dataset by fetching the parent and children of these comments.
## Requirements
A starting **sample** of target comments, as explained in the [paragraph above](#objective).

An **archive** of Reddit comments. For this dataset we used a dump spanning from 2017 to 2022, kindly provided by the [Pushshift API](https://github.com/pushshift/api) team.

Such archive should be saved on a **MongoDB Server** instance running on the same machine as the script.

The TypeScript files "database.ts" and "parse.ts" should be executed with **Deno**.

## Steps
On MongoDB create a database named "historia". Save the archive of comments in a collection named "comments_pushshift" and the starting sample in another collection named "based_comments".

Run "database.ts" with `deno run --allow-all database.ts`. This will create a new collection named "based_comments_complete". The dataset is all there, now the only thing left is cleaning it up a bit to make it more digestible for the AI model.

Use the "children.mongodb" and "parents.mongodb" aggregation pipelines to create two .json files named  "children.json" and "parents.json", place these two files in a "dataset" folder. Create an empty folder named "output". This is where the resulting files will be saved.

By this point your project structure should look like this:
```
.
├── dataset/
│   ├── children.json
│   └── parents.json
├── output/
│   └── ..
├── children.mongodb
├── parents.mongodb
├── database.ts
├── parse.ts
└── README.md
```

Now run the "parse.ts" script with  `deno run --allow-all --allow-write parse.ts`. This will create multiple .json files in the output directory you just created. These files shouldn't be larger than 10KB and will contain exactly 30000 pairs of comment-reply sets. To modify this number edit the TOKEN variable in "parse.ts".

The model trainer doesn't seem to like emojis or weird unicode characters, so the resulting dataset will be limited to alphanumerical characters of the Latin alphabet (regional variations included) basic spacing and punctuation marks.