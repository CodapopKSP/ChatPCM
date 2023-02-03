use std::{env, path::Path};

mod minerva;

#[tokio::main]
async fn main() {
    let args: Vec<String> = env::args().collect();
    let import_target = args.get(1).expect("Please provide an argument pointing to a comments file.");
    let import_path = Path::new(import_target);
    if !import_path.exists() {
        panic!("I can't access that file. Maybe get good and try again?");
    }

    // I'm trying to figure out how the fuck I actually train this thing. So I can test my ranking algorithm I havne't written yet. 
}
