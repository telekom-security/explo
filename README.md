explo
=====

explo is a simple tool to describe security issues in a human and machine readable format.
By defining a request/response workflow explo is able to reproduce the exploiting of security issues without the
need of writing a script. This allows chaining of requests.

### Example (POST form with CSRF field)

	---
    name: get_csrf
	description: This request receives a csrf token to save it for further exploitation
    module: http
    parameter:
        url: http://example.com/contact
        method: GET
	    header:
            user-agent: Mozilla/5.0
        extract:
            csrf: [CSS, "#csrf_token"]
	---
	name: Exploit
    description: Exploit issue with valid csrf token
    module: http
    parameter:
        url: http://example.com/contact
        method: POST
        body:
            csrf: "{{get_csrf.extracted.csrf}}"
            username: "' SQL INJECTION"
        find: You have an error in your SQL syntax

In this example definition file the security issue is tested by executing 2 steps which are run from top to bottom. The last step returns a success or failure, depending on the string 'You have an error in your SQL syntax' to be found.

It is possible to share and easily re-test a specific vulnerability with this tool.

### Installation

1. Clone the repository

    ```
    git clone https://github.com/dtag-dev-sec/explo
    ```

2. Install explo

    ```
    cd explo
    python setup.py install
    ```

### Usage

```
explo [--debug] testcase.yaml
```

### Modules

Modules can be added to improve the functionality and testable security issues.

#### http (basic)

The http modules allows to make http request, extract content and search for content. The http as well as headers can be passed.

The following data is made available for other modules:

* the http response body: `stepname.response.content` 
* the http response cookies: `stepname.response.cookies`
* extracted content: `response.extracted.variable_name`

If a `find` parameter is set, a regular expression match is executed on the response body. If this fails, this module returns a failure and thus stopping the executing of the current workflow.


