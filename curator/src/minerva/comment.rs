use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Comment {
    pub body: String,
    pub id: String,
    pub link_id: String,
    pub permalink: String,
    pub created_utc: u32,
    pub author: String,
    pub flair: String,
}
