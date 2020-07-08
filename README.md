# Home-made glamorous tools

This is a repo where I put non-related hacking tools I coded myself.

They are not meant to be generic tools ready for use in any situation. I was too lazy to make a proper UI and just modified the parameters in an icky hard-coded way whenever I needed to, since it was just for one CTF. This repo is mainly for myself, to keep track of my code, but feel free to use it and/or suggest improvements. It's always nice to work with fellow passionate noobs (if you're offended by this word look at my username.)

Coding the scripts in this repo was a lot of fun!

## dict_attack.py

This is an implementation of a multi-threaded distant dictionary attack. I used it for a CTF challenge, and I used the same words list (containing 1000000 entries) to find both the username and the password. 

The script reads all the file at once, and divides it in chunks. Each thread gets a chunk. Every thread makes web requests for the words in its chunk only (so no data sharing between threads). Whenever a thread finds the right word (gets a string different from the one provided as 'fail string' in the HTTP response) it signals it to all the others so they stop working. This approach is beneficial for two reasons:

- The time some threads spend idly waiting for a web response is used for other threads who are executing local instructions. Too few threads means your process is idle sometimes and that's a waste of time. Too many threads means it gets crowded and it's not so useful because threads end up waiting idly.
- If the word list is not ordered according to frequency (e.g. if it's in alphabetical order), how fast you find isn't extra long if the word is at the end of the list. It would still be a bummer if it's at the end of a words chunk though. But it will still be faster.

For me, threads somewhere between 30 and 45 were good. But make your own benchmarking on your machines AND take into consideration the web server's capabilities. You don't want to DoS it.

## enumerate_blind_sql.py

This is an implementation of a blind SQL distant timing attack. Although it works fine, I don't think you should use it instead of SQLMap. SQLMap does a lot more.

Anyway, here's what my implementation does:

1. In order to find the value of a field (username, password, etc.), it does a binary search to find the letter that goes in every position (length unkown)
2. It bases its decisions during the binary search on the duration of the response (SQL timing attack, duh).
3. When there is only one possible letter left for a given position, it is considered as the correct letter.
4. If no letters are left in an interval, the field is considered to be entirely figured out and that the end of the word has been reached
