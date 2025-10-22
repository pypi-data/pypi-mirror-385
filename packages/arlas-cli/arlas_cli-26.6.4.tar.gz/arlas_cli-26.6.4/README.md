# ARLAS Command line for collection management

```
python3 -m arlas.cli.cli  --help
                                                                              
 Usage: python -m arlas.cli.cli [OPTIONS] COMMAND [ARGS]...                   
                                                                              
╭─ Options ──────────────────────────────────────────────────────────────────╮
│ --config-file                       TEXT  Path to the configuration file   │
│                                           if you do not want to use the    │
│                                           default one:                     │
│                                           .arlas/cli/configuration.yaml.   │
│ --print-curl     --no-print-curl          Print curl command               │
│                                           [default: no-print-curl]         │
│ --version                                 Print command line version       │
│ --quiet          --no-quiet               Remove non-essential printing    │
│                                           [default: no-quiet]              │
│ --help                                    Show this message and exit.      │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────╮
│ collections                                                                │
│ indices                                                                    │
│ persist                                                                    │
│ confs                                                                      │
│ iam                                                                        │
╰────────────────────────────────────────────────────────────────────────────╯

```

Actions on collections:

```
python3 -m arlas.cli.cli collections --help
                                                                              
 Usage: python -m arlas.cli.cli collections [OPTIONS] COMMAND [ARGS]...       
                                                                              
╭─ Options ──────────────────────────────────────────────────────────────────╮
│ --config        TEXT  Name of the ARLAS configuration to use from your     │
│                       configuration file                                   │
│                       (/home/gaudan/.arlas/cli/configuration.yaml).        │
│ --help                Show this message and exit.                          │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────╮
│ list        List collections                                               │
│ count       Count the number of hits within a collection (or all           │
│             collection if not provided)                                    │
│ describe    Describe a collection                                          │
│ public      Set collection visibility to public                            │
│ private     Set collection visibility to private                           │
│ share       Share the collection with the organisation                     │
│ unshare     Unshare the collection with the organisation                   │
│ name        Set the collection display name                                │
│ set_alias   Set the field display name                                     │
│ sample      Display a sample of a collection                               │
│ delete      Delete a collection                                            │
│ create      Create a collection                                            │
╰────────────────────────────────────────────────────────────────────────────╯

```

Actions on indices:

```
python3 -m arlas.cli.cli indices --help
                                                                              
 Usage: python -m arlas.cli.cli indices [OPTIONS] COMMAND [ARGS]...           
                                                                              
╭─ Options ──────────────────────────────────────────────────────────────────╮
│ --config        TEXT  Name of the ARLAS configuration to use from your     │
│                       configuration file                                   │
│                       (/home/gaudan/.arlas/cli/configuration.yaml).        │
│ --help                Show this message and exit.                          │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────╮
│ list       List indices                                                    │
│ describe   Describe an index                                               │
│ clone      Clone an index and set its name                                 │
│ migrate    Migrate an index on another arlas configuration, and set the    │
│            target index name                                               │
│ sample     Display a sample of an index                                    │
│ create     Create an index                                                 │
│ data       Index data                                                      │
│ mapping    Generate the mapping based on the data                          │
│ delete     Delete an index                                                 │
╰────────────────────────────────────────────────────────────────────────────╯

```

Actions on configurations:

```
python3 -m arlas.cli.cli confs --help
                                                                              
 Usage: python -m arlas.cli.cli confs [OPTIONS] COMMAND [ARGS]...             
                                                                              
╭─ Options ──────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────╮
│ set        Set default configuration among existing configurations         │
│ default    Display the default configuration                               │
│ check      Check the services of a configuration                           │
│ list       List configurations                                             │
│ create     Add a configuration                                             │
│ login      Add a configuration for ARLAS Cloud                             │
│ delete     Delete a configuration                                          │
│ describe   Describe a configuration                                        │
╰────────────────────────────────────────────────────────────────────────────╯

```
