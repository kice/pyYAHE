#!/usr/bin/env python

import email.parser
import functools
import json
import sys
import string
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from urllib.parse import unquote_plus, parse_qs


class RequestHandler(BaseHTTPRequestHandler):
    def __getattr__(self, name: str):
        if name.startswith('do_'):
            return functools.partial(self.echo_request, method=name[3:])
        else:
            return super().__getattr__(name)

    def echo_request(self, method: str):
        print("\n----- Request Start ----->\n")
        print(f'* {self.client_address[0]}:{self.client_address[1]} {unquote_plus(self.path)}\n')
        print(f'> {method} {self.path} {self.request_version}')
        for k, v in self.headers.items():
            print(f'> {k}: {v}')

        content_length = self.headers.get('content-length')
        length = int(content_length) if content_length else 0

        missing = object()
        content_type = self.headers.get('content-type', missing)
        if content_type is missing:
            mime = 'text/plain'
            options = {}
            encoding = 'utf-8'
        else:
            msg = EmailMessage()
            msg['content-type'] = content_type
            mime, options = msg.get_content_type(), msg['content-type'].params
            encoding = options['charset'] if 'charset' in options else 'utf-8'

        print()

        if length == 0:
            print("<no body>\n<----- Request End -----\n")
            self.send_response(200)
            self.end_headers()
            return

        request_body = self.rfile.read(length)

        if mime.startswith('text/') or mime.lower() in {
            'application/json', 'application/x-www-form-urlencoded',
        }:
            try:
                text = request_body.decode(encoding)
            except UnicodeDecodeError:
                print(f'<error when decode as {encoding}>', end='')
            else:
                if mime == 'application/json':
                    try:
                        print(json.dumps(json.loads(text), indent=4, ensure_ascii=False))
                    except json.JSONDecodeError as e:
                        print(f'<invalid JSON string: {e!r}>')
                        print(text, end='')
                elif mime == 'application/x-www-form-urlencoded':
                    o = parse_qs(text)
                    for key, values in o.items():
                        if len(values) == 0:
                            print(f'{key}: <no set>')
                            continue
                        for v in values:
                            print(f'{key}: {v}')
                else:
                    print(text, end='')
        elif mime == 'multipart/form-data':
            # Decoder from https://github.com/requests/toolbelt
            boundary = options['boundary'].encode('ascii') if 'boundary' in options else b''
            boundary = b''.join((b'--', boundary))
            for i, part in enumerate(request_body.split(b''.join((b'\r\n', boundary)))):
                if not (
                    part != b'' and part != b'\r\n' and
                    part[:4] != b'--\r\n' and part != b'--'
                ):
                    continue

                if i == 0 and part.startswith(boundary):
                    part = part[len(boundary):]

                idx = part.find(b'\r\n\r\n')
                if idx == -1:
                    raise Exception('content does not contain CR-LF-CR-LF')
                elif idx == 0:
                    headers = {}
                    content = part
                else:
                    text = part[:idx].decode('utf-8').lstrip()
                    headers = email.parser.HeaderParser().parsestr(text)
                    content = part[idx + len(b'\r\n\r\n'):]
                print(f'> FormData {i+1}:')
                for k, v in headers.items():
                    print(f'{k}: {v}')
                print(f'<binary data, len={len(content)} ({content[:20]})>\n')
        else:
            print(f'<binary data, len={len(request_body)}>')
            off = 0
            while off < 160 and off < len(request_body):
                h = request_body[off:off+16]
                line = ''.join([
                    ' '.join(f'{c:02X}' for c in h[:8]), '  ',
                    ' '.join(f'{c:02X}' for c in h[8:16])
                ])
                text = ''.join(chr(c) if chr(c) in string.printable.strip() + ' ' else '.' for c in h)
                print(f'{line.ljust((16 * 3 + 2))}   {text}')
                off += 16

        print("\n<----- Request End -----\n")
        self.send_response(200)
        self.end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 37012
    print(f'Listening on 0.0.0.0:{port}')
    server_class = ThreadingHTTPServer if sys.argv[-1] == '-t' else HTTPServer
    server = server_class(('0.0.0.0', port), RequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
