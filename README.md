explo
=====

![screenshot](screenshot.png)

`explo` is a simple tool to describe web security issues in a human and machine readable format.
By defining a request/response workflow explo is able to exploit security issues without the
need of writing a script. This allows chaining of requests.

### Example (POST form with CSRF field)

    name: get_csrf
	description: extract csrf token from contact page
    module: http
    parameter:
        url: http://example.com/contact
        method: GET
	    header:
            user-agent: Mozilla/5.0
        extract:
            csrf: [CSS, "#csrf"]
	---
	name: exploit
    description: exploit sql injection vulnerability with valid csrf token
    module: http
    parameter:
        url: http://example.com/contact
        method: POST
        body:
            csrf: "{{get_csrf.extracted.csrf}}"
            username: "' SQL INJECTION"
        find: You have an error in your SQL syntax

In this example definition file the security issue is tested by executing two steps which are run from top to bottom. The last step returns a success or failure, depending on the string 'You have an error in your SQL syntax' to be found.

### Installation

1. Clone the repository

        git clone https://github.com/dtag-dev-sec/explo

2. Install explo

        cd explo
        python setup.py install

### Usage

    explo [--verbose] testcase.yaml
    explo [--verbose] examples/*.yaml

There are a few examples testcases in the `examples/` folder.

    explo examples/SQLI_simple_testphp.vulnweb.com.yaml

### Modules

Modules can be added to improve the functionality and testable security issues.

#### http (basic)

The http modules allows to make http request, extract content and search for content. The http as well as headers can be passed.

The following data is made available for other modules:

* the http response body: `stepname.response.content` 
* the http response cookies: `stepname.response.cookies`
* extracted content: `response.extracted.variable_name`

If a `find` parameter is set, a regular expression match is executed on the response body. If this fails, this module returns a failure and thus stopping the executing of the current workflow.

Parameter examples:

    parameter:
        url: http://example.com
        method: GET
        allow_redirects: True
        headers:
            User-Agent: explo
            Content-Type: abc
        body:
            key: value
        find: (reg|ular)expression
        extract:
            variable1: [CSS, '#csrf']
            variable2: [REGEX, '(reg|ular)expression']

#### http_header

The http header module allows to check if a response contains a specified set of headers (and values). All other parameters are identical to the http module.

The following data is made available for other modules:

* the http response body: `stepname.response.content` 
* the http response cookies: `stepname.response.cookies`

Parameter examples:

    parameter:
        url: http://example.com
        method: GET
        allow_redirects: True
        headers:
            User-Agent: explo
            Content-Type: abc
        body:
            key: value
        headers_required:
            X-XSS-Protection: 1
            Server: .               # all values are valid

#### sqli_blind

The sqli\_blind module is able to identify time based blind sql injections.

The following data is made available for other modules:

* the http response body: `stepname.response.content` 
* the http response cookies: `stepname.response.cookies`

Parameter examples:

    parameter:
        url: http://example.com/vulnerable.php?id=1' waitfor delay '00:00:5'--
        method: GET
        delay_seconds: 5

If the threshold of 5 seconds (delay_seconds) is exceeded, the check returns true (open).
