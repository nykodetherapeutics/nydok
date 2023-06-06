# Traceability matrix

The traceability matrix report creates a table from your requirements with their references and test cases.


## Usage

You can create a traceability matrix report by running the following command:

```bash
nydok report traceability-matrix <args>
```

## Default report

By default the created table will list all requirements, regardless of the ID of the requirements, sorted by the requirement ID. This is useful when you want a complete overview of all requirements in your application. It does not, however, give a good overview of how the requirements are connected to eachother.

Example:

ID    | Description                                                                         | References   | Test case
----- | ----------------------------------------------------------------------------------- | ------------ | ---------
FR001 | Package must support generating random cooking recipes.                             | DOC001,UR001 | TC001
FR010 | Package must be written in Python programming language.                             | DOC002,UR002 | TC002
FR020 | Package must use Python-only packages.                                              | DOC050,UR002 | TC002
UR001 | Software must demonstrate functionality of how a computer can generate random data. | DOC001       | TC001
UR002 | Software must run on several operating systems.                                     | DOC050       | TC002


## Filtering requirements by prefix

To control which requirements are provided in a table, you can filter the requirements by using the `--base-prefix` argument.

For instance `--base-prefix="FR"` will only list the requirements starting with `FR`:

ID    | Description                                             | References   | Test case
----- | ------------------------------------------------------- | ------------ | ---------
FR001 | Package must support generating random cooking recipes. | DOC001,UR001 | TC001
FR010 | Package must be written in Python programming language. | DOC002,UR002 | TC002
FR020 | Package must use Python-only packages.                  | DOC050,UR002 | TC002


## Adding additional columns

You can add arbitrary many columns, each containing their own prefix.

For example, adding the argument `--categories="User Requirement,UR"` together with `--base-prefix="FR"` will yield the following table:

User Requirement | ID    | Description                                             | References | Test case
---------------- | ----- | ------------------------------------------------------- | ---------- | ---------
UR001            | FR001 | Package must support generating random cooking recipes. | DOC001     | TC001
UR002            | FR010 | Package must be written in Python programming language. | DOC002     | TC002
UR002            | FR020 | Package must use Python-only packages.                  | DOC050     | TC002

You can add more columns using comma separation `<title1>,<prefix1>,<title2>,<prefix2>,...`.

Bringing the `DOC` references to it's own column with `--categories="User Requirement,UR,Internal system,DOC"` could look like the following:

User Requirement | Internal system | ID    | Description                                             | References | Test case
---------------- | --------------- | ----- | ------------------------------------------------------- | ---------- | ---------
UR001            | DOC001          | FR001 | Package must support generating random cooking recipes. |            | TC001
UR002            | DOC002          | FR010 | Package must be written in Python programming language. |            | TC002
UR002            | DOC050          | FR020 | Package must use Python-only packages.                  |            | TC002


Likewise, we could flip it around and use the `UR` as base-prefix, to create a table for the user requirements only.


!!! note "References are only traversed one way"
    The reference traversal only works one way, from the requirement referencing another requirement and outwards. This means you always have to start using the innermost ID as base-prefix to create the table if you want to include all requirements. In the examples above, one could not use `UR` as base-prefix, since it is the `FR` referencing the `UR`s, not the other way around.