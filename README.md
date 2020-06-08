# canvas.py

canvas.py provides a Pythonic wrapper for some of the REST API calls in the Instructure Canvas Learning Management System (LMS).

## Installation into Conda environment

```bash
conda env create -f environment.yml
conda activate canvas
```


## Example Usage

To export a quiz to markdown

```python
token = os.environ['CANVAS_TOKEN']
classroom = Canvas(token)
classroom.export_quiz('test.md', 1277781, 1348890)
```

where `1277781` is the course ID and `1348890` is the quiz ID.  This will create a markdown file called `test.md`.  If you wish to export to PDF, and you have a LaTeX installation, you can
pass the keyword argument `output_format='pdf'`.



