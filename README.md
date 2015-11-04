## explo

explo is a simple tool to describe security issues in a human and machine readable format.
By defining a request/response workflow explo is able to reproduce the exploiting of security issues without the
need of writing a script. This allows chaining of requests.

### Example (POST form with CSRF field)

	---
    name: CSRF
	description: This request receives a csrf token to save it for further exploitation
    module: http
    parameter:
        url: http://example.com/login
        method: GET
	    header:
            user-agent: Mozilla/5.0
        extract:
            csrf: form#login > .input[hidden]
	---
	name: Exploit
    description: Exploit issue with valid csrf token
    module: http
	source: CSRF.extracted.csrf
    parameter:
        url: http://example.com/login
        method: POST
        data: csrf={{csrf}}&username=' SQL INJECTION

    ---
    name: Report result
	description: Check if the injection returned an error
    module: match
	source: Exploit.response
	parameter:
        type: stringfind
        value: You have an error in your SQL syntax

In this example definition file the security issue is tested by executing 4 steps which are run from top to bottom. The last action block (REPORT) matches for a string or regular expression and returns the result.

It is possible to share and easily retest a specific vulnerability with this tool.
