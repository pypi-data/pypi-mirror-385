# ARLAS Command line for collection management

```
python3 -m arlas.cli.cli  --help
                                                                                                                                             
 Usage: python -m arlas.cli.cli [OPTIONS] COMMAND [ARGS]...                                                                                  
                                                                                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config-file                       TEXT  Path to the configuration file if you do not want to use the default one:                       │
│                                           .arlas/cli/configuration.yaml.                                                                  │
│                                           [default: None]                                                                                 │
│ --print-curl     --no-print-curl          Print curl command [default: no-print-curl]                                                     │
│ --version                                 Print command line version                                                                      │
│ --help                                    Show this message and exit.                                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ collections                                                                                                                               │
│ confs                                                                                                                                     │
│ iam                                                                                                                                       │
│ indices                                                                                                                                   │
│ persist                                                                                                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Actions on collections:

```
python3 -m arlas.cli.cli collections --help
                                                                                                                                             
 Usage: python -m arlas.cli.cli collections [OPTIONS] COMMAND [ARGS]...                                                                      
                                                                                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config        TEXT  Name of the ARLAS configuration to use from your configuration file (/home/gaudan/.arlas/cli/configuration.yaml).   │
│                       [default: None]                                                                                                     │
│ --help                Show this message and exit.                                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ count            Count the number of hits within a collection (or all collection if not provided)                                         │
│ create           Create a collection                                                                                                      │
│ delete           Delete a collection                                                                                                      │
│ describe         Describe a collection                                                                                                    │
│ list             List collections                                                                                                         │
│ name             Set the collection display name                                                                                          │
│ private          Set collection visibility to private                                                                                     │
│ public           Set collection visibility to public                                                                                      │
│ sample           Display a sample of a collection                                                                                         │
│ set_alias        Set the field display name                                                                                               │
│ share            Share the collection with the organisation                                                                               │
│ unshare          Unshare the collection with the organisation                                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Actions on indices:

```
python3 -m arlas.cli.cli indices --help
                                                                                                                                             
 Usage: python -m arlas.cli.cli indices [OPTIONS] COMMAND [ARGS]...                                                                          
                                                                                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config        TEXT  Name of the ARLAS configuration to use from your configuration file (/home/gaudan/.arlas/cli/configuration.yaml).   │
│                       [default: None]                                                                                                     │
│ --help                Show this message and exit.                                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ clone           Clone an index and set its name                                                                                           │
│ create          Create an index                                                                                                           │
│ data            Index data                                                                                                                │
│ delete          Delete an index                                                                                                           │
│ describe        Describe an index                                                                                                         │
│ list            List indices                                                                                                              │
│ mapping         Generate the mapping based on the data                                                                                    │
│ migrate         Migrate an index on another arlas configuration, and set the target index name                                            │
│ sample          Display a sample of an index                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Actions on configurations:

```
python3 -m arlas.cli.cli confs --help
                                                                                                                                             
 Usage: python -m arlas.cli.cli confs [OPTIONS] COMMAND [ARGS]...                                                                            
                                                                                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ check               Check the services of a configuration                                                                                 │
│ create              Add a configuration                                                                                                   │
│ default             Display the default configuration                                                                                     │
│ delete              Delete a configuration                                                                                                │
│ describe            Describe a configuration                                                                                              │
│ list                List configurations                                                                                                   │
│ login               Add a configuration for ARLAS Cloud                                                                                   │
│ set                 Set default configuration among existing configurations                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```
