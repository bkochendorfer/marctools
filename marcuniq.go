package main

import (
    "./marc21"
    "flag"
    "fmt"
    "io"
    "log"
    "os"
)

// poor mans string set
type StringSet struct {
    set map[string]bool
}

func NewStringSet() *StringSet {
    return &StringSet{set: make(map[string]bool)}
}

func (set *StringSet) Add(s string) bool {
    _, found := set.set[s]
    set.set[s] = true
    return !found //False if it existed already
}

func (set *StringSet) Contains(s string) bool {
    _, found := set.set[s]
    return found
}

func (set *StringSet) Size() int {
    return len(set.set)
}

type SeekMap struct {
    offset int64
    length int64
}

func main() {

    const app_version = "1.3.1"

    ignore := flag.Bool("i", false, "ignore marc errors (not recommended)")
    version := flag.Bool("v", false, "prints current program version")
    outfile := flag.String("o", "", "output file (or stdout if none given)")

    var PrintUsage = func() {
        fmt.Fprintf(os.Stderr, "Usage: %s [OPTIONS] MARCFILE\n", os.Args[0])
        flag.PrintDefaults()
    }

    flag.Parse()

    // display version and exit
    if *version {
        fmt.Println(app_version)
        os.Exit(0)
    }

    if flag.NArg() != 1 {
        PrintUsage()
        os.Exit(1)
    }

    // input file
    fi, err := os.Open(flag.Args()[0])
    if err != nil {
        panic(err)
    }

    defer func() {
        if err := fi.Close(); err != nil {
            panic(err)
        }
    }()

    // output file or stdout
    var output *os.File

    if *outfile == "" {
        output = os.Stdout
    } else {
        output, err := os.Create(*outfile)
        if err != nil {
            panic(err)
        }
        defer func() {
            if err := output.Close(); err != nil {
                panic(err)
            }
        }()
    }

    // keep track of all ids
    ids := NewStringSet()
    // collect the duplicate ids; array, since same id may occur many times
    skipped := make([]string, 0, 0)
    // just count the total records
    counter := 0

    for {
        head, _ := fi.Seek(0, os.SEEK_CUR)
        record, err := marc21.ReadRecord(fi)
        if err == io.EOF {
            break
        }
        if err != nil {
            if *ignore {
                fmt.Fprintf(os.Stderr, "Skipping, since -i: %s\n", err)
                continue
            } else {
                panic(err)
            }
        }
        tail, _ := fi.Seek(0, os.SEEK_CUR)
        length := tail - head

        fields := record.GetFields("001")
        id := fields[0].(*marc21.ControlField).Data
        if ids.Contains(id) {
            skipped = append(skipped, id)
        } else {
            ids.Add(id)
            fi.Seek(head, 0)
            buf := make([]byte, length)
            n, err := fi.Read(buf)
            if err != nil {
                panic(err)
            }
            if _, err := output.Write(buf[:n]); err != nil {
                panic(err)
            }
        }
        counter += 1
    }

    log.Printf("Looped over %d records.\n", counter)
    log.Printf("Uniq: %d\n", ids.Size())
    log.Printf("Skipped: %d\n", len(skipped))
}
