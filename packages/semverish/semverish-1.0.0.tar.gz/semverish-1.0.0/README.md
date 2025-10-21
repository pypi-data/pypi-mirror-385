# semverish

`semverish` is a simple go module designed to manage version information for different ecosystem like pypi.org, maven.org,
npmjs.com, crates.io ect. in a structured manner.

## Motivation

There are a lot of tools in different ecosystem .e.g `github.com/go-simpler/goversion` and `github.com/Masterminds/semver`
in golang, `semver` in python and obviously there will be ecosystem specific package available to manage, parse and do a
lot of operations on version strings of any package.

But the real life scenario is different, when dealing with multiple ecosystem and encountered different versioning
of different packages, it becomes difficult to manage and parse them in a structured manner dut to non-semverish
versioning followed by different maintainers.

So, here comes `versions` to rescue, it provides a structured way to manage version information for different ecosystem
in a structured manner, do operations on them and parse them that cannot be parsed by these packages.

## Installation

```bash
  pip install semverish
```

## Usage
```python
    import semverish
    
    print(semverish.natural_sorted_versions(
        ['1.0.0', '2.0.0', '1.2.0', '1.0.0-alpha', '1.0.0-beta.1', '1.0.0.beta2', 'rel-1.3.3', '1.3.4'],
        descending=False)
    )
    # output: ['1.0.0-alpha', '1.0.0-beta.1', '1.0.0.beta2', '1.0.0', '1.2.0', 'rel-1.3.3', '1.3.4', '2.0.0']
    
    print(semverish.analyze_constraints(
        'npm',
        '>1.1 <=2.9',
        ['1.1.1', '3.0', '2.9.9', '2.9.0', '1.9.0', '2.8.1', '1.0.0', '2.0.0', '1.2.0', '1.0.0-alpha', '1.0.0-beta.1', '1.0.0.beta2'])
    )
    # output: ['1.1.1', '3.0', '2.9.9', '2.9.0', '1.9.0', '2.8.1', '2.0.0', '1.2.0']
    
    print(semverish.analyze_constraints(
        language='python',
        constraints='>1.1,<=4.9',
        versions=['1.1.1', '3.0', '2.9.9', '2.9.0', '1.9.0', '2.8.1', '1.0.0', 'rel-2.0.0', '1.2.0', '1.0.0-alpha', '1.0.0-beta.1', 'rel_1.0.0.beta2'])
    )
```

## Supported Ecosystem
- pypi.org
- maven.org
- npmjs.com
- crates.io
- golang.org
- rubygems.org
