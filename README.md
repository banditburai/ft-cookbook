# FastHTML Examples

A collection of example patterns and tutorials for building web applications with FastHTML and HTMX.

## Examples

- [State Patterns](docs/state-patterns/index.html) - Working with state in FastHTML applications
- Pydantic Integration (Coming Soon) - Best practices for form validation
- (More examples coming soon...)

## Development

Examples are developed in Jupyter notebooks and exported to static HTML for GitHub Pages hosting.

## View the Examples

Visit [FastHTML Cookbook](https://banditburai.github.io/ft-cookbook) to see the examples in action.

## Local Development

Examples are developed in Jupyter notebooks using my ft-jupyter package. A template notebook is provided to get you started quickly. I use uv to set stuff up - you can use whatever you want.

in your project root, run:
```bash
uv init --app . --python python3.11
```

```bash
uv add --dev ipykernel uv

```bash
uv run ipython kernel install --user --name=project
```

```bash
uv add python-fasthtml
```

(this is to init the kernel, you can also just do a source .venv/bin/activate and uv sync)
```bash
uv run hello.py
```

1. Download the [template notebook](https://raw.githubusercontent.com/banditburai/ft-cookbook/main/notebooks/index.ipynb)
2. Open the notebook in vscode or cursor or jupyter lab
3. (If you're using vscode or cursor, choose the venv as the kernel)
4. You'll want to spam 'run all' as you develop if major changes are made. Otherwise, you can just run the cells you're working on, make changes, and it'll update automagically.
5. The last line in the template is a manager.stop() call. You can uncomment and run that to stop the server.

## Contributing

Feel free to open issues or submit pull requests with new examples or improvements to existing ones. Info might be wrong, ai was used, consulted, spammed, yapped at etc.
