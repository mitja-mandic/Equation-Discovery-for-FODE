---
title: "Become a Master of Supercomputing: Intensive HPC Training at FIS"
subTitle: "Workshop HPC in Practice I: From Linux to Containers"
language: "en"
tocInHeader: true
---

**Author:** Srdjan Skrbic  
**Email:** srdjan.skrbic@fis.unm.si  
**Affiliation:** Faculty of Information Studies in Novo mesto (FIS)

# Become a Master of Supercomputing: Intensive HPC Training at FIS
## Workshop HPC in Practice I: From Linux to Containers

### SESSION 1: Linux and Slurm - Your First Contact with HPC
Master the terminal, the entry point to all modern HPC clusters. You will learn navigation, file management, and writing automation scripts.

*   **Lecturer:** Srdjan Skrbic
*   **Email:** srdjan.skrbic@fis.unm.si
*   **Website:** skrbic.fis.unm.si

---

## The HPC Landscape

### You aren't on the supercomputer - you are in the lobby
*   **The Login Node:** Where you edit code and manage files. *(Don't run heavy code here!)*
*   **The Compute Nodes:** Where the heavy lifting happens.
*   **The Bridge:** `ssh username@hpc.university.edu`

> 💡 **Tip:** Think of the Login Node as the "Kitchen Office" and the Compute Nodes as the "Industrial Oven." You prepare the recipe in the office, but you cook in the oven.

---

## Where Am I?

*   `pwd`: Print Working Directory (Where am I right now?)
*   `whoami`: Confirm your identity.
*   `ls`: List files.
*   `ls -l`: Long format (shows permissions and size).
*   `ls -lh`: Human-readable (KB, MB, GB).
*   `ls -a`: Show hidden files (like `.bashrc` configs).

> 💡 **HPC Tip:** Use `ls -ltr` to list files by time, with the newest at the bottom. Great for finding the output file you just generated.

---

## Moving Around the Cluster

*   `cd <directory>`: Change directory.
*   `cd ..`: Move up one level.
*   `cd ~`: Go straight to your Home directory.
*   `cd -`: Jump back to the last directory you were in (the "Back" button).

### Common Paths:
*   `/home/user`: Small, backed up (for scripts).
*   `/data/project`: Shared with your team.
*   **Trdina Cluster:** `/ceph/projects`

---

## File Management

*   `mkdir project_name`: Create a folder.
*   `touch notes.txt`: Create an empty file.
*   `cp source.py destination.py`: Copy.
*   `mv old_name.sh new_name.sh`: Rename or move.
*   `rm file.txt`: Delete *(Careful: There is no "Trash Can" in Linux!)*

> 💡 **Tip:** Use `cp -r` to copy entire directories of dataset results.

---

## Peeking Inside

*   `cat file.txt`: Dump the whole file to the screen (bad for large files).
*   `head -n 20 file.txt`: See the first 20 lines.
*   `tail -n 20 file.txt`: See the last 20 lines.
*   `less file.txt`: Open in a scrollable viewer (Press `q` to exit).
*   `nano script.py`: The easiest text editor.

> 💡 **Tip:** Use `tail -f slurm-123.out` to watch your simulation output in real-time as it runs.

---

## Pipes and Power Searching

*   `grep "Error" log.txt`: Find every line containing the word "Error".
*   `wc -l file.txt`: Count the number of lines in a file.
*   **The Pipe (`|`):** Take the output of command A and feed it to command B.
    *   *Example:* `ls -l | grep "Aug" | wc -l`
*   **Redirection (`>`):** Save output to a file.
    *   *Example:* `grep "Finished" simulation.log > summary.txt`

---

## Permissions and Chmod

### The Breakdown
Linux tracks three types of access for every file:
*   **Read (r)**
*   **Write (w)**
*   **Execute (x)**

### The Players
*   `u` (User/You)
*   `g` (Group/Team)
*   `o` (Others/Everyone else)
*   `a` (All)

### The Command: `chmod` (Change Mode)
Common Use Cases:
*   `chmod +x script.sh`: "Add Execute" – Makes your script runnable.
*   `chmod g+w data.csv`: "Group plus Write" – Lets your lab partners edit your data.
*   `chmod o-rwx secret_dir/`: "Other minus everything" – Keeps everyone else out of your folder.

---

## Storage and Finding Files

*   HPC storage is huge, but your "quota" (limit) is not.
*   `du -sh *`: Disk Usage. Shows how much space each folder is taking up.
    *   *Why?* You need this when your job fails because your "Home" directory is 100% full.
*   `find . -name "*.csv"`: Search for files in the current folder and all subfolders.
    *   *Why?* When you have 10,000 simulation outputs, `ls` isn't enough.

---

## Help and History

Don't memorize everything; know how to look it up.
*   `man <command>`: The built-in Manual (e.g., `man grep`).
*   `<command> --help`: A shorter "cheat sheet" version of the manual.
*   `history`: Shows a list of every command you’ve typed.

> 💡 **Tip:** Type `history | grep "scp"` to find that complex transfer command you used three days ago.

---

## Automation – Bash Script

1. **Create the file:** `nano run_analysis.sh`
2. **Add the content:**
```bash
#!/bin/bash
# This is a comment
echo "Starting analysis at $(date)"
mkdir -p results
cp data/*.csv results/
echo "Analysis complete!"
