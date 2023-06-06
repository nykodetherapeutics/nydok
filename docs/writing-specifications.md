# Writing specifications

nydok uses Markdown files for collecting specifications. By default, it collects `Requirement`s from files with `.spec.md` extension.



!!! tip "Use the power of Markdown"
    Since you are writing Markdown documents, the specifications can be rich in content and not just a list of requirements. Keep in mind that you can add sections, tables, figures, references and anything else Markdown supports in order to create good specifications.

## Writing a requirement

nydok will scan the collected Markdown files for requirements matching a given regex. By default[^1], the format is given below:

```
- <ID>: <Description>
```
or with references:
```
- <ID> [<Reference(s)>]: <Description>
```

An example specification could look like the following:

```title="functional-specification.spec.md"

- FR001: Package must support generating random cooking recipes.

```

You can by default use any text for the requirement ID, as long as it's capital letters followed by a number. Examples could be `UR001` and `FR001` for user and functional requirements, but they could also be for instance `SEC001` (security requirements), `INFRA001` (infrastructure requirements) or `MYMOD001` (requirements concerning `MyModule`). It's completely up to you how to structure your specification.

!!! tip "Leave room for later requirements"
    When writing the initial specification, it is advised to leave a gap in the numbering so it's easier to add requirements later on. Two subsequent (related) requirements could for instance initially be named `FR001` and `FR010`, leaving room for adding more later within the same ID range.


!!! tip "On creating normal lists"
    The default regex reserves `-` character for requirements, while letting them render as lists when converted to HTML. If you need a normal list it is advised to use `*` to initiate the list items to avoid accidentially creating requirements.


## Referencing other requirements

A requirement can reference other requirements, which will allow you to e.g. connect requirements together in a traceability matrix.

The requirements can come in any order, you don't have to write the requirements being referred to first.

An example could look like the following:

```title="user-specification.spec.md"

- UR001: Software must demonstrate functionality of how a computer can generate random data.

```

```title="functional-specification.spec.md"

- FR001 [UR001]: Package must support displaying random cooking recipes.

```

Here, the `[UR001]` part will add `UR001` to `FR001` as a reference. Multiple references can be comma separated, like this: `[UR001,UR002]`.


## More on references

The references added within the brackets `[]` can be any kind of ID. This lets you also add references to external documents outside what's written for nydok and allows for mixing what kind of documents your write with nydok and what you write in e.g. Microsoft Word or other software.


## Changing the requirement format

You can change the format of the requirements by changing the regex used to match them. This is done by setting the `--nydok-specs-regex` option when running `py.test`. The regex should contain three named groups: `req_id`, `refs` and `desc`. The default regex is given below:

```bash

py.test --nydok-specs-regex='-(?P<req_id>[A-Z]+[0-9]+)( \[(?P<refs>[A-Z,0-9]+)\])?: (?P<desc>.*)' specifications/

```
