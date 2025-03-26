# ProxE
ProxE is a open-source, free to use, python proxy with access logging, authentication, and tunneling support built for flexibility and control.

## Disclaimer!!!
> ProxE is currently in development and extremely incomplete. It is currently being developed in github along with the documentation. Please keep watch for future development.

## Executable 
ProxE will come shipped with a standalone executable for Windows and Linux.

## HTTPS vs HTTP
ProxE utilizes the HTTP `CONNECT` method to start a new TCP tunnel from the client to the website. This allows SSL encrypted traffic to travel between the two without the need for the ProxE to ever handle encryption. It also benefits the client and website by ensuring none of their data is available to be tampered with by us sitting in the middle.

HTTP traffic is directly forwarded to the server without any tunneling. HTTP traffic can be disabled entirely via the config.


## Future implementation
Specific users can have http disabled and are only allowed to use encrypted requests.