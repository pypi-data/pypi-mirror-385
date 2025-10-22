# Configen CLI

This is the CLI tool for **Configen**, built with **Typer**, **Rich**, and **OpenAI**.

### 1. Install Pyenv
```
brew update
```
```
brew install pyenv
```
```
cat << 'EOF' >> ~/.zshrc
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
EOF
```
```
source ~/.zshrc
```
```
pyenv --version
```
```
pyenv install 3.12.3
```
```
pyenv local 3.12.3
```
```
which python
```
```
python --version
```

### 2. Create new Poetry project
```
poetry new configen-{project}
```
```
cd /configen-{project}
```
```
poetry install
```
```
poetry run pytest
```
```
poetry env info --path
```

### 3. Install/uninstall CLI from source code
```
pip install -e .
```
```
pip uninstall configen-cli
```

### 4. Deploy CLI to PyPI
```
poetry version patch
```
```
poetry build
```
```
poetry run twine upload --repository testpypi dist/* --verbose
```
```
poetry run twine upload --repository pypi dist/* --verbose
```