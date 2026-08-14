import urllib.request, json
req = urllib.request.Request('https://api.github.com/user/repos', data=json.dumps({'name':'career-ops','private':True}).encode('utf-8'), headers={'Authorization': 'token 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', 'Content-Type': 'application/json', 'Accept': 'application/vnd.github.v3+json'})
try:
    res = urllib.request.urlopen(req)
    print(res.read().decode('utf-8'))
except Exception as e:
    print(e.read().decode('utf-8'))
