#  coding: utf-8 
import socketserver
import os.path

# Copyright 2021 Abram Hindle, Eddie Antonio Santos, Faiyaz Ahmed
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright Â© 2001-2021 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        
        root = "./www"
        method, file, host = self.parse_request()  
        
        path = root + file  # path 
        response = None
        
        if file.endswith("/"):
            path = path + "index.html" #to homepage

       
        if method != "GET":                 #determine if its allowed method and not HEAD POST PUT DELETE  
            response = self.response_405()     
        elif not file.endswith("/") and os.path.isdir(path):     # if file exists and not "/", redirect
            redirec_path = file + "/"       
            response = self.response_301(redirec_path, host)
        elif os.path.isfile(path):                         #if specified path exist
            mime_type = self.get_mime_type(path)           #find file type or if folder
            if mime_type != "folder":
                content = self.file_content(path)
                if content != "Error reading file!":
                    response = self.response_200(mime_type, content)  #Ok return
                else:
                    response = self.response_404()        #errors
            else:
                response = self.response_404()
        else:
                response = self.response_404()

        self.request.sendall(bytearray(response,'utf-8'))     #encoding and return response


    
    def parse_request(self):
        host = None
        lines = self.data.decode("utf-8").splitlines()  #decode data received to utf-8 from byte and create list of each line content
        method, file, protocol = lines[0].split()      #take the first line and split its content into method, file and protocol
        for line in lines:                             #find the host in the list of "lines"
            if "Host:" in line:
                host = "http://"+line.split()[-1]
        return method, file, host

            

    def file_content(self, path):        #reading file and returning its content
        try:
            file = open(path, "r") 
        except Exception:
            content = "Error reading file!"
        else:
            content = file.read()
            file.close()
        finally:
            return content


   
    def get_mime_type(self, path):
        ext = os.path.splitext(path)[1]
        if ext != "":
            return "text/" + ext.split(".")[1] # for a valid file,there is extension
        else:
            return "folder"    # a folder,no extension

            
   
    def response_200(self, mime_type, content):
        return "HTTP/1.1 200 OK\r\nContent-Type: " + mime_type + "\r\n\r\n" + content + "\r\n"  #found content

    def response_301(self, redirect_path, host):
        return "HTTP/1.1 301 Moved Permanently\r\nLocation: " + host + redirect_path + "\r\n"  #redirect to redirect_path

    def response_404(self):
        return "HTTP/1.1 404 Not Found\r\nConnection: close\r\n" #connection close if not found

    def response_405(self):
        return "HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n" #connection close if method not implemented


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()