# mw-citation-check
A bot for validating the values of citations instead of just their syntax.

## Usage ##

````
cat pageNameList.txt | python main.py <blacklist_dir>
````

The blacklist directory contains a list of urls with the domains of suspicious,fraudulent or predatory sites.

## Features
### Serious errors
* Blacklisted Domain
* Invalid(Unparsable) date formats
* Unrealistic Dates: Any year only date prior to the year 1000

#### Todo
* Unrealistic dates: Exact dates prior to user configurable cutoff year. e.g.( 1 February 100 )

### Warnings

* Weak Dates: Unspecific dates e.g.
 - Fall 2018
 - 2018
 - Early 2018
 
## TODO
Right now this is a good enough implementation for simple validation of some cases.  In the long run

* Separate `cite web`, `cite book`, etc., into common and  specific checks
* Generalize check logic
* Create different hooks for `emit_bad_citation()`, e.g. database, or actual page modification.

* Verify bad book publishers
* Distinguish between bad journals, books and self publishers.
