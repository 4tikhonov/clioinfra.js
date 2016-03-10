from __future__ import absolute_import
database = 'datasets'
configpath = "/etc/apache2/clioinfra.conf"

FORBIDDENURI = "(curl|bash|mail|ping|sleep|passwd|cat\s+|cp\s+|mv\s+|certificate|wget|usr|bin|lhost|lport)"
FORBIDDENPIPES = '[\|\;><`()$]'
ERROR1 = "Something went wrong with special characters in url..."
ERROR2 = "Something definitely went wrong with specific terms in url..."
