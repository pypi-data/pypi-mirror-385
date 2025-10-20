# VerNum

Configurable GitLab CI/CD-powered version numbering for project releases

<a href="https://www.flaticon.com/free-icons/rat" title="rat icons">Logo by Freepik/Flaticon</a>

(Similar to [GitVersion](https://gitversion.net/docs/))

## Python module/CLI installation

The VerNum Python module is distributed as a PyPI module and can be installed like any other.

Install with system-level Python

```
pip3 install vernum
```

Install with `pipx` to avoid dependency collisions

```
pipx install vernum
```

Install with a venv (depends on venv location)

```
.venv/bin/pip install vernum
```

... or install as a Poetry dev dependency


## Commands

*The `vernum max` command*

Takes a list of version numbers and based on the configued numbering scheme, returns the highest value in the list.

```bash
echo "1.4.0\n1.4.1\n1.5.0" | vernum max
```

*The `vernum next` command*

Takes a single version number and, based on the configured numbering scheme and the selected increment, outputs the next version number.

```bash
echo "3.4.5" | vernum next patch
```

*The `vernum limit` command*

Takes a single version number and, based on the onfigured numbering scheme and provided limits, triggers an error if the version number falls outside the limit. Only a minimum limit is currently supported (see configuration below).

## Schemes

VerNum supports multiple "schemes" for version numbering.

| Scheme | Description | Increments | Example |
| --- | --- | ---| --- |
| `major` | Just a single version number | `major` | `4` |
| `minor` | Major, dot, minor | `major` `minor` | `4.2` |
| `patch` | Major, dot, minor, dot patch | `major` `minor` `patch` | `4.2.1` |
| `minor-alpha-beta` | Major, dot, minor, dot, and either a patch, alpha, or beta | `major`, `minor`, `patch`, `alpha`, `beta` | `4.3.alpha2` |

Schemes support an optional "v" before the version number for inputs, including from Git, but output the result without a "v".

The default scheme is `patch`.

## Schemes with prerelease versions

Some schemes have prerelease versions (alpha, beta) with varying syntax. The basic approach to incrementing is to assume a preference for starting with alpha, then going to beta. So, for example, if the current version is at `1.2.3` and the operator requests a `patch` update, the version becomes, for example, `1.2.4-alpha` (depending on the scheme itself).

Increments only go forward, so avoid attempting to move from beta to alpha.

FOr the `minor-alpha-beta` scheme:

- `major` changes e.g. 5.6.2 to 6.0.alpha1
- `major-zero` changes e.g. 5.6.2 to 6.0.0
- `minor` changes e.g. 5.6.2 to 5.7.alpha1
- `minor-zero` changes e.g. 5.6.2 to 5.7.0
- `beta` changes e.g. 5.7.beta3 to 5.7.beta4
- `alpha` changes e.g. 5.7.alpha8 to 5.7.alpha9
- `patch` changes e.g. 5.6.beta6 to 5.6.0
- `patch` changes e.g. 5.6.2 to 5.6.3

For the `patch-hyphen-al-be` scheme:

- `major` changes e.g. 5.6.2 to 6.0.0-alpha
- `major-zero` changes e.g. 5.6.2 to 6.0.0
- `minor` changes e.g. 5.6.2 to 5.7.0-alpha
- `minor-zero` changes e.g. 5.6.2 to 5.7.0
- `patch` changes e.g. 5.6.2 to 5.6.3-alpha
- `patch-zero` changes e.g. 5.6.2 to 5.6.3
- `beta` changes e.g. 5.7.3-alpha to 5.7.3-beta
- `patch` changes e.g. 5.7.3-alpha to 5.7.3
- `patch-zero` changes e.g. 5.7.3-beta to 5.7.3
- The `major`, `major-zero`, `minor`, and `minor-zero` increments work as expected

### Use with Git tags

We designed VerNum to use with Git tags, and recommend using the history of tags in the default branch as the  source of truth for version numbers.

The example below demonstrates one way to use VerNum with Git tags.

```bash
git tag --list --merged HEAD | vernum max | vernum next patch > .version
git tag -a "$(cat .version)" -m "$(cat .version)"
```

Keep the following pointers in mind when using VerNum with Git.

- CD to the root of the project before running it
- Be on the branch that you use for releases (i.e. `master`)
- Be fully up-to-date in git (i.e. merged, committed, and pushed)


## Configuration and input

VerNum uses the [WizLib](https://gitlab.com/steampunk-wizard/wizlib) framework for configuration and input control.

- Input to commands can come through stdin
- Alternatively, use the `vernum --input <filename>` to pull input from a file
- The scheme can be selected with an environment variable `$VERNUM_SCHEME`
- Alternatively, the scheme can be set in a YAML configuration file; the application will try, in order:
  - A config file location designated with `vernum --config <filename>`
  - A config file location designated with a `$VERNUM_CONFIG` environment variable
  - `.vernum.yml` in the local directory
  - `.vernum.yml` in the user's home directory

We recommend placing a `.vernum.yml` file in the project directory and committing it to the project's Git repository, so different environments use the same scheme.

The format for the YAML file is simple (allowing for other forms of configuration in the future):

```yaml
vernum:
  scheme: minor
  limit:
    min: '4.2'
```

## Usage (GitLab CICD)

See the [ProCICD documentation](https://procicd.gitlab.io/patterns/version-numbering.html) for usage within GitLab CICD.
