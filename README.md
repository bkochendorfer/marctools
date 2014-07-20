marctools
=========

Various MARC utilities.

[![Build Status](http://img.shields.io/travis/miku/marctools.svg?style=flat)](https://travis-ci.org/miku/marctools)

Installation
------------

For native packages see: https://github.com/miku/marctools/releases

If you have a local Go installation, you can just

    go get github.com/miku/marctools/cmd/{marccount,marcdump,marcmap,marcsplit,marctojson,...}

Executables available are:

    marccount
    marcdump
    marcmap
    marcsplit
    marctojson
    marctotsv
    marcuniq

marccount
---------

Prints the number of records found in a file and then exits.

    $ marccount fixtures/journals.mrc
    10

marcdump
--------

Dumps MARC to stdout (just like `yaz-marcdump`):

    $ marcdump fixtures/testbug2.mrc
    001 testbug2
    005 20110419140028.0
    008 110214s1992    it a     b    001 0 ita d
    020 [  ] [(a) 8820737493]
    035 [  ] [(a) (OCoLC)ocm30585539]
    040 [  ] [(a) RBN], [(c) RBN], [(d) OCLCG], [(d) PVU]
    041 [1 ] [(a) ita], [(a) lat], [(h) lat]
    043 [  ] [(a) e-it---]
    050 [14] [(a) DG848.15], [(b) .V53 1992]
    049 [  ] [(a) PVUM]
    100 [1 ] [(a) Vico, Giambattista,], [(d) 1668-1744.]
    240 [10] [(a) Principum Neapolitanorum coniurationis anni MDCCI historia.], [(l) Italian & Latin]
    245 [13] [(a) La congiura dei Principi Napoletani 1701 :], [(b) (prima e seconda stesura) /], [(c) Giambattista Vico ; a cura di Claudia Pandolfi.]
    250 [  ] [(a) Fictional edition.]
    260 [  ] [(a) Morano :], [(b) Centro di Studi Vichiani,], [(c) 1992.]
    300 [  ] [(a) 296 p. :], [(b) ill. ;], [(c) 24 cm.]
    490 [1 ] [(a) Opere di Giambattista Vico ;], [(v) 2/1]
    500 [  ] [(a) Italian and Latin.]
    504 [  ] [(a) Includes bibliographical references (p. [277]-281) and index.]
    520 [3 ] [(a) Sample abstract.]
    590 [  ] [(a) April11phi]
    651 [ 0] [(a) Naples (Kingdom)], [(x) History], [(y) Spanish rule, 1442-1707], [(v) Sources.]
    700 [1 ] [(a) Pandolfi, Claudia.]
    800 [1 ] [(a) Vico, Giambattista,], [(d) 1668-1744.], [(t) Works.], [(f) 1982 ;], [(v) 2, pt. 1.]
    856 [40] [(u) http://fictional.com/sample/url]
    994 [  ] [(a) C0], [(b) PVU]

marcmap
-------

Dumps a list of id, offset, length tuples to stdout (TSV) or to a sqlite3 database:

    $ marcmap fixtures/journals.mrc
    testsample1 0   1571
    testsample2 1571    1195
    testsample3 2766    1057
    testsample4 3823    1361
    testsample5 5184    1707
    testsample6 6891    1532
    testsample7 8423    1426
    testsample8 9849    1251
    testsample9 11100   2173
    testsample10    13273   1195

    $ marcmap -o seekmap.db fixtures/journals.mrc
    $ sqlite3 seekmap.db 'select id, offset, length from seekmap'
    testsample1|0|1571
    testsample2|1571|1195
    testsample3|2766|1057
    testsample4|3823|1361
    testsample5|5184|1707
    testsample6|6891|1532
    testsample7|8423|1426
    testsample8|9849|1251
    testsample9|11100|2173
    testsample10|13273|1195

marcsplit
---------

Splits a marcfile into smaller pieces.

    $ marcsplit -h
    Usage of marcsplit:
      -C=1: number of records per file
      -cpuprofile="": write cpu profile to file
      -d=".": directory to write to
      -s="split-": split file prefix
      -v=false: prints current program version

    $ marcsplit -d /tmp -C 3 -s "example-prefix-" fixtures/journals.mrc
    $ ls -1 /tmp/example-prefix-0000000*
    /tmp/example-prefix-00000000
    /tmp/example-prefix-00000001
    /tmp/example-prefix-00000002
    /tmp/example-prefix-00000003

marctojson
----------

Converts MARC to JSON.

    $ marctojson -h
    Usage of marctojson:
      -cpuprofile="": write cpu profile to file
      -i=false: ignore marc errors (not recommended)
      -l=false: dump the leader as well
      -m="": a key=value pair to pass to meta
      -p=false: plain mode: dump without content and meta
      -r="": only dump the given tags (e.g. 001,003)
      -v=false: prints current program version and exit
      -w=4: number of workers

    $ marctojson fixtures/testbug2.mrc | jsonpp
    {
      "content": {
        "001": "testbug2",
        "005": "20110419140028.0",
        "008": "110214s1992    it a     b    001 0 ita d",
        "020": [
          {
            "a": "8820737493",
            "ind1": " ",
            "ind2": " "
          }
        ],
        ...
        "040": [
          {
            "a": "RBN",
            "c": "RBN",
            "d": [
              "OCLCG",
              "PVU"
            ],
            "ind1": " ",
            "ind2": " "
          }
        ],
        ...
        "856": [
          {
            "ind1": "4",
            "ind2": "0",
            "u": "http://fictional.com/sample/url"
          }
        ]
      },
      ...
      "meta": {}
    }

    $ marctojson -l -r 040 fixtures/testbug2.mrc | jsonpp
    {
      "content": {
        "040": [
          {
            "a": "RBN",
            "c": "RBN",
            "d": [
              "OCLCG",
              "PVU"
            ],
            "ind1": " ",
            "ind2": " "
          }
        ],
        "leader": {
          "ba": "337",
          "cs": "a",
          "ic": "2",
          "impldef": "m Ma ",
          "length": "1234",
          "lol": "4",
          "losp": "5",
          "raw": "01234cam a2200337Ma 4500",
          "sfcl": "2",
          "status": "c",
          "type": "a"
        }
      },
      "meta": {}
    }

    $ marctojson -r "001, 245" -p fixtures/testbug2.mrc | jsonpp
    {
      "001": "testbug2",
      "245": [
        {
          "a": "La congiura dei Principi Napoletani 1701 :",
          "b": "(prima e seconda stesura) /",
          "c": "Giambattista Vico ; a cura di Claudia Pandolfi.",
          "ind1": "1",
          "ind2": "3"
        }
      ]
    }

    $ marctojson -r "001, 245" -m date="$(date)" fixtures/testbug2.mrc | jsonpp
    {
      "content": {
        "001": "testbug2",
        "245": [
          {
            "a": "La congiura dei Principi Napoletani 1701 :",
            "b": "(prima e seconda stesura) /",
            "c": "Giambattista Vico ; a cura di Claudia Pandolfi.",
            "ind1": "1",
            "ind2": "3"
          }
        ]
      },
      "meta": {
        "date": "Sun Jul 20 17:36:37 CEST 2014"
      }
    }

marctotsv
---------

Converts selected MARC tags to tab-separated values (TSV).

    $ marctotsv
    Usage: marctotsv [OPTIONS] MARCFILE TAG [TAG, TAG, ...]
      -cpuprofile="": write cpu profile to file
      -f="<NULL>": fill missing values with this
      -i=false: ignore marc errors (not recommended)
      -k=false: skip incomplete lines (missing values)
      -s="": separator to use for multiple values
      -v=false: prints current program version and exit
      -w=4: number of workers

    $ marctotsv fixtures/journals.mrc 001
    testsample1
    testsample2
    testsample3
    testsample4
    testsample5
    testsample6
    testsample7
    testsample8
    testsample9
    testsample10

    $ marctotsv fixtures/journals.mrc 001 245.a
    testsample1 Journal of rational emotive therapy :
    testsample2 Rational living.
    testsample3 Psychotherapy in private practice.
    testsample4 Journal of quantitative criminology.
    testsample5 The Journal of parapsychology.
    testsample6 Journal of mathematics and mechanics.
    testsample7 The Journal of psychology.
    testsample8 Journal of psychosomatic research.
    testsample9 The journal of sex research
    testsample10    Journal of phenomenological psychology.

    $ marctotsv -f UNDEF fixtures/journals.mrc  001 245.a 245.b
    testsample1 Journal of rational emotive therapy :   the journal of the Institute for Rational-Emotive Therapy.
    testsample2 Rational living.    UNDEF
    testsample3 Psychotherapy in private practice.  UNDEF
    testsample4 Journal of quantitative criminology.    UNDEF
    testsample5 The Journal of parapsychology.  UNDEF
    testsample6 Journal of mathematics and mechanics.   UNDEF
    testsample7 The Journal of psychology.  UNDEF
    testsample8 Journal of psychosomatic research.  UNDEF
    testsample9 The journal of sex research UNDEF
    testsample10    Journal of phenomenological psychology. UNDEF

    $ marctotsv -k fixtures/journals.mrc  001 245.a 245.b
    testsample1 Journal of rational emotive therapy :   the journal of the Institute for Rational-Emotive Therapy.

    $ marctotsv -s "|" fixtures/journals.mrc  001 710.a
    testsample1 Institute for Rational-Emotive Therapy (New York, N.Y.)
    testsample2 Institute for Rational-Emotive Therapy (New York, N.Y.)|Institute for Rational Living.
    testsample3 <NULL>
    testsample4 LINK (Online service)
    testsample5 Duke University.|ProQuest Psychology Journals.
    testsample6 Indiana University.|Indiana University.
    testsample7 ProQuest Psychology Journals.
    testsample8 ScienceDirect (Online service).
    testsample9 Society for the Scientific Study of Sex (U.S.)|Society for the Scientific Study of Sexuality (U.S.)|JSTOR (Organization)
    testsample10    Ingenta (Firm).

marcuniq
--------

    $ marcuniq -h
    Usage: marcuniq [OPTIONS] MARCFILE
      -i=false: ignore marc errors (not recommended)
      -o="": output file (or stdout if none given)
      -v=false: prints current program version
      -x="": comma separated list of ids to exclude (or filename with one id per line)

    $ marcuniq -x "testsample1,testsample2,testsample3" -o filtered.mrc fixtures/journals.mrc
    excluded ids interpreted as string
    3 ids to exclude loaded
    10 records read
    7 records written, 0 skipped, 3 excluded, 0 without ID (001)

    $ marctotsv filtered.mrc 001
    testsample4
    testsample5
    testsample6
    testsample7
    testsample8
    testsample9
    testsample10
