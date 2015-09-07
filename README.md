# fixity-auditor

An auditor for the fixity of AWS S3 and OpenStack Swift objects.


_THIS HAS NOT YET BEEN TESTED TO ENSURE IT WORKS_


## Swift Middleware


To enable the fixity audit middleware for OpenStack Swift, add the following to
your `proxy.conf` file in your swift configuration which is probably in `/etc/swift/`


    [pipeline:main]
    pipeline = healthcheck fixity … proxy-server

    [filter:fixity]
    paste.filter_factory = fixity.swift:fixity_factory


To use the middleware, you will want to add an `x-fixity-nonce` header to a HEAD
request to `v1/:account:/:container:/:object:/fixity-check` as follows:

    curl -i $publicURL/cheesemonger/cave/brie/fixity-check -X HEAD -H "X-Auth-Token: $token" -H "X-Fixity-Nonce: camembert"




