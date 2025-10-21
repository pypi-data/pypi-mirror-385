use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::println;
use std::{env, process::Command};

fn main() {
    let out_dir = std::env::var("OUT_DIR").unwrap();
    let version = get_version_and_commit().unwrap_or(Version {
        tag: env!("CARGO_PKG_VERSION").into(),
        branch_commit: None,
    });
    let mut sli_version_file =
        fs::File::create(PathBuf::from(out_dir).join("sli_version.rs")).unwrap();
    if let Some(commit) = &version.branch_commit {
        writeln!(
            &mut sli_version_file,
            "pub static VERSION: &str = \"{}-{}-{}\";",
            version.tag, commit.branch, commit.commit,
        )
        .unwrap();
    } else {
        writeln!(
            &mut sli_version_file,
            "pub static VERSION: &str = \"{}\";",
            version.tag,
        )
        .unwrap();
    }
}

struct Version {
    tag: String,
    branch_commit: Option<BranchCommit>,
}

struct BranchCommit {
    branch: String,
    commit: String,
}

fn get_version_and_commit() -> Option<Version> {
    println!("cargo:rerun-if-changed=../../.git/HEAD");
    let tag = Command::new("git")
        .args(["describe", "--tags", "--abbrev=0"])
        .output()
        .ok()?;
    let tag = if tag.status.success() {
        String::from_utf8(tag.stdout).unwrap().trim().to_string()
    } else {
        "Unknown".to_string()
    };
    let commit = Command::new("git")
        .args(["rev-parse", "HEAD"])
        .output()
        .ok()?;
    let branch_commit = if !commit.status.success() {
        return None;
    } else {
        let commit = String::from_utf8(commit.stdout).unwrap().trim().to_string();
        let commit_tag = String::from_utf8(
            Command::new("git")
                .args(["describe", "--tags", "--abbrev=0", &commit])
                .output()
                .ok()?
                .stdout,
        )
        .ok()?
        .trim()
        .to_string();

        if commit_tag == tag {
            None
        } else {
            let branch = String::from_utf8(
                Command::new("git")
                    .args(["branch", "--show-current"])
                    .output()
                    .ok()?
                    .stdout,
            )
            .ok()?
            .trim()
            .to_string();
            Some(BranchCommit { branch, commit })
        }
    };
    Version { tag, branch_commit }.into()
}
