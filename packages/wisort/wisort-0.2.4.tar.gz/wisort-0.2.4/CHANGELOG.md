# CHANGELOG


## v0.2.4 (2025-10-18)

### Bug Fixes

- Quiet option always returns False as default
  ([`3fbcb44`](https://github.com/vividsystem/wisort/commit/3fbcb44b40da41df765c2bcd34c771cf96ba74b9))


## v0.2.3 (2025-10-18)


## v0.2.2 (2025-10-18)

### Continuous Integration

- Changing build to second step to implement the versioning
  ([`c75848c`](https://github.com/vividsystem/wisort/commit/c75848c1416f6393821ba48969da87dd7719ee46))

- Fixing incorrect build step dependencies
  ([`c4c51d0`](https://github.com/vividsystem/wisort/commit/c4c51d0d39a450b30dd758e0cad43510f774967f))


## v0.2.1 (2025-10-18)

### Bug Fixes

- Added config printing in verbose mode
  ([`50ed597`](https://github.com/vividsystem/wisort/commit/50ed597527310f620de67d77e35d5e87ccd09983))

- Added fallback config path if `$XDG_CONFIG_HOME` is not set
  ([`c082f85`](https://github.com/vividsystem/wisort/commit/c082f858d4626137ab3b3ddd4586f9e6f0400385))

- Added file removal before symlinking in portal mode
  ([`1556bae`](https://github.com/vividsystem/wisort/commit/1556bae591bb1efe7b630eb8bb48e1648bb06558))

- Handle edge case where st_birthtime doesn't get set by fs
  ([`801a71b`](https://github.com/vividsystem/wisort/commit/801a71b0d85b3b5e2724aa36e9fc332d3410b2ab))

### Documentation

- Added requirement for UNIX OS
  ([`113c5e2`](https://github.com/vividsystem/wisort/commit/113c5e299da557372fc70194fdad73e4d7edc860))


## v0.2.0 (2025-10-13)

### Chores

- Added `blake3`
  ([`d532680`](https://github.com/vividsystem/wisort/commit/d532680a1eca722bb72769d616e02935877a6c08))

### Documentation

- Updated roadmap and readme
  ([`c77d26a`](https://github.com/vividsystem/wisort/commit/c77d26a1d9001b4b887d91713e082ec1b08dca6a))

### Features

- Added default XDG_CONFIG_HOME path
  ([`e1c282f`](https://github.com/vividsystem/wisort/commit/e1c282f7cd5015961cafa5f465ec5f0e8eff5b3d))

- Added empty file removal
  ([`5d2dd7f`](https://github.com/vividsystem/wisort/commit/5d2dd7f1f5948f96e8ce9932c057aaa67328c448))

- Added runes and deduplication
  ([`44bc320`](https://github.com/vividsystem/wisort/commit/44bc32019866e897bb9c6dba54e4990578a5379c))


## v0.1.5 (2025-10-12)

### Continuous Integration

- Fixed download artifact dest
  ([`b879459`](https://github.com/vividsystem/wisort/commit/b87945995b33e4a7375dc72bf5647324bada7799))

- Fixing version
  ([`387ee0c`](https://github.com/vividsystem/wisort/commit/387ee0cb1a8b6188be5fdfc284f8930a262ca232))


## v0.1.4 (2025-10-12)


## v0.1.3 (2025-10-12)

### Continuous Integration

- Fixed environment mismatch
  ([`9224ecd`](https://github.com/vividsystem/wisort/commit/9224ecd46263988f3a9b7e7d539c5bef174e74d5))

- Removed deploy only on release condition
  ([`5b78100`](https://github.com/vividsystem/wisort/commit/5b781009c62a9a2443d62120600c1b560174388c))


## v0.1.2 (2025-10-12)

### Continuous Integration

- Fixed artifacts 2, added names to build and version steps
  ([`b1393f1`](https://github.com/vividsystem/wisort/commit/b1393f138eadc16c77574d8df10ce3a4ae48b408))

- Fixed skipping deploy
  ([`eb238aa`](https://github.com/vividsystem/wisort/commit/eb238aa2b5edea23ffe4f91870e28f2fa015f313))


## v0.1.1 (2025-10-12)

### Continuous Integration

- Fixed artifact up and download
  ([`a528149`](https://github.com/vividsystem/wisort/commit/a5281493ffbfca70037df7756aac1b3506845e46))


## v0.1.0 (2025-10-12)

### Bug Fixes

- Added force to config arguments
  ([`59d8ad1`](https://github.com/vividsystem/wisort/commit/59d8ad1f6dc8fef2563048a09edebd1bd63bb986))

- Artifact ci upload
  ([`09d3638`](https://github.com/vividsystem/wisort/commit/09d36387c9a0b4c01243558945e8dda279362888))

- Ci
  ([`a3e2ea5`](https://github.com/vividsystem/wisort/commit/a3e2ea500785098c628a6110ff146b04be9f15ec))

- Ci test in prod
  ([`cea3674`](https://github.com/vividsystem/wisort/commit/cea36743466c61a91acbebcce52be065aba43b20))

- Removed duplicate semantic-release config key
  ([`6fbd92f`](https://github.com/vividsystem/wisort/commit/6fbd92fb0bad253bbb402d6e567971500150fabf))

- Switched to dedicated action
  ([`a46bfd1`](https://github.com/vividsystem/wisort/commit/a46bfd19238c99f3c7ae432749bb34014ae3c1fd))

### Chores

- Configuring semver
  ([`2ab6a1c`](https://github.com/vividsystem/wisort/commit/2ab6a1cd7f652f3781c5d9c97ca03e9889c23b05))

- Switched semantic-release commad
  ([`0a6293c`](https://github.com/vividsystem/wisort/commit/0a6293ced7faa5b50771cf0ec2b1fe6589680e53))

### Continuous Integration

- Add checkout to build step
  ([`1db10f5`](https://github.com/vividsystem/wisort/commit/1db10f5dd204860926589b97ca2e6208201112f9))

- Fix 2
  ([`a889c49`](https://github.com/vividsystem/wisort/commit/a889c492b0561907f54f42180a0f3237fd1ba73c))

- Fix 3
  ([`66d5c9c`](https://github.com/vividsystem/wisort/commit/66d5c9ca3d4fe941b4cbba4f929f1dc268b8c419))

- Fix semantic-release
  ([`05c6b02`](https://github.com/vividsystem/wisort/commit/05c6b02f162e55077a43d25b799880aafbc2e443))

- Fixing
  ([`b5559f8`](https://github.com/vividsystem/wisort/commit/b5559f846fd9827d764ab5353d9bc59041e478bd))

- Fixing broken perms
  ([`929599f`](https://github.com/vividsystem/wisort/commit/929599fc4b72beed238cb8cede9fbbaecf9dab01))

### Documentation

- Added suggestion to publish in ROADMAP
  ([`44e044d`](https://github.com/vividsystem/wisort/commit/44e044d06afe5d1d9f7c2ac1fc94dad17665d8d4))

- Fixed :sparkles: emoji
  ([`56ac91b`](https://github.com/vividsystem/wisort/commit/56ac91ba14b34cd9e2fa4c8e29469eae4c276661))

### Features

- Please pretty please work
  ([`12b1eaa`](https://github.com/vividsystem/wisort/commit/12b1eaaa48ab30e2af708b9e9031acc187dd34ba))

- Redoing code that i accidentally deleted on my maschine
  ([`f5da9de`](https://github.com/vividsystem/wisort/commit/f5da9de6110c57a1312673dc9e3bb8f57bfbe86f))

### Refactoring

- Move conflict resolution
  ([`697ec5d`](https://github.com/vividsystem/wisort/commit/697ec5d10fb5f7c7286863187e4ad5d6548efe49))


## v0.0.0 (2025-10-10)

### Continuous Integration

- Fixed artifact name
  ([`6d7bae2`](https://github.com/vividsystem/wisort/commit/6d7bae2db9fe3227830768b29de350fc1c679418))

- Fixed wrong fetch depth
  ([`891e1fd`](https://github.com/vividsystem/wisort/commit/891e1fd8f0b2f64077df4700036aaa3552e91cfd))

- Fixing broken venv build pipeline
  ([`e741174`](https://github.com/vividsystem/wisort/commit/e741174d2d63c7134762840dc5781b31a4c20c9b))

- Fixing my stupidity
  ([`87b142c`](https://github.com/vividsystem/wisort/commit/87b142c9646e1416650c3d50ff0c06ef86a44dbc))

- Improved security and fixed build artifacts
  ([`3beed25`](https://github.com/vividsystem/wisort/commit/3beed25b725fd7768136230aaebd087763823e30))

- Make release pipeline
  ([`161d10c`](https://github.com/vividsystem/wisort/commit/161d10c5d667e737f727a1c438a4723071bdd5ce))

### Documentation

- Added LICENSE
  ([`99ef9f7`](https://github.com/vividsystem/wisort/commit/99ef9f78c3bdbecc2cd975a069d856321d33426f))

### Features

- Adding basic functionality
  ([`4117c19`](https://github.com/vividsystem/wisort/commit/4117c19ef7191cdf566ced9fe0f0dc57eb60b3e6))
