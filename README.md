# MkDocs PlantUML plugin

[MkDocs](https://www.mkdocs.org/) plugin to support inline [PlantUML](https://plantuml.com/) in markdown pages

For a plugin that generates diagrams from puml files see also:
[mkdocs_build_plantuml](https://github.com/christo-ph/mkdocs_build_plantuml)

This plugin replaces inline plantuml in md files with a link to the actual generated plantuml diagram.

For example:
<pre>
```plantuml
@startuml
title Hello world
Alice -> Bob : hello
@enduml
```
</pre>

The plugin will call a local plantuml server (or the global plantuml server if configured) and generate the output in the configured format - default is svg.

<pre>
![Hello world](./md_name_1.svg)
</pre>

The @startuml / @enduml is optional here.

Great visual studio code plugins that support this format as well are [vscode-plantuml](https://github.com/qjebbs/vscode-plantuml/) in conjunction with [vscode-markdown-extended](https://github.com/qjebbs/vscode-markdown-extended).

My own PlantUML server [pumlsrv](https://github.com/michael72/pumlsrv) will render the SVG images from plantuml very quickly.

Have fun!

