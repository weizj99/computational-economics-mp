# The course website

The website is in `website/`: HTML, CSS and JavaScript, saved results and
figures, fonts, captions, videos and the code downloads. Its controls choose
among saved results; they do not run the model.

## Preview it

From the repository root, run

```bash
python run.py serve --site-dir website
```

and open http://127.0.0.1:8765/. The server only reads files, listens on this
computer alone, and supports the byte ranges that video seeking needs. It is a
local preview, not a production host. Opening the HTML files directly also
works, but browsers may then block the course fonts and the video captions.

## Hosting

GitHub Pages serves the website from this repository, at
<https://computational-economics.zhongjiwei.org/>. The workflow
`.github/workflows/pages.yml` publishes the `website/` folder whenever
`main` changes; the new version is online a minute or two later. Nothing runs
on a server: the pages, figures, videos and downloads are static files. See
[GitHub's Pages overview](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

[project_links.json](project_links.json) holds the website's address, the
repository's address and the branch that the pages link to.

## Links to the code

Every page's header links to the repository. Every lesson ends with a "Code on
GitHub" line that links each file the lesson uses, as listed in
[course_map.json](course_map.json). `python tools/site/source_links.py`
writes these lines; `--check` reports a page whose lines are out of date, and a
page header, home page, download README, notice or citation file that names
another repository address. A line that is already on a page keeps its place, so it can be moved
by hand. The links point to the main branch, so readers can open them once the
repository is public.

The code downloads on the unit pages are built from the repository by
`python tools/build_downloads.py`; `--check` reports any download that no longer
matches the repository.
