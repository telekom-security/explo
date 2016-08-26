from explo.exceptions import ParserException

def required_fields(opts, fields):
    """
    Check if all ensured fields passed by `fields` are set in the options
    """

    if not all(k in opts for k in fields):
        raise ParserException(
            'not all required parameters were passed. required: ' \
            ','.join(required_fields)
        )
