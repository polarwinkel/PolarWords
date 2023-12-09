# PolarWords

A vocabulary, names and words learning server with multi-student and instructor accounts

## What is this

PolarWords is a server for learning and memorizing especially vicabulary, but also other words like names, tecnical or medical terms and so on.

It distinguishes from most other similar software in two parts:

- It is a server, so you can access your database from all your devices at the same time.
- It has separate instructor/tescher/parent and multiple student-accounts. The instructor can see the progress the students make in just one click.

## How can I install this

A small computer like a Raspberry Pi will do just fine. Clone this repository, install the dependencies, and run `app.py`. Then point your browser to the IP of the machine to port 5000 (default at the moment - will still change).

It is strongly advised to use encryption to access the PolVocab-Server to protect the admin-password and other data! You can i.e. use nginx as a reverse proxy with Let's Encrypt certificates.

### Dependencies

All dependencies can be installed on a debian-besed system with `apt install`, on other systems with pip:

- `python3`
- `python-flask`
- `python3-jinja2`
- `python3-yaml`
- `python3-flask-login`

## TODO

This is still in an alpha-state, some features are not implemented yet like editing accounts and other stuff.

But it is already useful in quite some cases, and since the database is an sqlite-db some hacks can be done by simply editing the database right in i.e. the SQLite-Browser.

Some ideas that I have for this project:

- change user-Accounts (i.e. set new password - would be easy to implement)
- allow external recources (i.e. images) as descriptions to learn the word for (prepared in the code already)
- allow multiple instructors (database itself has it implemented already)
    - add groups-support

## Contribute

If your like this: Spread the word, and give this project a star so I know it is being used. That might also be an incentive for me to implement some more ideas I still have for this project.

If you want to make translations please let me know.

You are very welcome to report any issues you find! If you have any suggestions, just let me know by sending an eMail or filing an issiue, we'll see what can be done.

You can also submit pull-requests if you like.
