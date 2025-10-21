# Get started

Initialize a `Denario` instance and describe the data and tools to be employed.

```python
from denario import Denario

den = Denario(project_dir="project_dir")

prompt = """
Analyze the experimental data stored in data.csv using sklearn and pandas.
This data includes time-series measurements from a particle detector.
"""

den.set_data_description(prompt)
```

Generate a research idea from that data specification.

```python
den.get_idea()
```

This will trigger a planning and control workflow to design the ide. For a faster method you can use:

```python
den.get_idea_fast()
```

Generate the methodology required for working on that idea.

```python
den.get_method()
```

This will trigger a planning and control workflow to design the ide. For a faster method you can use:

```python
den.get_method_fast()
```


With the methodology setup, perform the required computations and get the plots and results.

```python
den.get_results()
```

Finally, generate a latex article with the results. You can specify the journal style, in this example we choose the [APS (Physical Review Journals)](https://journals.aps.org/) style.

```python
from denario import Journal

den.get_paper(journal=Journal.APS)
```

You can also manually provide any info as a string or markdown file in an intermediate step, using the `set_idea`, `set_method` or `set_results` methods. For instance, for providing a file with the methodology developed by the user:

```python
den.set_method(path_to_the_method_file.md)
```
