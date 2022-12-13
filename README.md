# pyYAHE

Yet Another HTTP Echo Server for debugging (no dependency)

Parse and print out incoming HTTP requests and its content to console, and always return HTTP200 with no body.

### Features 

0. Output is designed for human reading (for code simplicity)
1. Only python standard libraries are used
2. Very small ~kinda~ (131 lines @ 5k)
3. Can parse and format
  + `application/json`
  + `application/x-www-form-urlencoded`
  + `multipart/form-data` (actual payload are treaded as binary data)
4. have a hex dump for rest of the content type

Tested with Python 3.9 and Python 3.11, on Ubuntu 20.02 and Win10.

### Road map

~If I have time...~

- [ ] have optional color output support
- [ ] have more options but not increase "config boilerplate"
- [ ] write output to file
- [ ] try to make it work with https

## Example output

```log
Listening on 0.0.0.0:8000

----- Request Start ----->

* 127.0.0.1:6695 /url_is_unquote_here/see?url=https://github.com/kice/pyYAHE

> GET /url_is_unquote_here/see?url=https%3A%2F%2Fgithub.com%2Fkice%2FpyYAHE HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.86.0
> Accept: */*

<no body>
<----- Request End -----

127.0.0.1 - - [13/Dec/2022 10:37:10] "GET /url_is_unquote_here/see?url=https%3A%2F%2Fgithub.com%2Fkice%2FpyYAHE HTTP/1.1" 200 -

----- Request Start ----->

* 127.0.0.1:5925 /post_a_form

> POST /post_a_form HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.86.0
> Accept: */*
> Content-Length: 19
> Content-Type: application/x-www-form-urlencoded

hello: world
xxx: yyy

<----- Request End -----

127.0.0.1 - - [13/Dec/2022 10:22:11] "POST /post_a_form HTTP/1.1" 200 -

----- Request Start ----->

* 127.0.0.1:5930 /post_a_file

> POST /post_a_file HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.86.0
> Accept: */*
> Content-Length: 1995383
> Content-Type: multipart/form-data; boundary=------------------------9d4e4cef68afef3c
> Expect: 100-continue

> FormData 1:
Content-Disposition: form-data; name="file"; filename="1.png"
Content-Type: image/png
<binary data, len=1995104 (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\n\x00')>

> FormData 2:
Content-Disposition: form-data; name="test"
<binary data, len=4 (b'1234')>


<----- Request End -----

127.0.0.1 - - [13/Dec/2022 10:22:21] "POST /post_a_file HTTP/1.1" 200 -

----- Request Start ----->

* 127.0.0.1:6070 /here_is_a_hex_dump_as_well

> POST /here_is_a_hex_dump_as_well HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.86.0
> Accept: */*
> Content-Type: application/octet-stream
> Content-Length: 5203

<binary data, len=5203>
23 21 2F 75 73 72 2F 62  69 6E 2F 65 6E 76 20 70     #!/usr/bin/env p
79 74 68 6F 6E 0D 0A 0D  0A 69 6D 70 6F 72 74 20     ython....import
65 6D 61 69 6C 2E 70 61  72 73 65 72 0D 0A 69 6D     email.parser..im
70 6F 72 74 20 66 75 6E  63 74 6F 6F 6C 73 0D 0A     port functools..
69 6D 70 6F 72 74 20 6A  73 6F 6E 0D 0A 69 6D 70     import json..imp
6F 72 74 20 73 79 73 0D  0A 69 6D 70 6F 72 74 20     ort sys..import
73 74 72 69 6E 67 0D 0A  66 72 6F 6D 20 65 6D 61     string..from ema
69 6C 2E 6D 65 73 73 61  67 65 20 69 6D 70 6F 72     il.message impor
74 20 45 6D 61 69 6C 4D  65 73 73 61 67 65 0D 0A     t EmailMessage..
66 72 6F 6D 20 68 74 74  70 2E 73 65 72 76 65 72     from http.server

<----- Request End -----

127.0.0.1 - - [13/Dec/2022 10:24:28] "POST /here_is_a_hex_dump_as_well HTTP/1.1" 200 -
```

## Disclaimer

Header portion is start with `> ...`, while request body dose not.

Also `<...>` are used to indicate empty value or some meta data **inline**, such as `<no body>`, `<binary data, len=5203>`.

If incomming HTTP requests also use the same style syntax, please be careful when reading output.
