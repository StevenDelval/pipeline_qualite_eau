# CHANGELOG

<!-- version list -->

## v1.3.0-beta.7 (2025-11-05)

### Bug Fixes

- Correct DataLake handler for UTF-8 messages with accents
  ([`23e83de`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/23e83de1307f225fca4c3f15c0da58c781657f6e))

### Refactoring

- Create a script folder for reuse function
  ([`49b19f2`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/49b19f27359483b1d827989c465d0cd16fd51c80))

- Use env vars
  ([`c42f79a`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/c42f79aa1c904dfe8003b645bfa23102669b98b8))

- Use scripts file for functions
  ([`4e5600d`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/4e5600d10c3f9378c053c13daafe4eed5b5c89b4))


## v1.3.0-beta.6 (2025-11-04)

### Bug Fixes

- Correct path
  ([`3aee473`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/3aee473393d69b98cbf0768f3789cfee913367b5))


## v1.3.0-beta.5 (2025-11-04)


## v1.3.0-beta.4 (2025-11-04)

### Features

- Create job on databricks
  ([`c0c1d98`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/c0c1d98bfab041ddb29d09cf55b9720870858656))

- Make a storage account for tfstate
  ([`dfa43be`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/dfa43bebdc8e7ed093c0b2da19b76c2f30e9e918))

- Migrate backend
  ([`9ac9d52`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/9ac9d52007c80472473cc44c0d78f305bbab3cf1))


## v1.3.0-beta.3 (2025-11-04)

### Chores

- Update gitignore
  ([`3eab25d`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/3eab25d1aa1bafcb560c0bf5101a736b161b8404))

### Features

- Upload geoJSON
  ([`d6b9aaf`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/d6b9aafa1793e197276729c25226bb8ce4320b5b))


## v1.3.0-beta.2 (2025-11-04)

### Bug Fixes

- Adls_folder_exists correction of the ADLS file existence check
  ([`f6911f2`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/f6911f25da3c4959103e656f1106e9979a065502))

### Documentation

- Change docsting
  ([`3754132`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/3754132e2d2f07778fcda7edb8cfe92fb4bd82a1))


## v1.3.0-beta.1 (2025-11-04)

### Features

- Create logs filessystem
  ([`c54ee12`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/c54ee1293849ca1a3c000f8260f5e39c18be05de))

- Download only if not exist or is last year
  ([`fe851c4`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/fe851c471b00233a693e811820292e3c92ba6dc0))

### Refactoring

- Change logging config to store in datalake
  ([`7e177dc`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/7e177dc8f80f5be5b0d4ceab592e7fc4adce7ba6))


## v1.2.0 (2025-10-31)


## v1.2.0-beta.2 (2025-10-31)

### Features

- Add transformations
  ([`6139972`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/6139972bb3770201809479551dfb5889a3b586a0))


## v1.2.0-beta.1 (2025-10-31)

### Features

- Sstore data in bronze data tables(databricks) and a Parquet-formatted storage copy in the lake
  ([`ccbcbe9`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/ccbcbe968f1438af3a208b66a033ebf4c2ece86e))


## v1.1.0 (2025-10-31)


## v1.1.0-beta.2 (2025-10-31)

### Features

- Ingest data in datalake
  ([`b94f360`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/b94f36039c37d8fdb0e56a99a7602e056c81aa7f))


## v1.1.0-beta.1 (2025-10-31)

### Features

- Add gitignore
  ([`e4c4d74`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/e4c4d74c89241d4609bfcd25a1387cf0514f0ca7))

- Create ressouce group and datalake
  ([`325bfc6`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/325bfc65996c8fa7d0201e8c1c6a6c7db1dfe648))

- Databricks ressource to deploye
  ([`0bd317d`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/0bd317d5ef96778fde4fd79c9d86cbf6bd7205e7))

- Notebooks folder
  ([`ef97fb5`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/ef97fb5905e48f94abbd40ba16fc00ea13ef27bb))

- Terraform's providers to use
  ([`641445d`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/641445d573c35a948444df19fb28107be67aa066))

- Variable use with terraform
  ([`01eb330`](https://github.com/StevenDelval/pipeline_qualite_eau/commit/01eb330fe00ee86b52eeda8a1e3c6476a1250239))


## v1.0.0 (2025-10-31)

- Initial Release
